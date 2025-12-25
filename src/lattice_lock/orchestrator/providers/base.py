"""
Base classes for API providers.
"""

import asyncio
import json
import logging
import os
import re
import threading
import time
from enum import Enum

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from lattice_lock.orchestrator.exceptions import (
    APIClientError,
    AuthenticationError,
    InvalidRequestError,
    ProviderConnectionError,
    RateLimitError,
    ServerError,
)
from lattice_lock.orchestrator.types import APIResponse, FunctionCall

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
    _lock = threading.Lock()
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
        """Get the singleton instance of ProviderAvailability."""
        if cls._instance is None:
            with cls._lock:
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


class ProviderUnavailableError(Exception):
    """Raised when a provider is unavailable due to missing credentials."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"Provider '{provider}' unavailable: {message}")


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
            # Shield cleanup from cancellation to ensure session is closed
            await asyncio.shield(self.session.close())

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
