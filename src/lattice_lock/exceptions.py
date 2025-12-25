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
    pass
