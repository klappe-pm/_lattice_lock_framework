import logging
import uuid
from collections.abc import Callable

from lattice_lock.tracing import AsyncSpanContext, generate_trace_id, get_current_trace_id

from .exceptions import APIClientError
from .providers import ProviderUnavailableError
from .cost.tracker import CostTracker
from .execution import ClientPool, ConversationExecutor
from .analysis import TaskAnalyzer
from .function_calling import FunctionCallHandler
from .guide import ModelGuideParser
from .registry import ModelRegistry
from .scoring import ModelScorer
from .selection import ModelSelector
from .types import APIResponse, TaskRequirements, TaskType

logger = logging.getLogger(__name__)


class ModelOrchestrator:
    """
    Intelligent model orchestration system.
    Routes requests to the best model using modular components for selection and execution.
    """

    def __init__(self, guide_path: str | None = None):
        # 1. Initialize Registry and Config
        self.registry = ModelRegistry()
        self.guide = ModelGuideParser(guide_path)
        
        # 2. Initialize Support Components
        self.scorer = ModelScorer()  # Used by selector
        self.analyzer = TaskAnalyzer()
        self.cost_tracker = CostTracker(self.registry)
        self.function_call_handler = FunctionCallHandler()
        
        # 3. Initialize Core Modules
        self.selector = ModelSelector(self.registry, self.scorer, self.guide)
        self.client_pool = ClientPool()
        self.executor = ConversationExecutor(
            self.function_call_handler, 
            self.cost_tracker
        )

        self._initialize_analyzer_client()

    def _initialize_analyzer_client(self):
        """Try to initialize TaskAnalyzer with a default client for semantic routing."""
        try:
            # We use a fast, cheap model if available
            # ClientPool lazily loads, so we just get one
            client = self.client_pool.get_client("openai")  # Fallback logic for router
            if client:
                self.analyzer = TaskAnalyzer(router_client=client)
        except Exception:
            logger.debug("Could not initialize Semantic Router client. Fallback to heuristics only.")

    def register_function(self, name: str, func: Callable):
        """Registers a function with the internal FunctionCallHandler."""
        self.function_call_handler.register_function(name, func)

    async def route_request(
        self,
        prompt: str,
        model_id: str | None = None,
        task_type: TaskType | None = None,
        trace_id: str | None = None,
        **kwargs,
    ) -> APIResponse:
        """
        Route a request to the appropriate model.

        Args:
            prompt: The user prompt.
            model_id: Optional specific model ID to force use.
            task_type: Optional manual task type override.
            trace_id: Optional trace ID for distributed tracing.
            **kwargs: Additional arguments passed to the API client.
        """
        # Generate or use provided trace ID for request correlation
        request_trace_id = trace_id or get_current_trace_id() or generate_trace_id()

        async with AsyncSpanContext(
            "route_request",
            trace_id=request_trace_id,
            attributes={"model_id": model_id, "task_type": str(task_type)},
        ):
            # 1. Analyze Task
            requirements = await self.analyzer.analyze_async(prompt)
            if task_type:
                requirements.task_type = task_type

            logger.info(
                f"Analyzed task: {requirements.task_type.name}, Priority: {requirements.priority}",
                extra={"trace_id": request_trace_id},
            )

            # 2. Select Model
            selected_model_id = model_id
            if not selected_model_id:
                selected_model_id = self.selector.select_best_model(requirements)

            if not selected_model_id:
                raise ValueError("No suitable model found for request")

            model_cap = self.registry.get_model(selected_model_id)
            if not model_cap:
                raise ValueError(f"Model {selected_model_id} not found in registry")

            logger.info(
                f"Selected model: {selected_model_id} ({model_cap.provider.value})",
                extra={"trace_id": request_trace_id},
            )

            # 3. Execute Request
            try:
                # Get client from pool
                client = self.client_pool.get_client(model_cap.provider.value)
                
                # Execute conversation (single turn logic wrapped in conversation executor for now)
                # But route_request is often single turn. ConversationExecutor handles tool loops.
                messages = kwargs.pop("messages", [{"role": "user", "content": prompt}])
                
                return await self.executor.execute(
                    model_cap=model_cap,
                    client=client,
                    messages=messages,
                    trace_id=request_trace_id,
                    task_type=requirements.task_type.name, # Pass task type for tracking
                    **kwargs
                )
                
            except (ValueError, APIClientError, ProviderUnavailableError) as e:
                logger.warning(
                    f"Primary model {selected_model_id} failed: {e}. Attempting fallback...",
                    extra={"trace_id": request_trace_id},
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error with primary model {selected_model_id}: {e}. Attempting fallback...",
                    extra={"trace_id": request_trace_id},
                    exc_info=True,
                )

            # 4. Handle Fallback
            return await self._handle_fallback(
                requirements,
                prompt,
                failed_model=selected_model_id,
                trace_id=request_trace_id,
                **kwargs,
            )

    async def _handle_fallback(
        self,
        requirements: TaskRequirements,
        prompt: str,
        failed_model: str,
        trace_id: str | None = None,
        **kwargs,
    ) -> APIResponse:
        """
        Handle fallback logic when primary model fails.
        Identical logic to original but delegated to ModelSelector for chain 
        and ClientPool/Executor for execution.
        """
        request_trace_id = trace_id or get_current_trace_id() or "unknown"
        
        # Get fallback chain
        chain = self.selector.get_fallback_chain(requirements, failed_model)

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

            # ModelSelector already checks provider availability for dynamically generated chains,
            # but guide-based chains might include unavailable ones.
            # ClientPool.get_client will raise if unavailable, so we catch it.

            logger.info(
                f"Attempting fallback to: {model_id} ({model_cap.provider.value})",
                extra={"trace_id": request_trace_id},
            )

            try:
                client = self.client_pool.get_client(model_cap.provider.value)
                messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

                response = await self.executor.execute(
                    model_cap=model_cap,
                    client=client,
                    messages=messages,
                    trace_id=request_trace_id, 
                    task_type=requirements.task_type.name,
                    **kwargs
                )

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
        error_details = (
            "; ".join([f"{m}: {e}" for m, e in failed_attempts])
            if failed_attempts
            else "No models attempted"
        )
        available = self.get_available_providers()
        raise RuntimeError(
            f"All fallback models failed. "
            f"Attempted: {error_details}. "
            f"Available providers: {available if available else 'None'}. "
            f"Check your API credentials and provider configuration."
        )

    def get_available_providers(self) -> list[str]:
        """Get list of providers that have credentials configured."""
        from .providers import ProviderAvailability
        return ProviderAvailability.get_available_providers()

    def check_provider_status(self) -> dict[str, str]:
        """Check and return status of all providers."""
        from .providers import ProviderAvailability
        status = ProviderAvailability.check_all_providers()
        return {provider: s.value for provider, s in status.items()}

    def _is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available."""
        from .providers import ProviderAvailability
        return ProviderAvailability.is_available(provider)

    def close(self):
        """Shutdown orchestrator resources."""
        # There is no async close method pattern in standard python __del__, usually explicit.
        # But this method is sync. ClientPool has async close_all.
        # Users should call shutdown explicitly if we want async support.
        pass

    async def shutdown(self):
        """Async shutdown."""
        await self.client_pool.close_all()

