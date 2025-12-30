"""
Lattice Lock Provider Package

API clients for all supported model providers.
"""

from lattice_lock.exceptions import ProviderUnavailableError

# Provider Implementations
from .anthropic import AnthropicAPIClient
from .azure import AzureOpenAIClient
from .base import BaseAPIClient, ProviderAvailability, ProviderStatus
from .bedrock import BedrockAPIClient
from .factory import get_api_client
from .google import GoogleAPIClient
from .local import LocalModelClient
from .openai import OpenAIAPIClient
from .xai import GrokAPIClient

# Generic XAI alias if needed, though GrokAPIClient is the class name in xai.py
XAIAPIClient = GrokAPIClient

__all__ = [
    "BaseAPIClient",
    "ProviderAvailability",
    "ProviderStatus",
    "ProviderUnavailableError",
    "get_api_client",
    # Providers
    "AnthropicAPIClient",
    "AzureOpenAIClient",
    "BedrockAPIClient",
    "GoogleAPIClient",
    "LocalModelClient",
    "OpenAIAPIClient",
    "GrokAPIClient",
    "XAIAPIClient",
]
