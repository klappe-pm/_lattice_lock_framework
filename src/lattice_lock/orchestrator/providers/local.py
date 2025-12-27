"""
Local Model Provider (Ollama/vLLM)
"""
import json
import logging
import os
from typing import Any

import aiohttp
from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class LocalModelClient(BaseAPIClient):
    """Local model client (Ollama/vLLM compatible)"""

    def __init__(self, config: AppConfig, base_url: str | None = None, **kwargs):
        self.base_url = base_url or os.getenv("CUSTOM_API_URL", "http://localhost:11434/v1")
        super().__init__(config)

    def _validate_config(self) -> None:
        # Local models don't strictly require config validation other than URL presence
        pass

    async def health_check(self) -> bool:
        """Verify local model connectivity."""
        try:
            # Check models endpoint
            await self._make_request("GET", f"{self.base_url}/models")
            return True
        except Exception as e:
            # Try Ollama specific endpoint if generic v1 fails
            try:
                # Need a bare request for this, _make_request prepends nothing but expects full URL in 2nd arg
                # Wait, _make_request takes full url?
                # In base.py I implemented: async with session.request(method, url, ...)
                # So yes.
                # Ollama tags
                await self._make_request("GET", f"{self.base_url.replace('/v1', '')}/api/tags")
                return True
            except Exception:
                 raise ProviderUnavailableError("local", f"Could not connect to {self.base_url}: {e}")

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
        """Send chat completion request"""
        header = {"Content-Type": "application/json"}
        
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

        try:
            data, latency_ms = await self._make_request(
                "POST", f"{self.base_url}/chat/completions", header, payload
            )
            
            # ... process response (same as before) ...
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
                provider="local",
                usage={
                    "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "output_tokens": data.get("usage", {}).get("completion_tokens", 0),
                },
                latency_ms=latency_ms,
                raw_response=data,
                function_call=function_call,
            )

        except Exception as e:
            # Fallback for Ollama format IF no functions are being used
            if functions:
                raise e

            try:
                ollama_payload = {
                    "model": model,
                    "prompt": clean_messages[-1]["content"],
                    "temperature": temperature,
                    "stream": False 
                }
                
                # Use raw base url without /v1
                base = self.base_url.replace("/v1", "")
                data, latency = await self._make_request(
                    "POST", f"{base}/api/generate", {}, ollama_payload
                )

                return APIResponse(
                    content=data.get("response", ""),
                    model=model,
                    provider="local",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    latency_ms=latency,
                    raw_response=data,
                )
            except Exception:
                raise e