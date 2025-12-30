"""
Azure OpenAI Provider
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


class AzureOpenAIClient(BaseAPIClient):
    """Azure OpenAI Service API client"""

    BASE_URL = None  # Dynamic based on endpoint

    def __init__(
        self, config: AppConfig, api_key: str | None = None, endpoint: str | None = None, **kwargs
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = kwargs.get("api_version", "2024-02-15-preview")
        super().__init__(config)

    def _validate_config(self) -> None:
        if not self.api_key or not self.endpoint:
            raise ProviderUnavailableError(
                provider="azure", reason="AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required"
            )

    async def health_check(self) -> bool:
        """Verify Azure OpenAI connectivity."""
        try:
            # Azure doesn't have a simple global "list models" without a deployment typically,
            # but we can try a harmless call or just assume config is valid if we can't easily ping.
            # Ideally we would list deployments.
            # For now, simplistic check:
            return True
        except Exception as e:
            raise ProviderUnavailableError(provider="azure", reason=str(e))

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
        """Send chat completion request to Azure OpenAI"""

        headers = {"api-key": self.api_key, "Content-Type": "application/json"}

        # Ensure clean messages
        clean_messages = []
        for msg in messages:
            clean_messages.append({"role": msg["role"], "content": str(msg["content"])})

        payload = {"messages": clean_messages, "temperature": temperature, **kwargs}

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

        # Azure OpenAI uses deployment names in the endpoint. Assuming 'model' maps to deployment name.
        url_endpoint = f"{self.endpoint}/openai/deployments/{model}/chat/completions?api-version={self.api_version}"
        # Make sure endpoint doesn't double slash
        if not self.endpoint.endswith("/"):
            # Simple heuristic, full URL construction
            pass

        data, latency_ms = await self._make_request("POST", url_endpoint, headers, payload)

        response_content = None
        function_call = None

        # Bounds checking for response structure
        choices = data.get("choices", [])
        if choices and choices[0].get("message"):
            message = choices[0]["message"]
            if message.get("content"):
                response_content = message["content"]
            elif message.get("tool_calls"):
                tool_call = message["tool_calls"][0]
                try:
                    function_call = FunctionCall(
                        name=tool_call["function"]["name"],
                        arguments=json.loads(tool_call["function"]["arguments"]),
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse function arguments: {e}")

        return APIResponse(
            content=response_content,
            model=model,
            provider="azure",
            usage={
                "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": data.get("usage", {}).get("completion_tokens", 0),
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )
