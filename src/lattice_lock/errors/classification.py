"""
Lattice Lock Error Classification

Defines severity levels, categories, and recoverability for error classification.
Used by the error handling middleware to determine appropriate responses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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


class Severity(Enum):
    """Error severity levels.

    Determines the urgency and impact of an error.
    Used for logging levels and alerting thresholds.
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        return self.value

    @property
    def log_level(self) -> str:
        """Map severity to Python logging level."""
        mapping = {
            Severity.CRITICAL: "CRITICAL",
            Severity.HIGH: "ERROR",
            Severity.MEDIUM: "WARNING",
            Severity.LOW: "INFO",
        }
        return mapping[self]


class Category(Enum):
    """Error categories.

    Groups errors by their domain for easier filtering and handling.
    """

    VALIDATION = "validation"
    RUNTIME = "runtime"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    AGENT = "agent"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value


class Recoverability(Enum):
    """Error recoverability levels.

    Indicates whether an error can be automatically recovered from,
    requires manual intervention, or is fatal.
    """

    RECOVERABLE = "recoverable"
    MANUAL_INTERVENTION = "manual_intervention"
    FATAL = "fatal"

    def __str__(self) -> str:
        return self.value

    @property
    def should_retry(self) -> bool:
        """Whether the operation should be retried."""
        return self == Recoverability.RECOVERABLE


@dataclass
class ErrorContext:
    """Complete context for a classified error.

    Contains all information needed for error handling, logging,
    and remediation.

    Attributes:
        error_type: The class name of the error
        error_code: Machine-parseable error code
        severity: How severe the error is
        category: What domain the error belongs to
        recoverability: Whether the error can be recovered from
        message: Human-readable error description
        remediation: List of steps to fix the error
        documentation_url: Link to relevant documentation
        details: Additional context from the original error
        original_error: The original exception instance
    """

    error_type: str
    error_code: str
    severity: Severity
    category: Category
    recoverability: Recoverability
    message: str
    remediation: list[str] = field(default_factory=list)
    documentation_url: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    original_error: LatticeError | Exception | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "error_type": self.error_type,
            "error_code": self.error_code,
            "severity": str(self.severity),
            "category": str(self.category),
            "recoverability": str(self.recoverability),
            "message": self.message,
            "remediation": self.remediation,
            "documentation_url": self.documentation_url,
            "details": self.details,
        }


ERROR_CLASSIFICATION: dict[type[Exception], tuple[Severity, Category, Recoverability]] = {
    SchemaValidationError: (Severity.HIGH, Category.VALIDATION, Recoverability.MANUAL_INTERVENTION),
    SheriffViolationError: (Severity.HIGH, Category.VALIDATION, Recoverability.MANUAL_INTERVENTION),
    GauntletFailureError: (Severity.MEDIUM, Category.VALIDATION, Recoverability.MANUAL_INTERVENTION),
    LatticeRuntimeError: (Severity.MEDIUM, Category.RUNTIME, Recoverability.RECOVERABLE),
    ConfigurationError: (Severity.HIGH, Category.CONFIGURATION, Recoverability.MANUAL_INTERVENTION),
    NetworkError: (Severity.MEDIUM, Category.NETWORK, Recoverability.RECOVERABLE),
    AgentError: (Severity.MEDIUM, Category.AGENT, Recoverability.RECOVERABLE),
    LatticeError: (Severity.MEDIUM, Category.UNKNOWN, Recoverability.MANUAL_INTERVENTION),
}


def classify_error(error: Exception) -> ErrorContext:
    """Classify an error and return its full context.

    Determines the severity, category, and recoverability of an error
    based on its type. Also generates remediation steps.

    Args:
        error: The exception to classify

    Returns:
        ErrorContext with full classification and remediation information
    """
    from lattice_lock.errors.remediation import get_remediation

    error_type = type(error).__name__
    error_code = getattr(error, "error_code", "LL-000")
    message = str(error)
    details = getattr(error, "details", {}) if hasattr(error, "details") else {}

    severity, category, recoverability = _get_classification(error)
    remediation_info = get_remediation(error)

    return ErrorContext(
        error_type=error_type,
        error_code=error_code,
        severity=severity,
        category=category,
        recoverability=recoverability,
        message=message,
        remediation=remediation_info.steps,
        documentation_url=remediation_info.documentation_url,
        details=details,
        original_error=error,
    )


def _get_classification(error: Exception) -> tuple[Severity, Category, Recoverability]:
    """Get classification tuple for an error.

    Looks up the error type in the classification mapping.
    Falls back to base LatticeError classification if not found.
    """
    for error_class, classification in ERROR_CLASSIFICATION.items():
        if isinstance(error, error_class):
            return classification

    return (Severity.MEDIUM, Category.UNKNOWN, Recoverability.MANUAL_INTERVENTION)


def get_severity(error: Exception) -> Severity:
    """Get the severity level for an error."""
    severity, _, _ = _get_classification(error)
    return severity


def get_category(error: Exception) -> Category:
    """Get the category for an error."""
    _, category, _ = _get_classification(error)
    return category


def get_recoverability(error: Exception) -> Recoverability:
    """Get the recoverability level for an error."""
    _, _, recoverability = _get_classification(error)
    return recoverability
