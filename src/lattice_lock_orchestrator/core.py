import logging
import asyncio
import json
from typing import Optional, Dict, List, Any, Callable
from .types import TaskType, TaskRequirements, APIResponse, ModelCapabilities, FunctionCall
from .registry import ModelRegistry
from .scorer import TaskAnalyzer, ModelScorer
from .guide import ModelGuideParser
from .api_clients import (
    get_api_client,
    ProviderAvailability,
    ProviderStatus,
    ProviderUnavailableError,
)
from .function_calling import FunctionCallHandler

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    """
    Intelligent model orchestration system.
    Routes requests to the best model based on task requirements, cost, and performance.
    """

    def __init__(self, guide_path: Optional[str] = None):
        self.registry = ModelRegistry()
        self.analyzer = TaskAnalyzer()
        self.scorer = ModelScorer()
        self.guide = ModelGuideParser(guide_path)
        self.clients = {}
        self.function_call_handler = FunctionCallHandler()

    def register_function(self, name: str, func: Callable):
        """Registers a function with the internal FunctionCallHandler."""
        self.function_call_handler.register_function(name, func)

    async def route_request(self,
                          prompt: str,
                          model_id: Optional[str] = None,
                          task_type: Optional[TaskType] = None,
                          **kwargs) -> APIResponse:
        """
        Route a request to the appropriate model.

        Args:
            prompt: The user prompt.
            model_id: Optional specific model ID to force use.
            task_type: Optional manual task type override.
            **kwargs: Additional arguments passed to the API client.
        """

        # 1. Analyze Task
        requirements = self.analyzer.analyze(prompt)
        if task_type:
            requirements.task_type = task_type

        logger.info(f"Analyzed task: {requirements.task_type.name}, Priority: {requirements.priority}")

        # 2. Select Model
        selected_model_id = model_id
        if not selected_model_id:
            selected_model_id = self._select_best_model(requirements)

        if not selected_model_id:
            raise ValueError("No suitable model found for request")

        model_cap = self.registry.get_model(selected_model_id)
        if not model_cap:
             raise ValueError(f"Model {selected_model_id} not found in registry")

        logger.info(f"Selected model: {selected_model_id} ({model_cap.provider.value})")

        # 3. Execute Request
        try:
            return await self._call_model(model_cap, prompt, **kwargs)
        except Exception as e:
            logger.error(f"Primary model failed: {e}. Attempting fallback...")
            return await self._handle_fallback(requirements, prompt, failed_model=selected_model_id, **kwargs)

    def _select_best_model(self, requirements: TaskRequirements) -> Optional[str]:
        """Select the best model based on requirements and guide"""

        # 1. Check Guide Recommendations first
        guide_recs = self.guide.get_recommended_models(requirements.task_type.name)
        if guide_recs:
            # Validate recommendations exist in registry and meet hard constraints
            valid_recs = []
            for mid in guide_recs:
                model = self.registry.get_model(mid)
                if model and self.scorer.score(model, requirements) > 0:
                    valid_recs.append(mid)

            if valid_recs:
                return valid_recs[0] # Return top recommendation

        # 2. Score all models
        candidates = []
        for model in self.registry.get_all_models():
            if self.guide.is_model_blocked(model.api_name):
                continue

            score = self.scorer.score(model, requirements)
            if score > 0:
                candidates.append((model.api_name, score))

        if not candidates:
            return None

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    async def _call_model(self, model: ModelCapabilities, prompt: str, **kwargs) -> APIResponse:
        """Call the specific model API"""
        client = self._get_client(model.provider.value)

        messages = [{"role": "user", "content": prompt}]
        if "messages" in kwargs:
            messages = kwargs.pop("messages")

        # Get registered functions for the model to use
        functions_metadata = self.function_call_handler.get_registered_functions_metadata()

        # Initial call to the model
        first_response = await client.chat_completion(
            model=model.api_name,
            messages=messages,
            functions=list(functions_metadata.values()), # Pass functions metadata
            **kwargs
        )

        # Check for function call in the first response
        if first_response.function_call:
            function_call_name = first_response.function_call.name
            function_call_args = first_response.function_call.arguments

            logger.info(f"Model requested function call: {function_call_name} with args {function_call_args}")

            try:
                function_result = await self.function_call_handler.execute_function_call(
                    function_call_name,
                    **function_call_args
                )
                first_response.function_call_result = function_result
                logger.info(f"Function call {function_call_name} executed successfully. Result: {function_result}")

                # Extract the tool_call_id from the first response's raw data
                tool_call_id = None
                if first_response.raw_response and \
                   'choices' in first_response.raw_response and \
                   first_response.raw_response['choices'] and \
                   'message' in first_response.raw_response['choices'][0] and \
                   'tool_calls' in first_response.raw_response['choices'][0]['message'] and \
                   first_response.raw_response['choices'][0]['message']['tool_calls']:
                    tool_call_id = first_response.raw_response['choices'][0]['message']['tool_calls'][0]['id']

                if not tool_call_id:
                    logger.warning("Could not extract tool_call_id from model's first response.")
                    # Fallback to a dummy ID if it cannot be extracted (though this might cause issues with some APIs)
                    tool_call_id = "call_dummy_id_fallback"

                # Append the assistant's function call message
                messages.append({
                    "role": "assistant",
                    "content": None, # Function call doesn't have content directly
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": function_call_name,
                            "arguments": json.dumps(function_call_args)
                        }
                    }]
                })

                # Append the tool's response message
                messages.append({
                    "role": "tool",
                    "content": str(function_result),
                    "tool_call_id": tool_call_id # Must match the ID from the assistant's tool_calls
                })

                # Make a second call to the model with the tool's response
                final_response = await client.chat_completion(
                    model=model.api_name,
                    messages=messages,
                    functions=list(functions_metadata.values()), # Pass functions metadata again
                    **kwargs
                )

                # Update the final response with the function call details and result from the first turn
                final_response.function_call = first_response.function_call
                final_response.function_call_result = first_response.function_call_result

                return final_response

            except Exception as e:
                first_response.error = f"Function call failed: {e}"
                logger.error(f"Function call {function_call_name} failed: {e}")

        return first_response

    async def _handle_fallback(self, requirements: TaskRequirements, prompt: str, failed_model: str, **kwargs) -> APIResponse:
        """
        Handle fallback logic when primary model fails.

        This method:
        1. Gets fallback chain from guide or builds one from registry
        2. Filters out unavailable providers (missing credentials)
        3. Attempts each fallback model in order
        4. Provides clear error messages when all fallbacks fail

        Args:
            requirements: The task requirements for model selection
            prompt: The user prompt
            failed_model: The model that failed (to skip in fallback)
            **kwargs: Additional arguments for the API call

        Returns:
            APIResponse from the first successful fallback model

        Raises:
            RuntimeError: If all fallback models fail or no providers available
        """
        # Get fallback chain from guide
        chain = self.guide.get_fallback_chain(requirements.task_type.name)

        # If no chain, or failed model was last in chain, try to find next best scorer
        if not chain:
            # Simple fallback: try next best model from registry
            candidates = []
            for model in self.registry.get_all_models():
                if model.api_name == failed_model:
                    continue

                # Skip models from unavailable providers
                provider_name = model.provider.value
                if not self._is_provider_available(provider_name):
                    logger.debug(f"Skipping model {model.api_name}: provider '{provider_name}' unavailable")
                    continue

                score = self.scorer.score(model, requirements)
                if score > 0:
                    candidates.append((model.api_name, score, provider_name))

            candidates.sort(key=lambda x: x[1], reverse=True)
            chain = [c[0] for c in candidates[:5]]  # Try top 5 available models

        if not chain:
            available = self.get_available_providers()
            raise RuntimeError(
                f"No fallback models available. "
                f"Available providers: {available if available else 'None'}. "
                f"Please configure credentials for at least one provider."
            )

        failed_attempts = []
        for model_id in chain:
            if model_id == failed_model:
                continue

            model_cap = self.registry.get_model(model_id)
            if not model_cap:
                logger.debug(f"Skipping fallback model {model_id}: not found in registry")
                continue

            # Check provider availability before attempting
            provider_name = model_cap.provider.value
            if not self._is_provider_available(provider_name):
                logger.info(f"Skipping fallback model {model_id}: provider '{provider_name}' unavailable")
                continue

            logger.info(f"Attempting fallback to: {model_id} ({provider_name})")

            try:
                response = await self._call_model(model_cap, prompt, **kwargs)
                # Check if the response indicates an error (e.g., from experimental providers)
                if response.error:
                    logger.warning(f"Fallback model {model_id} returned error: {response.error}")
                    failed_attempts.append((model_id, response.error))
                    continue
                return response
            except ProviderUnavailableError as e:
                logger.warning(f"Fallback model {model_id} provider unavailable: {e.message}")
                failed_attempts.append((model_id, e.message))
                continue
            except Exception as e:
                logger.warning(f"Fallback model {model_id} failed: {e}")
                failed_attempts.append((model_id, str(e)))
                continue

        # Build detailed error message
        error_details = "; ".join([f"{m}: {e}" for m, e in failed_attempts]) if failed_attempts else "No models attempted"
        available = self.get_available_providers()
        raise RuntimeError(
            f"All fallback models failed. "
            f"Attempted: {error_details}. "
            f"Available providers: {available if available else 'None'}. "
            f"Check your API credentials and provider configuration."
        )

    def _get_client(self, provider: str):
        """
        Get or create API client for the specified provider.

        Args:
            provider: The provider name (e.g., 'openai', 'anthropic')

        Returns:
            The API client instance.

        Raises:
            ProviderUnavailableError: If provider credentials are missing.
        """
        if provider not in self.clients:
            try:
                self.clients[provider] = get_api_client(provider, check_availability=True)
            except ProviderUnavailableError as e:
                logger.error(f"Cannot create client for provider '{provider}': {e.message}")
                raise
        return self.clients[provider]

    def _is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available (has credentials configured)."""
        return ProviderAvailability.is_available(provider)

    def get_available_providers(self) -> List[str]:
        """Get list of providers that have credentials configured."""
        return ProviderAvailability.get_available_providers()

    def check_provider_status(self) -> Dict[str, str]:
        """
        Check and return the status of all providers.

        Returns:
            Dict mapping provider names to their status messages.
        """
        ProviderAvailability.check_all_providers()
        result = {}
        for provider in ProviderAvailability.REQUIRED_CREDENTIALS.keys():
            status = ProviderAvailability.get_status(provider)
            message = ProviderAvailability.get_message(provider)
            result[provider] = f"{status.value}: {message}"
        return result
