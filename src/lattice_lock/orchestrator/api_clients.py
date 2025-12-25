"""
DEPRECATED: Import from lattice_lock.orchestrator.providers instead.
"""
import warnings

# Re-export exceptions for backward compatibility
from .exceptions import (
    APIClientError,
    AuthenticationError,
    InvalidRequestError,
    ProviderConnectionError,
    RateLimitError,
    ServerError,
)

from .providers import (
    BaseAPIClient,
    ProviderAvailability,
    ProviderUnavailableError,
    OpenAIAPIClient,
    AnthropicAPIClient,
    GoogleAPIClient,
    XAIAPIClient,
    GrokAPIClient,
    AzureOpenAIClient,
    BedrockAPIClient,
    get_api_client,
)

warnings.warn(
    "Importing from api_clients is deprecated. Use lattice_lock.orchestrator.providers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "APIClientError",
    "AuthenticationError",
    "InvalidRequestError",
    "ProviderConnectionError",
    "RateLimitError",
    "ServerError",
    "BaseAPIClient",
    "ProviderAvailability",
    "ProviderUnavailableError",
    "OpenAIAPIClient",
    "AnthropicAPIClient",
    "GoogleAPIClient",
    "XAIAPIClient",
    "GrokAPIClient",
    "AzureOpenAIClient",
    "BedrockAPIClient",
    "get_api_client",
]
