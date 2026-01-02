"""Framework-wide custom exceptions."""


class LatticeError(Exception):
    """Base exception for Lattice Lock framework."""

    pass


class BillingIntegrityError(LatticeError):
    """Token aggregation or billing data corruption detected."""

    pass


class SecurityConfigurationError(LatticeError):
    """Security requirements not met for current environment."""

    pass


class BackgroundTaskError(LatticeError):
    """Background task failed to complete within timeout."""

    pass


class ProviderUnavailableError(LatticeError):
    """Provider credentials missing or provider unreachable."""

    def __init__(self, provider: str, reason: str):
        self.provider = provider
        self.reason = reason
        super().__init__(f"Provider '{provider}' unavailable: {reason}")

    @property
    def message(self) -> str:
        """Alias for reason for backwards compatibility."""
        return self.reason
