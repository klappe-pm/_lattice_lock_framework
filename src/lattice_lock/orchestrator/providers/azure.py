"""
Azure OpenAI Provider
"""
import json
import logging
import os

from lattice_lock.orchestrator.types import APIResponse, FunctionCall
from .base import BaseAPIClient

logger = logging.getLogger(__name__)

class AzureOpenAIClient(BaseAPIClient):
    """Azure OpenAI Service API client"""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None, **kwargs):
        api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required")
        self.api_version = kwargs.get("api_version", "2024-02-15-preview")
        super().__init__(api_key, endpoint)

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
        """Send chat completion request to Azure OpenAI"""

        headers = {"api-key": self.api_key, "Content-Type": "application/json"}

        payload = {"messages": messages, "temperature": temperature, **kwargs}

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

        # Azure OpenAI uses deployment names in the endpoint
        endpoint = f"openai/deployments/{model}/chat/completions?api-version={self.api_version}"
        data, latency_ms = await self._make_request("POST", endpoint, headers, payload)

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
            provider="azure",
            usage={
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )
