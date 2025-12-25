"""
Anthropic API Provider (and DIAL support)
"""
import json
import logging
import os

from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class AnthropicAPIClient(BaseAPIClient):
    """Anthropic Claude API client (via DIAL or direct)"""

    def __init__(self, api_key: str | None = None, use_dial: bool = False, **kwargs):
        if use_dial:
            api_key = api_key or os.getenv("DIAL_API_KEY")
            if not api_key:
                raise ValueError("DIAL_API_KEY not found")
            # Assuming DIAL endpoint - adjust as needed
            super().__init__(api_key, "https://dial.api.endpoint/v1")
        else:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            super().__init__(api_key, "https://api.anthropic.com/v1")

        self.use_dial = use_dial
        self.anthropic_version = kwargs.get("api_version", "2023-06-01")

    async def _chat_completion_impl(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> APIResponse:
        """Send chat completion request to Anthropic/DIAL"""

        response_content = None
        function_call = None

        if self.use_dial:
            # DIAL format (OpenAI-compatible)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {"model": model, "messages": messages, "temperature": temperature, **kwargs}

            if max_tokens:
                payload["max_tokens"] = max_tokens
            if functions:
                payload["tools"] = [{"type": "function", "function": f} for f in functions]

            data, latency_ms = await self._make_request(
                "POST", "chat/completions", headers, payload
            )

            if data["choices"][0]["message"].get("content"):
                response_content = data["choices"][0]["message"]["content"]
            elif data["choices"][0]["message"].get("tool_calls"):
                tool_call = data["choices"][0]["message"]["tool_calls"][0]
                function_call = FunctionCall(
                    name=tool_call["function"]["name"],
                    arguments=json.loads(tool_call["function"]["arguments"]),
                )

            return APIResponse(
                content=response_content,
                model=model,
                provider="dial",
                usage={
                    "input_tokens": data["usage"]["prompt_tokens"],
                    "output_tokens": data["usage"]["completion_tokens"],
                },
                latency_ms=latency_ms,
                raw_response=data,
                function_call=function_call,
            )
        else:
            # Direct Anthropic API
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.anthropic_version,
                "Content-Type": "application/json",
            }

            # Convert to Anthropic format
            system_msg = None
            claude_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    claude_messages.append({"role": msg["role"], "content": msg["content"]})

            payload = {
                "model": model,
                "messages": claude_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs,
            }

            if system_msg:
                payload["system"] = system_msg
            if functions:
                payload["tools"] = functions

            data, latency_ms = await self._make_request("POST", "messages", headers, payload)

            if data["content"][0].get("text"):
                response_content = data["content"][0]["text"]
            elif data["content"][0].get("type") == "tool_use":
                tool_use = data["content"][0]
                function_call = FunctionCall(name=tool_use["name"], arguments=tool_use["input"])

            return APIResponse(
                content=response_content,
                model=model,
                provider="anthropic",
                usage={
                    "input_tokens": data["usage"]["input_tokens"],
                    "output_tokens": data["usage"]["output_tokens"],
                },
                latency_ms=latency_ms,
                raw_response=data,
                function_call=function_call,
            )
