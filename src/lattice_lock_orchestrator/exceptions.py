"""
Lattice Lock Framework Exceptions

Defines the custom exception hierarchy for API clients and provider interactions.
"""


class APIClientError(Exception):
    """Base exception for all API client errors."""

    def __init__(self, message: str, provider: str | None = None, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)


class ProviderConnectionError(APIClientError):
    """Raised when connection to a provider fails (network issues, timeout)."""

    pass


class InvalidPolicyError(APIClientError):
    """Raised when a request violates configured policies."""

    pass


class ModelNotAvailableError(APIClientError):
    """Raised when a requested model is deprecated, access is denied, or it is not found."""

    pass


class RateLimitError(APIClientError):
    """Raised when API rate limits are exceeded (HTTP 429)."""

    pass


class AuthenticationError(APIClientError):
    """Raised when API credentials are invalid or missing (HTTP 401/403)."""

    pass


class InvalidRequestError(APIClientError):
    """Raised when the request parameters are invalid (HTTP 400)."""

    pass


class ServerError(APIClientError):
    """Raised when the provider returns a 5xx error."""

    pass
