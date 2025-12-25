"""
DEPRECATED: Import from lattice_lock.orchestrator.providers instead.
"""
import warnings

# Re-export exceptions and types that were originally imported in api_clients.py
from .exceptions import (
    APIClientError,
    AuthenticationError,
    InvalidRequestError,
    ProviderConnectionError,
    RateLimitError,
    ServerError,
)
from .providers import (
    AnthropicAPIClient,
    AzureOpenAIClient,
    BaseAPIClient,
    BedrockAPIClient,
    GoogleAPIClient,
    GrokAPIClient,
    LocalModelClient,
    OpenAIAPIClient,
    ProviderAvailability,
    ProviderStatus,
    ProviderUnavailableError,
    XAIAPIClient,
    get_api_client,
)
from .types import APIResponse, FunctionCall

# Preserve old alias for backward compatibility explicitly
GrokAPIClient = XAIAPIClient

warnings.warn(
    "Importing from api_clients is deprecated. Use lattice_lock.orchestrator.providers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BaseAPIClient",
    "OpenAIAPIClient",
    "GrokAPIClient",
    "XAIAPIClient",
    "GoogleAPIClient",
    "AnthropicAPIClient",
    "AzureOpenAIClient",
    "BedrockAPIClient",
    "LocalModelClient",
    "ProviderAvailability",
    "ProviderStatus",
    "ProviderUnavailableError",
    "get_api_client",
    "APIClientError",
    "AuthenticationError",
    "InvalidRequestError",
    "ProviderConnectionError",
    "RateLimitError",
    "ServerError",
    "APIResponse",
    "FunctionCall",
]
