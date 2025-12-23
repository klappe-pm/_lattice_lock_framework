"""
Lattice Lock Framework Exceptions

Defines the custom exception hierarchy for API clients and provider interactions.
"""


from lattice_lock.errors.types import LatticeError

class APIClientError(LatticeError):
    """Base exception for all API client errors."""
    
    error_code = "LL-600"

    def __init__(self, message: str, provider: str | None = None, status_code: int | None = None):
        details = {}
        if provider:
            details["provider"] = provider
        if status_code is not None:
            details["status_code"] = status_code
            
        super().__init__(message, error_code=self.error_code, details=details)
        self.provider = provider
        self.status_code = status_code


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
