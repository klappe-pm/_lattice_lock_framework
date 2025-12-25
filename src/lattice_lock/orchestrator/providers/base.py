"""
Provider Base Classes and Interfaces.

This module defines the abstract base class and common interfaces
for all model provider clients.

For the full provider implementations, see api_clients.py.
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lattice_lock.orchestrator.types import APIResponse

logger = logging.getLogger(__name__)


class BaseProviderClient(ABC):
    """Abstract base class for model provider clients.
    
    All provider clients should inherit from this class and implement
    the required abstract methods.
    
    Attributes:
        provider_name: Canonical name of the provider.
    """
    
    provider_name: str = "unknown"
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider connectivity and credential validity.
        
        Implementation Requirements:
        - Verify API credentials are valid (not just present)
        - Confirm provider endpoint is reachable
        - Cache results for max 60 seconds
        - Must not consume significant billable quota
        
        Returns:
            True if provider is healthy, False otherwise.
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> "APIResponse":
        """Execute a chat completion request.
        
        Args:
            model: Model identifier.
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.
            functions: Optional list of function definitions for tool use.
            tool_choice: Optional tool selection constraint.
            **kwargs: Provider-specific additional arguments.
            
        Returns:
            APIResponse with completion results.
        """
        pass
    
    async def validate_credentials(self) -> bool:
        """Validate provider credentials.
        
        Default implementation delegates to health_check.
        
        Returns:
            True if credentials are valid.
        """
        return await self.health_check()


# Re-export the actual BaseAPIClient for backward compatibility
from lattice_lock.orchestrator.api_clients import BaseAPIClient

__all__ = ["BaseProviderClient", "BaseAPIClient"]
