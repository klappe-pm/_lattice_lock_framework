"""
OpenAI API Provider
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


class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API client"""

    PROVIDER_NAME = "openai"
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, config: AppConfig, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate OpenAI API key is present."""
        if not self.api_key:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME, reason="OPENAI_API_KEY environment variable not set"
            )

    async def health_check(self) -> bool:
        """Verify OpenAI API connectivity."""
        try:
            # Minimal API call to verify credentials
            headers = {"Authorization": f"Bearer {self.api_key}"}
            await self._make_request("GET", f"{self.BASE_URL}/models", headers=headers)
            logger.debug("OpenAI health check passed")
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            raise ProviderUnavailableError(provider=self.PROVIDER_NAME, reason=str(e))

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
        """Send chat completion request to OpenAI"""

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        # Convert messages to dict if they aren't already (though types says they are)
        # Ensure we pass strings for content
        clean_messages = []
        for msg in messages:
            clean_messages.append({"role": msg["role"], "content": str(msg["content"])})

        payload = {"model": model, "messages": clean_messages, "temperature": temperature, **kwargs}

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

        data, latency_ms = await self._make_request(
            "POST", f"{self.BASE_URL}/chat/completions", headers, payload
        )

        response_content = None
        function_call = None

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
            provider="openai",
            usage={
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )
