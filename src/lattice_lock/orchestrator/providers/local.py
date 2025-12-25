"""
Local Model Provider (Ollama/vLLM)
"""
import json
import logging
import os

import aiohttp

from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class LocalModelClient(BaseAPIClient):
    """Local model client (Ollama/vLLM compatible)"""

    def __init__(self, base_url: str | None = None):
        base_url = base_url or os.getenv("CUSTOM_API_URL", "http://localhost:11434/v1")
        # No API key needed for local models
        super().__init__("", base_url)

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
        """Send chat completion request to local model"""

        headers = {"Content-Type": "application/json"}

        payload = {"model": model, "messages": messages, "temperature": temperature, **kwargs}

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

        try:
            data, latency_ms = await self._make_request(
                "POST", "chat/completions", headers, payload
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
                raise e  # Re-raise if functions were provided, as fallback doesn't support them

            try:
                ollama_payload = {
                    "model": model,
                    "prompt": messages[-1]["content"],
                    "temperature": temperature,
                }

                async with self.session.post(
                    f"{self.base_url}/api/generate", json=ollama_payload
                ) as response:
                    data = await response.json()

                return APIResponse(
                    content=data["response"],
                    model=model,
                    provider="local",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    latency_ms=0,
                    raw_response=data,
                )
            except (aiohttp.ClientError, KeyError, json.JSONDecodeError):
                # Ollama fallback failed, re-raise original exception
                raise e
