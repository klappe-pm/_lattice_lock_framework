"""
API Client Factory
"""

import logging

from lattice_lock.config import AppConfig, get_config

from .anthropic import AnthropicAPIClient
from .azure import AzureOpenAIClient
from .base import BaseAPIClient, ProviderAvailability
from .bedrock import BedrockAPIClient
from .google import GoogleAPIClient
from .local import LocalModelClient
from .openai import OpenAIAPIClient
from .xai import GrokAPIClient

logger = logging.getLogger(__name__)


def get_api_client(
    provider: str, check_availability: bool = True, config: AppConfig | None = None, **kwargs
) -> BaseAPIClient:
    """
    Factory function to get the appropriate API client.

    Args:
        provider: The provider name (e.g., 'openai', 'anthropic', 'bedrock')
        check_availability: If True, check credentials before creating client.
                          Set to False to skip availability check.
        config: Application configuration object (optional, uses global if None)
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

    # Load config if not provided
    if config is None:
        config = get_config()

    # Map provider aliases
    provider_aliases = {
        "grok": "xai",
        "gemini": "google",
        "claude": "anthropic",
        "ollama": "local",
    }
    provider_lower = provider_aliases.get(provider_lower, provider_lower)

    # Dictionary mapping provider names to client classes
    clients = {
        "xai": GrokAPIClient,
        "openai": OpenAIAPIClient,
        "google": GoogleAPIClient,
        "anthropic": AnthropicAPIClient,
        "azure": AzureOpenAIClient,
        "bedrock": BedrockAPIClient,
        "local": LocalModelClient,
    }

    # Special handling for 'dial' which maps to AnthropicAPIClient with specific flag
    if provider_lower == "dial":
        client_class = AnthropicAPIClient
        kwargs["use_dial"] = True
    elif provider_lower in clients:
        client_class = clients[provider_lower]
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Available providers: {list(clients.keys()) + ['dial']}"
        )

    # Check availability if requested
    if check_availability:
        # For 'dial', we check DIAL requirements
        check_provider = "dial" if provider_lower == "dial" else provider_lower

        # Check against ProviderAvailability singleton AND/OR try instantiation validation
        # Since we moved validation to __init__, instantiation WILL fail if check_availability is implicitly handled there.
        # But BaseAPIClient.__init__ calls _validate_config().
        # So we can just rely on instantiation to raise ProviderUnavailableError.
        # However, ProviderAvailability singleton gives us a way to check WITHOUT instantiating.
        # Let's check singleton first for better error messages or pre-checks.
        if not ProviderAvailability.is_available(check_provider):
            # Wait, ProviderAvailability.is_available checks env vars.
            # If env vars are missing, we raise here.
            pass

        # Actually, the requirement says "raises ProviderUnavailableError".
        # If we rely on __init__, it does that.
        # If we check ProviderAvailability, that's optimizing.
        # But ProviderAvailability currently only checks basic keys.
        # Let's trust the class __init__ validation mostly, but we can do a quick check if simple credentials.

        # Actually, let's just let instantiation handle it as it's the source of truth for "required config".
        pass

    logger.debug(f"Creating {client_class.__name__} for provider '{provider}'")
    return client_class(config=config, **kwargs)
