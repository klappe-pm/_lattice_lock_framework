"""Tests for error middleware."""

import pytest
from lattice_lock.errors.classification import Category, ErrorContext, Recoverability, Severity
from lattice_lock.errors.middleware import (
    ErrorMetrics,
    RetryConfig,
    error_boundary,
    get_metrics,
    reset_metrics,
)


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_backoff=True, max_delay=60.0, jitter=False)

        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0
        assert config.get_delay(3) == 8.0

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(base_delay=1.0, exponential_backoff=True, max_delay=10.0, jitter=False)

        assert config.get_delay(10) == 10.0  # Would be 1024 without cap

    def test_linear_backoff(self):
        """Test linear (non-exponential) backoff."""
        config = RetryConfig(base_delay=2.0, exponential_backoff=False, jitter=False)

        assert config.get_delay(0) == 2.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(5) == 2.0


class TestErrorBoundary:
    """Tests for error_boundary decorator."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_metrics()
        yield
        reset_metrics()

    @pytest.mark.asyncio
    async def test_async_success(self):
        """Test async function succeeds without error."""

        @error_boundary()
        async def success():
            return "ok"

        result = await success()
        assert result == "ok"

    def test_sync_success(self):
        """Test sync function succeeds without error."""

        @error_boundary()
        def success():
            return "ok"

        result = success()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_async_error_tracked(self):
        """Test async errors are tracked in metrics."""

        @error_boundary(log_errors=False, track_metrics=True)
        async def fail():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await fail()

        metrics = get_metrics()
        assert metrics.error_counts.get("ValueError") == 1


class TestErrorMetrics:
    """Tests for ErrorMetrics."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_metrics()
        yield
        reset_metrics()

    def test_record_error(self):
        """Test error recording."""

        metrics = ErrorMetrics()
        context = ErrorContext(
            error_type="TestError",
            error_code="LL-TEST",
            message="test",
            severity=Severity.MEDIUM,
            category=Category.UNKNOWN,
            recoverability=Recoverability.MANUAL_INTERVENTION,
        )

        metrics.record_error(context)

        assert metrics.error_counts["TestError"] == 1

    def test_error_rate_calculation(self):
        """Test error rate is calculated correctly."""

        metrics = ErrorMetrics()
        context = ErrorContext(
            error_type="RateTest",
            error_code="LL-RATE",
            message="test",
            severity=Severity.LOW,
            category=Category.UNKNOWN,
            recoverability=Recoverability.MANUAL_INTERVENTION,
        )

        for _ in range(5):
            metrics.record_error(context)

        assert metrics.error_rates["RateTest"] == 5

    def test_get_summary(self):
        """Test metrics summary."""

        metrics = ErrorMetrics()
        context = ErrorContext(
            error_type="SummaryTest",
            error_code="LL-SUM",
            message="test",
            severity=Severity.LOW,
            category=Category.UNKNOWN,
            recoverability=Recoverability.MANUAL_INTERVENTION,
        )

        metrics.record_error(context)
        metrics.record_error(context)

        summary = metrics.get_summary()
        assert summary["total_errors"] == 2
        assert summary["error_counts"]["SummaryTest"] == 2
