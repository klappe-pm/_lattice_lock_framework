"""
Provider Factory.

This module provides factory functions for creating provider clients.
Re-exports from api_clients.py for convenience.
"""

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lattice_lock.orchestrator.api_clients import BaseAPIClient

# Re-export the factory function
from lattice_lock.orchestrator.api_clients import (
    get_api_client,
    ProviderAvailability,
    ProviderStatus,
    ProviderUnavailableError,
)


def create_provider(provider: str, **kwargs) -> "BaseAPIClient":
    """Create a provider client instance.
    
    This is an alias for get_api_client() for semantic clarity.
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic', 'xai')
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured provider client instance.
        
    Raises:
        ProviderUnavailableError: If provider credentials are missing.
        ValueError: If provider is unknown.
    """
    return get_api_client(provider, **kwargs)


__all__ = [
    "get_api_client",
    "create_provider",
    "ProviderAvailability",
    "ProviderStatus",
    "ProviderUnavailableError",
]
