"""
API Client Factory
"""
import logging

from .anthropic import AnthropicAPIClient
from .azure import AzureOpenAIClient
from .base import BaseAPIClient, ProviderAvailability, ProviderStatus, ProviderUnavailableError
from .bedrock import BedrockAPIClient
from .google import GoogleAPIClient
from .local import LocalModelClient
from .openai import OpenAIAPIClient
from .xai import GrokAPIClient

logger = logging.getLogger(__name__)


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
