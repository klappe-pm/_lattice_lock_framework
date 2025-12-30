import json
import logging
from typing import Any

from lattice_lock.orchestrator.cost.tracker import CostTracker
from lattice_lock.orchestrator.function_calling import FunctionCallHandler
from lattice_lock.orchestrator.providers.base import BaseAPIClient
from lattice_lock.orchestrator.types import APIResponse, ModelCapabilities, TokenUsage
from lattice_lock.tracing import get_current_trace_id

logger = logging.getLogger(__name__)


class ConversationExecutor:
    """
    Executes the conversation loop, handling tool calls and aggregating token usage.
    """

    def __init__(
        self,
        function_call_handler: FunctionCallHandler,
        cost_tracker: CostTracker,
        max_turns: int = 5,
    ):
        self.function_call_handler = function_call_handler
        self.cost_tracker = cost_tracker
        self.max_turns = max_turns

    async def execute(
        self,
        model_cap: ModelCapabilities,
        client: BaseAPIClient,
        messages: list[dict[str, Any]],
        trace_id: str | None = None,
        **kwargs,
    ) -> APIResponse:
        """
        Execute the chat completion loop.

        Args:
            model_cap: The capabilities of the selected model.
            client: The API client to use.
            messages: The conversation history.
            trace_id: Optional trace ID.
            **kwargs: Additional arguments for the API call.

        Returns:
            The final APIResponse with aggregated token usage.
        """
        request_trace_id = trace_id or get_current_trace_id() or "unknown"

        # Initialize usage aggregation
        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0, cost=0.0)

        functions_metadata = self.function_call_handler.get_registered_functions_metadata()
        functions = list(functions_metadata.values()) if functions_metadata else None

        current_messages = messages.copy()
        final_response = None

        for turn in range(self.max_turns):
            logger.debug(
                f"Turn {turn+1}/{self.max_turns} for model {model_cap.api_name}",
                extra={"trace_id": request_trace_id},
            )

            # Call the model
            response = await client.chat_completion(
                model=model_cap.api_name,
                messages=current_messages,
                functions=functions,
                **kwargs,
            )

            # Aggregate usage
            if response.usage:
                if isinstance(response.usage, dict):
                    total_usage.prompt_tokens += response.usage.get("prompt_tokens", 0)
                    total_usage.completion_tokens += response.usage.get("completion_tokens", 0)
                    total_usage.total_tokens += response.usage.get("total_tokens", 0)
                    # Cost might not be in dict for all providers
                else:
                    total_usage.prompt_tokens += response.usage.prompt_tokens
                    total_usage.completion_tokens += response.usage.completion_tokens
                    total_usage.total_tokens += response.usage.total_tokens
                    if response.usage.cost:
                        total_usage.cost = (total_usage.cost or 0.0) + response.usage.cost

            # Record individual transaction cost
            # Note: We record each step, but we return the aggregated usage on the final response object
            self.cost_tracker.record_transaction(
                response,
                task_type=kwargs.get("task_type", "general"),
                trace_id=request_trace_id,
            )

            # Check for function call
            if response.function_call:
                function_call_name = response.function_call.name
                function_call_args = response.function_call.arguments

                logger.info(
                    f"Model requested function call: {function_call_name}",
                    extra={"trace_id": request_trace_id},
                )

                try:
                    function_result = await self.function_call_handler.execute_function_call(
                        function_call_name, **function_call_args
                    )

                    # Update response with result (for potential return if it was the last turn)
                    response.function_call_result = function_result

                    # Extract tool_call_id
                    tool_call_id = self._extract_tool_call_id(response)

                    # Append assistant message with tool calls
                    current_messages.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": tool_call_id,
                                    "type": "function",
                                    "function": {
                                        "name": function_call_name,
                                        "arguments": json.dumps(function_call_args),
                                    },
                                }
                            ],
                        }
                    )

                    # Append tool result message
                    current_messages.append(
                        {
                            "role": "tool",
                            "content": str(function_result),
                            "tool_call_id": tool_call_id,
                        }
                    )

                    # Continue to next turn (automatic recursion)
                    final_response = response  # Keep track of last response
                    continue

                except Exception as e:
                    logger.error(
                        f"Function call {function_call_name} failed: {e}",
                        extra={"trace_id": request_trace_id},
                    )
                    response.error = f"Function call failed: {e}"
                    # Allow return of error response
                    final_response = response
                    break
            else:
                # No function call, this is the final response
                final_response = response
                break

        if final_response:
            # Attach aggregated usage to the final response
            final_response.usage = total_usage
            return final_response

        raise RuntimeError("Conversation loop ended without a final response.")

    def _extract_tool_call_id(self, response: APIResponse) -> str:
        """Safely extract tool_call_id from response with error handling."""
        try:
            if (
                response.raw_response
                and "choices" in response.raw_response
                and response.raw_response["choices"]
                and "message" in response.raw_response["choices"][0]
                and "tool_calls" in response.raw_response["choices"][0]["message"]
                and response.raw_response["choices"][0]["message"]["tool_calls"]
            ):
                return response.raw_response["choices"][0]["message"]["tool_calls"][0]["id"]
        except (KeyError, IndexError, TypeError) as e:
            logger.debug(f"Error extracting tool_call_id: {e}")

        logger.warning("Could not extract tool_call_id from model's response.")
        return "call_dummy_id_fallback"
