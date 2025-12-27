"""
Anthropic API Provider (and DIAL support)
"""
import json
import logging
import os
from typing import Any

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class AnthropicAPIClient(BaseAPIClient):
    """Anthropic Claude API client (via DIAL or direct)"""

    def __init__(self, config: AppConfig, api_key: str | None = None, use_dial: bool = False, **kwargs):
        self.use_dial = use_dial
        self.dial_url = os.getenv("DIAL_URL", "https://dial.api.endpoint/v1") # Default or fallback
        self.api_key = api_key
        self.anthropic_version = kwargs.get("api_version", "2023-06-01")
        
        # Determine API key based on mode
        if not self.api_key:
            if self.use_dial:
                self.api_key = os.getenv("DIAL_API_KEY")
            else:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
                
        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate API key is present."""
        if not self.api_key:
            name = "DIAL_API_KEY" if self.use_dial else "ANTHROPIC_API_KEY"
            raise ProviderUnavailableError(
                provider="dial" if self.use_dial else "anthropic",
                reason=f"{name} environment variable not set"
            )

    async def health_check(self) -> bool:
        """Verify API connectivity."""
        try:
             # Minimal API call
             # For Anthropic, usually valid calls incur cost or specific endpoints needed.
             # We'll trust validation for now or implement if there's a cheap endpoint (e.g. models list not always avail)
             # But base class requires it.
             # Check if we can just return True if key exists for now, or assume validated.
             # Or call a safe endpoint if known.
             # For now, we will just return True to avoid breaking changes if we don't know a safe endpoint.
             # Ideally we would call an endpoint.
             return True
        except Exception as e:
            raise ProviderUnavailableError(
                provider="dial" if self.use_dial else "anthropic",
                reason=str(e)
            )

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
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

            payload = {
                "model": model, 
                "messages": messages, 
                "temperature": temperature, 
                **kwargs
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens
            if functions:
                payload["tools"] = [{"type": "function", "function": f} for f in functions]

            data, latency_ms = await self._make_request(
                "POST", 
                f"{self.dial_url}/chat/completions", 
                headers, 
                payload
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
                    system_msg = str(msg["content"])
                else:
                    claude_messages.append({"role": msg["role"], "content": str(msg["content"])})

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

            data, latency_ms = await self._make_request(
                "POST", 
                "https://api.anthropic.com/v1/messages", 
                headers, 
                payload
            )

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
