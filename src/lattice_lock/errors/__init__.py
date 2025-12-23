"""
Lattice Lock Error Handling

Provides comprehensive error classification, handling, and remediation
for the Lattice Lock Framework.

Usage:
    import logging
    from lattice_lock.errors import (
        LatticeError,
        SchemaValidationError,
        classify_error,
        ErrorContext,
    )

    logger = logging.getLogger("lattice_lock.errors")

    try:
        validate_schema(path)
    except SchemaValidationError as e:
        context = classify_error(e)
        logger.info(f"Severity: {context.severity}")
        logger.info(f"Remediation: {context.remediation}")
"""

from lattice_lock.errors.classification import (
    Category,
    ErrorContext,
    Recoverability,
    Severity,
    classify_error,
    get_category,
    get_recoverability,
    get_severity,
)
from lattice_lock.errors.middleware import (
    ErrorHandler,
    ErrorMetrics,
    RetryConfig,
    error_boundary,
    format_error_report,
    get_metrics,
    handle_errors,
    reset_metrics,
    with_graceful_degradation,
)
from lattice_lock.errors.remediation import RemediationInfo, format_remediation, get_remediation
from lattice_lock.errors.types import (
    AgentError,
    ConfigurationError,
    GauntletFailureError,
    LatticeError,
    LatticeRuntimeError,
    NetworkError,
    SchemaValidationError,
    SheriffViolationError,
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
