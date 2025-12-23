#!/usr/bin/env python3
"""
Unified API Clients for all model providers
Handles real API calls with error handling and retry logic
"""

import json
import logging
import os
import re
import time
from collections.abc import AsyncIterator
from enum import Enum

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from .exceptions import (
    APIClientError,
    AuthenticationError,
    InvalidRequestError,
    ProviderConnectionError,
    RateLimitError,
    ServerError,
)
from .types import APIResponse, FunctionCall

logger = logging.getLogger(__name__)


def _redact_sensitive_in_message(message: str) -> str:
    """Redact sensitive data from error messages (URLs with tokens, API keys, etc.)."""
    # Redact API keys in URLs (e.g., ?key=xxx, &api_key=xxx)
    message = re.sub(
        r"([?&](?:key|api_key|token|access_token|apikey)=)[^&\s]+",
        r"\1[REDACTED]",
        message,
        flags=re.IGNORECASE,
    )
    # Redact Bearer tokens
    message = re.sub(r"(Bearer\s+)[^\s]+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    # Redact Authorization headers
    message = re.sub(r"(Authorization:\s*)[^\s]+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    return message


class ProviderStatus(Enum):
    """Provider maturity/availability status."""

    PRODUCTION = "production"  # Fully supported, tested, recommended
    BETA = "beta"  # Working but may have issues
    EXPERIMENTAL = "experimental"  # Use at own risk, may not work
    UNAVAILABLE = "unavailable"  # Missing credentials or not configured


class ProviderAvailability:
    """Tracks provider availability and credential status."""

    _instance = None
    _checked = False
    _status: dict[str, ProviderStatus] = {}
    _messages: dict[str, str] = {}

    # Required environment variables per provider
    REQUIRED_CREDENTIALS = {
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "xai": ["XAI_API_KEY"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
        "bedrock": [],  # Uses AWS credentials from environment/config
        "dial": ["DIAL_API_KEY"],
        "local": [],  # Local models (Ollama/vLLM), no credentials needed
    }

    # Provider maturity classification
    PROVIDER_MATURITY = {
        "openai": ProviderStatus.PRODUCTION,
        "anthropic": ProviderStatus.PRODUCTION,
        "google": ProviderStatus.PRODUCTION,
        "xai": ProviderStatus.PRODUCTION,
        "local": ProviderStatus.PRODUCTION,  # Local models (Ollama/vLLM)
        "azure": ProviderStatus.BETA,
        "dial": ProviderStatus.BETA,
        "bedrock": ProviderStatus.EXPERIMENTAL,
    }

    @classmethod
    def get_instance(cls) -> "ProviderAvailability":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def check_all_providers(cls) -> dict[str, ProviderStatus]:
        """Check availability of all providers. Returns status dict."""
        instance = cls.get_instance()
        if instance._checked:
            return instance._status

        for provider, required_vars in cls.REQUIRED_CREDENTIALS.items():
            missing = [var for var in required_vars if not os.getenv(var)]

            if missing:
                instance._status[provider] = ProviderStatus.UNAVAILABLE
                instance._messages[provider] = f"Missing credentials: {', '.join(missing)}"
                logger.warning(f"Provider '{provider}' unavailable: {instance._messages[provider]}")
            else:
                instance._status[provider] = cls.PROVIDER_MATURITY.get(
                    provider, ProviderStatus.EXPERIMENTAL
                )
                instance._messages[provider] = f"Status: {instance._status[provider].value}"

        instance._checked = True
        return instance._status

    @classmethod
    def is_available(cls, provider: str) -> bool:
        """Check if a provider is available (has credentials)."""
        status = cls.check_all_providers()
        return status.get(provider, ProviderStatus.UNAVAILABLE) != ProviderStatus.UNAVAILABLE

    @classmethod
    def get_status(cls, provider: str) -> ProviderStatus:
        """Get the status of a provider."""
        status = cls.check_all_providers()
        return status.get(provider, ProviderStatus.UNAVAILABLE)

    @classmethod
    def get_message(cls, provider: str) -> str:
        """Get the status message for a provider."""
        cls.check_all_providers()
        instance = cls.get_instance()
        return instance._messages.get(provider, "Unknown provider")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers."""
        status = cls.check_all_providers()
        return [p for p, s in status.items() if s != ProviderStatus.UNAVAILABLE]

    @classmethod
    def reset(cls):
        """Reset the singleton for testing."""
        cls._instance = None
        cls._checked = False
        cls._status = {}
        cls._messages = {}


class BaseAPIClient:
    """Base class for all API clients"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True
    )
    async def _make_request(self, method: str, endpoint: str, headers: dict, payload: dict) -> dict:
        """Make API request with retry logic"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()

        try:
            async with self.session.request(method, url, headers=headers, json=payload) as response:
                latency_ms = int((time.time() - start_time) * 1000)

                if response.status != 200:
                    try:
                        error_text = await response.text()
                        # try to parse json if possible to get better error message
                        try:
                            error_json = json.loads(error_text)
                            error_msg = error_json.get("error", {}).get("message", error_text)
                        except (json.JSONDecodeError, KeyError, TypeError):
                            error_msg = error_text
                    except (aiohttp.ClientError, UnicodeDecodeError):
                        error_msg = f"Unknown error (status {response.status})"

                    msg = f"API Error {response.status}: {error_msg}"

                    if response.status == 401 or response.status == 403:
                        raise AuthenticationError(msg, status_code=response.status)
                    elif response.status == 429:
                        raise RateLimitError(msg, status_code=response.status)
                    elif response.status >= 500:
                        raise ServerError(msg, status_code=response.status)
                    elif response.status == 400:
                        raise InvalidRequestError(msg, status_code=response.status)
                    else:
                        raise APIClientError(msg, status_code=response.status)

                data = await response.json()
                return data, latency_ms

        except aiohttp.ClientError as e:
            redacted_msg = _redact_sensitive_in_message(str(e))
            logger.error(f"Connection failed: {redacted_msg}")
            raise ProviderConnectionError(f"Connection failed: {redacted_msg}") from e
        except APIClientError:
            raise
        except Exception as e:
            redacted_msg = _redact_sensitive_in_message(str(e))
            logger.error(f"Request failed: {redacted_msg}")
            raise APIClientError(f"Unexpected error: {redacted_msg}") from e

    async def chat_completion(
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
        Unified entry point for chat completions.
        Handles common logic (logging, tracing, error wrapping) and delegates to provider implementation.
        """
        try:
            # Common logging or pre-processing could go here
            return await self._chat_completion_impl(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                tool_choice=tool_choice,
                **kwargs,
            )
        except Exception as e:
            redacted_msg = _redact_sensitive_in_message(str(e))
            logger.error(f"Chat completion failed for {self.__class__.__name__}: {redacted_msg}")
            raise

    async def _chat_completion_impl(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
        functions: list[dict] | None,
        tool_choice: str | dict | None,
        **kwargs,
    ) -> APIResponse:
        """
        Provider-specific implementation of chat completion.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _chat_completion_impl")

    async def validate_credentials(self) -> bool:
        """
        Validate credentials by making a lightweight API call.
        Subclasses should implement this with a cheap provider-specific call.
        """
        # Default fallback for now
        return True

    async def health_check(self) -> bool:
        """
        Check provider health status.
        """
        try:
            return await self.validate_credentials()
        except Exception as e:
            redacted_msg = _redact_sensitive_in_message(str(e))
            logger.error(f"Health check failed: {redacted_msg}")
            return False


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


class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API client"""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        super().__init__(api_key, "https://api.openai.com/v1")

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
        """Send chat completion request to OpenAI"""

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {"model": model, "messages": messages, "temperature": temperature, **kwargs}

        if max_tokens:
            payload["max_tokens"] = max_tokens
        if functions:
            payload["tools"] = [{"type": "function", "function": f} for f in functions]
        if tool_choice:
            payload["tool_choice"] = tool_choice

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
            provider="openai",
            usage={
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            function_call=function_call,
        )


class GoogleAPIClient(BaseAPIClient):
    """Google Gemini API client"""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        super().__init__(api_key, "https://generativelanguage.googleapis.com/v1beta")

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
        """Send chat completion request to Google Gemini"""

        headers = {
            "Content-Type": "application/json",
        }

        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            contents.append(
                {
                    "parts": [{"text": msg["content"]}],
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
        data, latency_ms = await self._make_request("POST", endpoint, headers, payload)

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


class AnthropicAPIClient(BaseAPIClient):
    """Anthropic Claude API client (via DIAL or direct)"""

    def __init__(self, api_key: str | None = None, use_dial: bool = False, **kwargs):
        if use_dial:
            api_key = api_key or os.getenv("DIAL_API_KEY")
            if not api_key:
                raise ValueError("DIAL_API_KEY not found")
            # Assuming DIAL endpoint - adjust as needed
            super().__init__(api_key, "https://dial.api.endpoint/v1")
        else:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            super().__init__(api_key, "https://api.anthropic.com/v1")

        self.use_dial = use_dial
        self.anthropic_version = kwargs.get("api_version", "2023-06-01")

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
        """Send chat completion request to Anthropic/DIAL"""

        response_content = None
        function_call = None

        if self.use_dial:
            # DIAL format (OpenAI-compatible)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {"model": model, "messages": messages, "temperature": temperature, **kwargs}

            if max_tokens:
                payload["max_tokens"] = max_tokens
            if functions:
                payload["tools"] = [{"type": "function", "function": f} for f in functions]

            data, latency_ms = await self._make_request(
                "POST", "chat/completions", headers, payload
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
                    system_msg = msg["content"]
                else:
                    claude_messages.append({"role": msg["role"], "content": msg["content"]})

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

            data, latency_ms = await self._make_request("POST", "messages", headers, payload)

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


class BedrockAPIClient(BaseAPIClient):
    """
    Amazon Bedrock API client.

    Status: EXPERIMENTAL

    This client wraps the BedrockClient from providers/bedrock.py.
    Bedrock requires AWS credentials and optionally boto3.

    To use Bedrock models:
    1. Install boto3: pip install boto3
    2. Configure AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
    """

    def __init__(self, region: str = "us-east-1", **kwargs):
        # Bedrock uses AWS credentials, not API keys
        super().__init__("", f"https://bedrock-runtime.{region}.amazonaws.com")
        self.region = region
        self.anthropic_version = kwargs.get("api_version", "bedrock-2023-05-31")
        self._warned = False

        # Import and initialize the actual Bedrock client
        from .providers.bedrock import BedrockClient

        self._bedrock_client = BedrockClient(region_name=region)

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
        Send chat completion request to Amazon Bedrock.

        Note: This is an experimental client.
        """
        if not self._warned:
            logger.warning(
                "BedrockAPIClient is EXPERIMENTAL. "
                "Bedrock requires AWS Signature V4 authentication via boto3."
            )
            self._warned = True

        # Check if Bedrock client is enabled
        if not self._bedrock_client.enabled:
            error_msg = "Bedrock provider is not configured (boto3 not installed or missing AWS credentials)."
            if functions:
                error_msg += " Additionally, Bedrock function calling requires model-specific tool definitions."
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                raw_response={"error": error_msg},
                error=error_msg,
            )

        # Delegate to the actual Bedrock client (async call)
        try:
            response = await self._bedrock_client.generate(
                model=model,
                messages=messages,
                max_tokens=max_tokens or 4096,
                anthropic_version=self.anthropic_version,
            )
            return response
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                error=str(e),
            )


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


class ProviderUnavailableError(Exception):
    """Raised when a provider is unavailable due to missing credentials."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"Provider '{provider}' unavailable: {message}")


def get_api_client(provider: str, check_availability: bool = True, **kwargs) -> BaseAPIClient:
    """
    Factory function to get the appropriate API client.

    Args:
        provider: The provider name (e.g., 'openai', 'anthropic', 'bedrock')
        check_availability: If True, check credentials before creating client.
                          Set to False to skip availability check.
        **kwargs: Additional arguments passed to the client constructor.

    Returns:
        BaseAPIClient: The appropriate API client instance.

    Raises:
        ProviderUnavailableError: If provider credentials are missing and
                                  check_availability is True.
        ValueError: If provider is unknown.
    """
    # Normalize provider name
    provider_lower = provider.lower()

    # Map provider aliases
    provider_aliases = {
        "grok": "xai",
        "gemini": "google",
        "claude": "anthropic",
        "ollama": "local",
    }
    provider_lower = provider_aliases.get(provider_lower, provider_lower)

    clients = {
        "xai": GrokAPIClient,
        "openai": OpenAIAPIClient,
        "google": GoogleAPIClient,
        "anthropic": AnthropicAPIClient,
        "dial": lambda **kw: AnthropicAPIClient(use_dial=True, **kw),
        "azure": AzureOpenAIClient,
        "bedrock": BedrockAPIClient,
        "local": LocalModelClient,
    }

    if provider_lower not in clients:
        raise ValueError(
            f"Unknown provider: {provider}. Available providers: {list(clients.keys())}"
        )

    # Check availability if requested
    if check_availability:
        status = ProviderAvailability.get_status(provider_lower)
        if status == ProviderStatus.UNAVAILABLE:
            message = ProviderAvailability.get_message(provider_lower)
            raise ProviderUnavailableError(provider_lower, message)

        # Log warning for experimental providers
        if status == ProviderStatus.EXPERIMENTAL:
            logger.warning(
                f"Provider '{provider_lower}' is EXPERIMENTAL. "
                f"It may not work as expected. {ProviderAvailability.get_message(provider_lower)}"
            )

    return clients[provider_lower](**kwargs)
