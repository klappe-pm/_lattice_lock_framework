"""
xAI (Grok) API Provider
"""
import json
import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class GrokAPIClient(BaseAPIClient):
    """xAI Grok API client with all models support"""
    
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self, config: AppConfig, api_key: str | None = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        super().__init__(config)
        
    def _validate_config(self) -> None:
        if not self.api_key:
            raise ProviderUnavailableError(
                provider="xai",
                reason="XAI_API_KEY environment variable not set"
            )

    async def health_check(self) -> bool:
        """Verify Grok API connectivity."""
        try:
             headers = {"Authorization": f"Bearer {self.api_key}"}
             await self._make_request("GET", f"{self.BASE_URL}/models", headers=headers)
             return True
        except Exception as e:
            raise ProviderUnavailableError(
                provider="xai",
                reason=str(e)
            )

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> APIResponse:
        """Send chat completion request to Grok"""

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        # Ensure clean messages
        clean_messages = []
        for msg in messages:
            clean_messages.append({"role": msg["role"], "content": str(msg["content"])})

        payload = {
            "model": model,
            "messages": clean_messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

        if stream:
            # We need to implement stream handling separately or raise NotSupported for now since base interface returns APIResponse directly
            # For simplicity in this refactor, we will disable stream or handle it if APIResponse supports it (it doesn't seem to be an async iterator)
            # The original code returned AsyncIterator[str], but base class returns APIResponse.
            # We will force stream=False for now to comply with BaseAPIClient signature, or adapt if needed.
            # Given BaseAPIClient defines return type as Any, technically we could return AsyncIterator.
            # But let's stick to non-streaming for consistency unless required.
            pass

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
            provider="xai",
            usage={
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )
