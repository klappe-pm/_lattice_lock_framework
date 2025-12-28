"""
Lattice Lock Provider Package

API clients for all supported model providers.
"""

from lattice_lock.exceptions import ProviderUnavailableError

from .anthropic import AnthropicAPIClient
from .azure import AzureOpenAIClient
from .base import BaseAPIClient, ProviderAvailability, ProviderStatus
from .bedrock import BedrockAPIClient
from .factory import get_api_client
from .google import GoogleAPIClient
from .local import LocalModelClient
from .openai import OpenAIAPIClient
from .xai import GrokAPIClient

# Backward compatibility alias for legacy imports using XAIAPIClient
XAIAPIClient = GrokAPIClient

__all__ = [
    "AnthropicAPIClient",
    "AzureOpenAIClient",
    "BaseAPIClient",
    "BedrockAPIClient",
    "GoogleAPIClient",
    "GrokAPIClient",
    "LocalModelClient",
    "OpenAIAPIClient",
    "ProviderAvailability",
    "ProviderStatus",
    "ProviderUnavailableError",
    "XAIAPIClient",
    "get_api_client",
]
