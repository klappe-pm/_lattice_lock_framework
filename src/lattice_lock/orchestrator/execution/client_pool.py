import logging

from lattice_lock.orchestrator.providers import ProviderUnavailableError, get_api_client
from lattice_lock.orchestrator.providers.base import BaseAPIClient

logger = logging.getLogger(__name__)


class ClientPool:
    """
    Manages a pool of API clients for different providers.
    Handles lazy loading and caching of client instances.
    """

    def __init__(self):
        self._clients: dict[str, BaseAPIClient] = {}

    def get_client(self, provider: str) -> BaseAPIClient:
        """
        Get or create an API client for the specified provider.

        Args:
            provider: The provider name (e.g., 'openai', 'anthropic').

        Returns:
            The API client instance.

        Raises:
            ProviderUnavailableError: If provider credentials are missing.
        """
        if provider not in self._clients:
            try:
                # We use check_availability=True to ensure we don't return broken clients
                self._clients[provider] = get_api_client(provider, check_availability=True)
                logger.debug(f"Initialized new client for provider: {provider}")
            except ProviderUnavailableError as e:
                logger.error(f"Cannot create client for provider '{provider}': {e.message}")
                raise

        return self._clients[provider]

    async def close_all(self):
        """Close all initialized clients."""
        for name, client in self._clients.items():
            try:
                # Assuming clients might have a close method in the future,
                # strictly speaking BaseAPIClient doesn't mandate it yet but good practice.
                if hasattr(client, "close"):
                    import inspect

                    if inspect.iscoroutinefunction(client.close):
                        await client.close()
                    else:
                        client.close()
            except Exception as e:
                logger.warning(f"Error closing client {name}: {e}")
        self._clients.clear()

    def reset(self):
        """Clear the client cache (useful for testing)."""
        self._clients.clear()
