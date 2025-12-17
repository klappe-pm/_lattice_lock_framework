"""
Tests for the Lattice Lock error handling middleware.

Tests error boundary decorator, logging, recovery actions, and telemetry.
"""

import logging
import os
import pytest
from unittest.mock import MagicMock, patch

from lattice_lock.errors import (
    LatticeError,
    NetworkError,
    ConfigurationError,
    LatticeRuntimeError,
    Severity,
    ErrorContext,
    ErrorMetrics,
    RetryConfig,
    ErrorHandler,
    error_boundary,
    handle_errors,
    with_graceful_degradation,
    get_metrics,
    reset_metrics,
    format_error_report,
    classify_error,
)


class TestErrorMetrics:
    """Tests for ErrorMetrics class."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_error_increments_count(self) -> None:
        """Test that recording an error increments the count."""
        metrics = ErrorMetrics()
        error = NetworkError("Test error")
        context = classify_error(error)

        metrics.record_error(context)

        assert metrics.error_counts["NetworkError"] == 1

    def test_record_multiple_errors(self) -> None:
        """Test recording multiple errors of the same type."""
        metrics = ErrorMetrics()
        error = NetworkError("Test error")
        context = classify_error(error)

        metrics.record_error(context)
        metrics.record_error(context)
        metrics.record_error(context)

        assert metrics.error_counts["NetworkError"] == 3

    def test_record_different_error_types(self) -> None:
        """Test recording different error types."""
        metrics = ErrorMetrics()

        metrics.record_error(classify_error(NetworkError("Net error")))
        metrics.record_error(classify_error(ConfigurationError("Config error")))

        assert metrics.error_counts["NetworkError"] == 1
        assert metrics.error_counts["ConfigurationError"] == 1

    def test_should_alert_based_on_threshold(self) -> None:
        """Test alert threshold checking."""
        metrics = ErrorMetrics()
        metrics.alert_thresholds["high"] = 2

        error = ConfigurationError("Test")
        context = classify_error(error)

        metrics.record_error(context)
        assert metrics.should_alert(context) is False

        metrics.record_error(context)
        assert metrics.should_alert(context) is True

    def test_get_summary(self) -> None:
        """Test getting metrics summary."""
        metrics = ErrorMetrics()
        metrics.record_error(classify_error(NetworkError("Error 1")))
        metrics.record_error(classify_error(NetworkError("Error 2")))

        summary = metrics.get_summary()

        assert summary["total_errors"] == 2
        assert "NetworkError" in summary["error_counts"]


class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_default_config(self) -> None:
        """Test default retry configuration."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0
        assert config.exponential_backoff is True

    def test_get_delay_exponential(self) -> None:
        """Test exponential backoff delay calculation."""
        config = RetryConfig(base_delay=1.0, exponential_backoff=True, jitter=False)

        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0

    def test_get_delay_linear(self) -> None:
        """Test linear delay calculation."""
        config = RetryConfig(base_delay=2.0, exponential_backoff=False, jitter=False)

        assert config.get_delay(0) == 2.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 2.0

    def test_get_delay_respects_max(self) -> None:
        """Test that delay respects maximum."""
        config = RetryConfig(base_delay=1.0, max_delay=5.0, jitter=False)

        assert config.get_delay(10) == 5.0

    def test_get_delay_with_jitter(self) -> None:
        """Test that jitter adds randomness."""
        config = RetryConfig(base_delay=1.0, jitter=True)

        delays = [config.get_delay(0) for _ in range(10)]
        assert len(set(delays)) > 1


class TestErrorBoundaryDecorator:
    """Tests for error_boundary decorator."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        reset_metrics()

    def test_successful_function_returns_normally(self) -> None:
        """Test that successful functions return normally."""

        @error_boundary()
        def successful_func() -> str:
            return "success"

        assert successful_func() == "success"

    def test_error_is_raised_without_retry(self) -> None:
        """Test that errors are raised when not recoverable."""

        @error_boundary()
        def failing_func() -> None:
            raise ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            failing_func()

    def test_retry_on_recoverable_error(self) -> None:
        """Test retry behavior on recoverable errors."""
        call_count = 0

        @error_boundary(
            recoverable_errors=[NetworkError],
            retry_config=RetryConfig(max_retries=2, base_delay=0.01),
        )
        def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Temporary failure")
            return "success"

        result = flaky_func()

        assert result == "success"
        assert call_count == 3

    def test_fallback_on_exhausted_retries(self) -> None:
        """Test fallback when retries are exhausted."""

        @error_boundary(
            recoverable_errors=[NetworkError],
            retry_config=RetryConfig(max_retries=2, base_delay=0.01),
            fallback=lambda: "fallback_value",
        )
        def always_fails() -> str:
            raise NetworkError("Always fails")

        result = always_fails()

        assert result == "fallback_value"

    def test_on_error_callback_called(self) -> None:
        """Test that on_error callback is called."""
        callback = MagicMock()

        @error_boundary(on_error=callback)
        def failing_func() -> None:
            raise LatticeError("Test error")

        with pytest.raises(LatticeError):
            failing_func()

        callback.assert_called_once()
        context = callback.call_args[0][0]
        assert isinstance(context, ErrorContext)

    def test_metrics_tracked(self) -> None:
        """Test that error metrics are tracked."""

        @error_boundary(track_metrics=True)
        def failing_func() -> None:
            raise NetworkError("Test error")

        with pytest.raises(NetworkError):
            failing_func()

        metrics = get_metrics()
        assert metrics.error_counts.get("NetworkError", 0) >= 1


class TestHandleErrorsDecorator:
    """Tests for handle_errors decorator."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        reset_metrics()

    def test_successful_function_returns_normally(self) -> None:
        """Test that successful functions return normally."""

        @handle_errors()
        def successful_func() -> str:
            return "success"

        assert successful_func() == "success"

    def test_error_is_reraised_by_default(self) -> None:
        """Test that errors are re-raised by default."""

        @handle_errors()
        def failing_func() -> None:
            raise LatticeError("Test error")

        with pytest.raises(LatticeError):
            failing_func()

    def test_error_suppressed_when_reraise_false(self) -> None:
        """Test that errors are suppressed when reraise=False."""

        @handle_errors(reraise=False)
        def failing_func() -> str:
            raise LatticeError("Test error")

        result = failing_func()

        assert result is None

    def test_metrics_tracked(self) -> None:
        """Test that error metrics are tracked."""

        @handle_errors(track_metrics=True)
        def failing_func() -> None:
            raise ConfigurationError("Test error")

        with pytest.raises(ConfigurationError):
            failing_func()

        metrics = get_metrics()
        assert metrics.error_counts.get("ConfigurationError", 0) >= 1


class TestErrorHandlerContextManager:
    """Tests for ErrorHandler context manager."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        reset_metrics()

    def test_no_error_context(self) -> None:
        """Test context manager with no error."""
        with ErrorHandler() as handler:
            pass

        assert handler.error is None
        assert handler.context is None

    def test_error_captured(self) -> None:
        """Test that errors are captured."""
        with pytest.raises(LatticeError):
            with ErrorHandler() as handler:
                raise LatticeError("Test error")

        assert handler.error is not None
        assert handler.context is not None
        assert handler.context.error_type == "LatticeError"

    def test_error_suppressed(self) -> None:
        """Test that errors can be suppressed."""
        with ErrorHandler(suppress=True) as handler:
            raise LatticeError("Test error")

        assert handler.error is not None
        assert handler.context is not None

    def test_on_error_callback(self) -> None:
        """Test on_error callback is called."""
        callback = MagicMock()

        with pytest.raises(LatticeError):
            with ErrorHandler(on_error=callback) as handler:
                raise LatticeError("Test error")

        callback.assert_called_once()


class TestGracefulDegradation:
    """Tests for with_graceful_degradation decorator."""

    def test_returns_fallback_on_error(self) -> None:
        """Test that fallback value is returned on error."""

        @with_graceful_degradation(fallback_value="default")
        def failing_func() -> str:
            raise LatticeError("Test error")

        result = failing_func()

        assert result == "default"

    def test_returns_normal_value_on_success(self) -> None:
        """Test that normal value is returned on success."""

        @with_graceful_degradation(fallback_value="default")
        def successful_func() -> str:
            return "success"

        result = successful_func()

        assert result == "success"

    def test_only_catches_specified_errors(self) -> None:
        """Test that only specified error types are caught."""

        @with_graceful_degradation(
            fallback_value="default",
            error_types=[NetworkError],
        )
        def failing_func() -> str:
            raise ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            failing_func()


class TestFormatErrorReport:
    """Tests for format_error_report function."""

    def test_report_contains_error_info(self) -> None:
        """Test that report contains error information."""
        error = NetworkError("Connection failed", url="https://api.example.com")
        context = classify_error(error)

        report = format_error_report(context)

        assert "NetworkError" in report
        assert "LL-600" in report
        assert "Connection failed" in report

    def test_report_contains_remediation(self) -> None:
        """Test that report contains remediation steps."""
        error = ConfigurationError("Missing key", config_key="API_KEY")
        context = classify_error(error)

        report = format_error_report(context)

        assert "Remediation Steps:" in report
        assert "1." in report

    def test_report_contains_documentation_url(self) -> None:
        """Test that report contains documentation URL."""
        error = NetworkError("Failed")
        context = classify_error(error)

        report = format_error_report(context)

        assert "Documentation:" in report


class TestGlobalMetrics:
    """Tests for global metrics functions."""

    def test_get_metrics_returns_instance(self) -> None:
        """Test that get_metrics returns an ErrorMetrics instance."""
        metrics = get_metrics()
        assert isinstance(metrics, ErrorMetrics)

    def test_reset_metrics_clears_data(self) -> None:
        """Test that reset_metrics clears all data."""
        metrics = get_metrics()
        metrics.record_error(classify_error(NetworkError("Test")))

        reset_metrics()

        new_metrics = get_metrics()
        assert new_metrics.error_counts == {}


class TestLoggingIntegration:
    """Tests for logging integration."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        reset_metrics()

    def test_error_logged_with_correct_level(self) -> None:
        """Test that errors are logged with correct level."""
        with patch("lattice_lock.errors.middleware.logger") as mock_logger:

            @handle_errors(log_errors=True)
            def failing_func() -> None:
                raise NetworkError("Test error")

            with pytest.raises(NetworkError):
                failing_func()

            mock_logger.log.assert_called()

    def test_sensitive_data_redacted(self) -> None:
        """Test that sensitive data is redacted in logs."""
        from lattice_lock.errors.middleware import _redact_sensitive

        data = {
            "api_key": os.getenv("TEST_SENSITIVE_API_KEY", "dummy_redaction_test_key"),
            "password": os.getenv("TEST_SENSITIVE_PASSWORD", "dummy_redaction_test_password"),
            "username": "testuser",
            "nested": {
                "token": os.getenv("TEST_SENSITIVE_TOKEN", "dummy_redaction_test_token"),
            },
        }

        redacted = _redact_sensitive(data)

        assert redacted["api_key"] == "[REDACTED]"
        assert redacted["password"] == "[REDACTED]"
        assert redacted["username"] == "testuser"
        assert redacted["nested"]["token"] == "[REDACTED]"
