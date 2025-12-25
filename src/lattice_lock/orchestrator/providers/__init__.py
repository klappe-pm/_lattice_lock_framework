"""
Lattice Lock Orchestrator Providers Package.

This package provides provider client implementations for various LLM providers.

Usage:
    from lattice_lock.orchestrator.providers import get_api_client
    
    client = get_api_client("openai")
"""

# Re-export factory functions
from lattice_lock.orchestrator.providers.factory import (
    get_api_client,
    create_provider,
    ProviderAvailability,
    ProviderStatus,
    ProviderUnavailableError,
)

# Re-export base classes
from lattice_lock.orchestrator.providers.base import (
    BaseProviderClient,
    BaseAPIClient,
)

# Re-export specialized providers
from lattice_lock.orchestrator.providers.bedrock import BedrockClient
from lattice_lock.orchestrator.providers.fallback import FallbackManager

__all__ = [
    # Factory
    "get_api_client",
    "create_provider",
    "ProviderAvailability",
    "ProviderStatus",
    "ProviderUnavailableError",
    # Base
    "BaseProviderClient",
    "BaseAPIClient",
    # Providers
    "BedrockClient",
    "FallbackManager",
]

