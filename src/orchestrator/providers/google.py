"""
Google Gemini API Provider
"""

import logging
import os
from typing import Any

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class GoogleAPIClient(BaseAPIClient):
    """Google Gemini API client"""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: AppConfig, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        super().__init__(config)

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ProviderUnavailableError(
                provider="google", reason="GOOGLE_API_KEY environment variable not set"
            )

    async def health_check(self) -> bool:
        """Verify Gemini API connectivity."""
        try:
            # Minimal API call to verify credentials
            # Calling models.list equivalent
            endpoint = f"models?key={self.api_key}"
            await self._make_request("GET", f"{self.BASE_URL}/{endpoint}")
            return True
        except Exception as e:
            raise ProviderUnavailableError(provider="google", reason=str(e))

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
        """Send chat completion request to Google Gemini"""

        headers = {
            "Content-Type": "application/json",
        }

        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            contents.append(
                {
                    "parts": [{"text": str(msg["content"])}],
                    "role": "user" if msg["role"] == "user" else "model",
                }
            )

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "candidateCount": 1,
            },
        }

        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        if functions:
            payload["tools"] = [{"functionDeclarations": functions}]

        endpoint = f"models/{model}:generateContent?key={self.api_key}"
        data, latency_ms = await self._make_request(
            "POST", f"{self.BASE_URL}/{endpoint}", headers, payload
        )

        response_content = None
        function_call = None

        if data.get("candidates") and data["candidates"][0]["content"].get("parts"):
            for part in data["candidates"][0]["content"]["parts"]:
                if part.get("text"):
                    response_content = part["text"]
                elif part.get("functionCall"):
                    function_call = FunctionCall(
                        name=part["functionCall"]["name"], arguments=part["functionCall"]["args"]
                    )

        # safely handle usage metadata if missing
        usage_meta = data.get("usageMetadata", {})

        return APIResponse(
            content=response_content,
            model=model,
            provider="google",
            usage={
                "input_tokens": usage_meta.get("promptTokenCount", 0),
                "output_tokens": usage_meta.get("candidatesTokenCount", 0),
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )
