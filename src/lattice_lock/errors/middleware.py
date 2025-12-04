"""
Lattice Lock Error Handling Middleware

Provides decorators and utilities for consistent error handling across the framework.
Includes error interception, automatic classification, logging, and recovery actions.
"""

import functools
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ParamSpec, TypeVar

from lattice_lock.errors.types import LatticeError
from lattice_lock.errors.classification import (
    Severity,
    Recoverability,
    ErrorContext,
    classify_error,
)
from lattice_lock.errors.remediation import format_remediation


P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("lattice_lock.errors")


@dataclass
class ErrorMetrics:
    """Tracks error metrics for telemetry.

    Attributes:
        error_counts: Count of errors by type
        error_rates: Error rate per minute by type
        last_errors: Timestamps of recent errors for rate calculation
        alert_thresholds: Thresholds for alerting
    """

    error_counts: dict[str, int] = field(default_factory=dict)
    error_rates: dict[str, float] = field(default_factory=dict)
    last_errors: dict[str, list[float]] = field(default_factory=dict)
    alert_thresholds: dict[str, int] = field(default_factory=lambda: {
        "critical": 1,
        "high": 5,
        "medium": 10,
        "low": 50,
    })

    def record_error(self, context: ErrorContext) -> None:
        """Record an error occurrence for metrics."""
        error_type = context.error_type
        current_time = time.time()

        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        if error_type not in self.last_errors:
            self.last_errors[error_type] = []
        self.last_errors[error_type].append(current_time)

        cutoff = current_time - 60
        self.last_errors[error_type] = [
            t for t in self.last_errors[error_type] if t > cutoff
        ]
        self.error_rates[error_type] = len(self.last_errors[error_type])

    def should_alert(self, context: ErrorContext) -> bool:
        """Check if an alert should be triggered based on thresholds."""
        severity_key = str(context.severity)
        threshold = self.alert_thresholds.get(severity_key, 10)
        error_type = context.error_type
        return self.error_counts.get(error_type, 0) >= threshold

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of error metrics."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": dict(self.error_counts),
            "error_rates_per_minute": dict(self.error_rates),
        }


_global_metrics = ErrorMetrics()


def get_metrics() -> ErrorMetrics:
    """Get the global error metrics instance."""
    return _global_metrics


def reset_metrics() -> None:
    """Reset global error metrics (useful for testing)."""
    global _global_metrics
    _global_metrics = ErrorMetrics()


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_backoff: Whether to use exponential backoff
        jitter: Whether to add random jitter to delays
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_backoff: bool = True
    jitter: bool = True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt."""
        import random

        if self.exponential_backoff:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay

        delay = min(delay, self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


def _log_error(context: ErrorContext, include_traceback: bool = True) -> None:
    """Log an error with appropriate level and structured context.

    Args:
        context: The classified error context
        include_traceback: Whether to include stack trace
    """
    log_level = getattr(logging, context.severity.log_level)

    log_data = {
        "error_type": context.error_type,
        "error_code": context.error_code,
        "severity": str(context.severity),
        "category": str(context.category),
        "recoverability": str(context.recoverability),
        "details": _redact_sensitive(context.details),
    }

    message = f"{context.error_code}: {context.message}"

    if include_traceback and context.original_error:
        logger.log(log_level, message, exc_info=context.original_error, extra=log_data)
    else:
        logger.log(log_level, message, extra=log_data)


def _redact_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive information from error details.

    Args:
        data: Dictionary that may contain sensitive values

    Returns:
        Dictionary with sensitive values redacted
    """
    sensitive_keys = {
        "password", "secret", "token", "api_key", "apikey",
        "authorization", "auth", "credential", "private_key",
    }

    result = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = _redact_sensitive(value)
        elif isinstance(value, str) and len(value) > 100:
            result[key] = value[:100] + "...[truncated]"
        else:
            result[key] = value
    return result


