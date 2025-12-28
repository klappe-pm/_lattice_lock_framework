"""Base classes for all API providers."""

import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from lattice_lock.config import AppConfig
from lattice_lock.orchestrator.exceptions import (
    AuthenticationError,
    ProviderConnectionError,
    RateLimitError,
    ServerError,
)

if TYPE_CHECKING:
    import aiohttp

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider availability status."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
    ERROR = "error"


class ProviderAvailability:
    """
    Singleton for tracking provider credential availability.

    Checks environment for required API keys and tracks provider status.
    """

    _instance: Optional["ProviderAvailability"] = None
    _status: dict[str, ProviderStatus] = {}

    REQUIRED_CREDENTIALS: dict[str, list[str]] = {
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "xai": ["XAI_API_KEY"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
        "bedrock": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
        "local": [],  # No credentials required
        "dial": ["DIAL_URL"],  # Assuming DIAL requires a URL
    }

    @classmethod
    def reset(cls) -> None:
        """Reset singleton state for testing."""
        cls._instance = None
        cls._status.clear()

    @classmethod
    def is_available(cls, provider: str) -> bool:
        """Check if provider has required credentials."""
        required = cls.REQUIRED_CREDENTIALS.get(provider.lower(), [])
        return all(os.environ.get(key) for key in required)

    @classmethod
    def get_status(cls, provider: str) -> ProviderStatus:
        """Get cached status for provider."""
        return cls._status.get(provider.lower(), ProviderStatus.UNKNOWN)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of providers with configured credentials."""
        return [p for p in cls.REQUIRED_CREDENTIALS if cls.is_available(p)]


class BaseAPIClient(ABC):
    """
    Abstract base class for all API provider clients.

    All providers must:
    1. Validate configuration on initialization
    2. Implement health_check for connectivity verification
    3. Implement chat_completion for LLM calls
    """

    def __init__(self, config: AppConfig):
        """
        Initialize client with configuration.

        Args:
            config: Application configuration object

        Raises:
            ProviderUnavailableError: If required credentials missing
        """
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        self._validate_config()
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Provider-specific configuration validation.

        Must check for required API keys and raise ProviderUnavailableError
        if any are missing.
        """
        pass

    async def _get_session(self) -> "aiohttp.ClientSession":
        """Get or create aiohttp session."""
        import aiohttp

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> tuple[dict[str, Any], float]:
        """
        Make HTTP request with latency tracking.

        Returns:
            Tuple of (response_data, latency_ms)
        """
        import time

        import aiohttp

        session = await self._get_session()
        start_time = time.perf_counter()

        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                latency_ms = (time.perf_counter() - start_time) * 1000

                try:
                    data = await response.json()
                except Exception:
                    text = await response.text()
                    # If not JSON, return text wrapped or raise error depending on status
                    if response.status >= 400:
                        raise Exception(f"Request failed {response.status}: {text}")
                    data = {"content": text}  # Fallback

                if response.status >= 400:
                    # Attempt to extract error message
                    error_msg = str(data)
                    if isinstance(data, dict):
                        error_msg = data.get("error", {}).get("message", str(data))

                    if response.status == 401 or response.status == 403:
                        raise AuthenticationError(error_msg, status_code=response.status)
                    if response.status == 429:
                        raise RateLimitError(error_msg, status_code=response.status)
                    if response.status >= 500:
                        raise ServerError(error_msg, status_code=response.status)
                    raise Exception(f"Provider error {response.status}: {error_msg}")

                return data, latency_ms
        except (AuthenticationError, RateLimitError, ServerError) as e:
            raise e
        except Exception as e:
            # Rethrow as specific error types would be better, but generic for now
            raise ProviderConnectionError(str(e)) from e

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify provider connectivity and credential validity.

        Returns:
            True if provider is healthy and accessible

        Raises:
            ProviderUnavailableError: If health check fails
        """
        pass

    @abstractmethod
    async def chat_completion(self, model: str, messages: list[dict[str, Any]], **kwargs) -> Any:
        """
        Execute a chat completion request.

        Args:
            model: Model identifier
            messages: Conversation messages

        Returns:
            APIResponse with completion result
        """
        pass

    async def close(self):
        """Close underlying session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.close()
