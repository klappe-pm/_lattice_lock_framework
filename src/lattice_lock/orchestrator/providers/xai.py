"""
xAI (Grok) API Provider
"""
import json
import logging
import os
from collections.abc import AsyncIterator

from lattice_lock.orchestrator.types import APIResponse, FunctionCall

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class GrokAPIClient(BaseAPIClient):
    """xAI Grok API client with all models support"""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("XAI_API_KEY not found")
        super().__init__(api_key, "https://api.x.ai/v1")

    async def _chat_completion_impl(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> APIResponse:
        """Send chat completion request to Grok"""

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": model,
            "messages": messages,
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
            return self._stream_completion(headers, payload)

        # Uses the refactored _make_request which handles exceptions
        data, latency_ms = await self._make_request("POST", "chat/completions", headers, payload)

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

    async def _stream_completion(self, headers: dict, payload: dict) -> AsyncIterator[str]:
        """Stream completion responses"""
        payload["stream"] = True

        async with self.session.post(
            f"{self.base_url}/chat/completions", headers=headers, json=payload
        ) as response:
            async for line in response.content:
                if line:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
