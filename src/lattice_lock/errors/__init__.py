"""
Lattice Lock Error Handling

Provides comprehensive error classification, handling, and remediation
for the Lattice Lock Framework.

Usage:
    from lattice_lock.errors import (
        LatticeError,
        SchemaValidationError,
        classify_error,
        ErrorContext,
    )

    try:
        validate_schema(path)
    except SchemaValidationError as e:
        context = classify_error(e)
        print(f"Severity: {context.severity}")
        print(f"Remediation: {context.remediation}")
"""

from lattice_lock.errors.types import (
    LatticeError,
    SchemaValidationError,
    SheriffViolationError,
    GauntletFailureError,
    LatticeRuntimeError,
    ConfigurationError,
    NetworkError,
    AgentError,
)

from lattice_lock.errors.classification import (
    Severity,
    Category,
    Recoverability,
    ErrorContext,
    classify_error,
    get_severity,
    get_category,
    get_recoverability,
)

from lattice_lock.errors.remediation import (
    RemediationInfo,
    get_remediation,
    format_remediation,
)

from lattice_lock.errors.middleware import (
    ErrorMetrics,
    RetryConfig,
    ErrorHandler,
    error_boundary,
    handle_errors,
    with_graceful_degradation,
    get_metrics,
    reset_metrics,
    format_error_report,
)

__all__ = [
    "LatticeError",
    "SchemaValidationError",
    "SheriffViolationError",
    "GauntletFailureError",
    "LatticeRuntimeError",
    "ConfigurationError",
    "NetworkError",
    "AgentError",
    "Severity",
    "Category",
    "Recoverability",
    "ErrorContext",
    "classify_error",
    "get_severity",
    "get_category",
    "get_recoverability",
    "RemediationInfo",
    "get_remediation",
    "format_remediation",
    "ErrorMetrics",
    "RetryConfig",
    "ErrorHandler",
    "error_boundary",
    "handle_errors",
    "with_graceful_degradation",
    "get_metrics",
    "reset_metrics",
    "format_error_report",
]