def error_boundary(
    recoverable_errors: list[type[Exception]] | None = None,
    on_error: Callable[[ErrorContext], Any] | None = None,
    retry_config: RetryConfig | None = None,
    fallback: Callable[..., R] | None = None,
    log_errors: bool = True,
    track_metrics: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that provides error boundary protection for functions.

    Intercepts exceptions, classifies them, logs them, and optionally
    retries or falls back to alternative behavior.

    Args:
        recoverable_errors: List of error types that should trigger retry
        on_error: Callback function called when an error occurs
        retry_config: Configuration for retry behavior
        fallback: Fallback function to call if all retries fail
        log_errors: Whether to log errors
        track_metrics: Whether to track error metrics

    Returns:
        Decorated function with error boundary protection

    Example:
        @error_boundary(
            recoverable_errors=[NetworkError],
            retry_config=RetryConfig(max_retries=3),
            on_error=handle_network_error,
        )
        def fetch_data(url: str) -> dict:
            ...
    """
    recoverable_errors = recoverable_errors or []
    retry_config = retry_config or RetryConfig(max_retries=0)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_error: Exception | None = None
            attempt = 0

            while attempt <= retry_config.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    context = classify_error(e)

                    if track_metrics:
                        _global_metrics.record_error(context)

                    if log_errors:
                        _log_error(context)

                    if on_error:
                        on_error(context)

                    is_recoverable = any(
                        isinstance(e, err_type) for err_type in recoverable_errors
                    )
                    can_retry = (
                        is_recoverable
                        and context.recoverability.should_retry
                        and attempt < retry_config.max_retries
                    )

                    if can_retry:
                        delay = retry_config.get_delay(attempt)
                        logger.info(
                            f"Retrying {func.__name__} in {delay:.2f}s "
                            f"(attempt {attempt + 1}/{retry_config.max_retries})"
                        )
                        time.sleep(delay)
                        attempt += 1
                    else:
                        break

            if fallback is not None:
                logger.warning(
                    f"Using fallback for {func.__name__} after {attempt} attempts"
                )
                return fallback(*args, **kwargs)

            if last_error is not None:
                raise last_error

            raise RuntimeError("Unexpected state in error boundary")

        return wrapper

    return decorator


def handle_errors(
    log_errors: bool = True,
    track_metrics: bool = True,
    reraise: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Simple decorator for error handling without retry logic.

    Intercepts exceptions, classifies them, logs them, and optionally
    re-raises them.

    Args:
        log_errors: Whether to log errors
        track_metrics: Whether to track error metrics
        reraise: Whether to re-raise the exception after handling

    Returns:
        Decorated function with error handling
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = classify_error(e)

                if track_metrics:
                    _global_metrics.record_error(context)

                if log_errors:
                    _log_error(context)

                if reraise:
                    raise

                return None  # type: ignore

        return wrapper

    return decorator


class ErrorHandler:
    """Context manager for error handling.

    Provides a context manager interface for error handling with
    classification, logging, and optional suppression.

    Example:
        with ErrorHandler(suppress=True) as handler:
            risky_operation()

        if handler.error:
            print(f"Error occurred: {handler.context.message}")
    """

    def __init__(
        self,
        suppress: bool = False,
        log_errors: bool = True,
        track_metrics: bool = True,
        on_error: Callable[[ErrorContext], Any] | None = None,
    ) -> None:
        self.suppress = suppress
        self.log_errors = log_errors
        self.track_metrics = track_metrics
        self.on_error = on_error
        self.error: Exception | None = None
        self.context: ErrorContext | None = None

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        if exc_val is not None and isinstance(exc_val, Exception):
            self.error = exc_val
            self.context = classify_error(exc_val)

            if self.track_metrics:
                _global_metrics.record_error(self.context)

            if self.log_errors:
                _log_error(self.context)

            if self.on_error:
                self.on_error(self.context)

            return self.suppress

        return False


def with_graceful_degradation(
    fallback_value: R,
    error_types: list[type[Exception]] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that provides graceful degradation on errors.

    Returns a fallback value instead of raising an exception for
    specified error types.

    Args:
        fallback_value: Value to return when an error occurs
        error_types: List of error types to catch (None = all)

    Returns:
        Decorated function with graceful degradation
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_types is None or any(
                    isinstance(e, t) for t in error_types
                ):
                    context = classify_error(e)
                    _global_metrics.record_error(context)
                    logger.warning(
                        f"Graceful degradation in {func.__name__}: "
                        f"{context.error_code} - returning fallback value"
                    )
                    return fallback_value
                raise

        return wrapper

    return decorator


def format_error_report(context: ErrorContext) -> str:
    """Format a complete error report for display or logging.

    Args:
        context: The classified error context

    Returns:
        Formatted error report string
    """
    lines = [
        "=" * 60,
        "LATTICE LOCK ERROR REPORT",
        "=" * 60,
        "",
        f"Error Type: {context.error_type}",
        f"Error Code: {context.error_code}",
        f"Severity: {context.severity}",
        f"Category: {context.category}",
        f"Recoverability: {context.recoverability}",
        "",
        "Message:",
        f"  {context.message}",
        "",
    ]

    if context.details:
        lines.append("Details:")
        for key, value in context.details.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    if context.remediation:
        lines.append("Remediation Steps:")
        for i, step in enumerate(context.remediation, 1):
            lines.append(f"  {i}. {step}")
        lines.append("")

    if context.documentation_url:
        lines.append(f"Documentation: {context.documentation_url}")

    lines.append("=" * 60)

    return "\n".join(lines)
