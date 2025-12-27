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
        """
        Send a chat completion request to a local model and return a normalized APIResponse.
        
        Parameters:
            model (str): Model identifier to use.
            messages (list[dict[str, str]]): Conversation messages as a list of dicts; each message should include at least a "content" key (and typically a "role" key).
            temperature (float): Sampling temperature for the model.
            max_tokens (int | None): Maximum number of tokens to generate, or None to use the model default.
            functions (list[dict] | None): Optional list of function descriptors; when provided they are sent as tools in the request.
            tool_choice (str | dict | None): Optional tool selection hint passed through to the model.
            **kwargs: Additional provider-specific payload fields to include in the request.
        
        Returns:
            APIResponse: Normalized response containing:
                - content: Generated text content (or None if a function/tool call was returned).
                - model: The model identifier used.
                - provider: "local".
                - usage: Dict with "input_tokens" and "output_tokens" (integers; 0 when not reported).
                - latency_ms: Observed request latency in milliseconds (0 for the Ollama fallback).
                - raw_response: Raw JSON response from the provider.
                - function_call: FunctionCall object when the model invoked a tool (otherwise None).
        
        Raises:
            Exception: Re-raises the original exception if the primary request fails and the Ollama-format fallback cannot be used or fails. The original exception is also re-raised immediately if the primary request fails while `functions` are provided, because the fallback does not support functions.
        """

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

                if not self.session:
                    self.session = aiohttp.ClientSession()

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