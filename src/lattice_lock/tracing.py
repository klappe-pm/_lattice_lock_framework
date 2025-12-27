"""
Distributed Tracing Support for Lattice Lock Framework.

Provides lightweight tracing infrastructure for correlating requests
across components without requiring external dependencies like OpenTelemetry.

Features:
- Trace ID generation and propagation
- Span tracking for major operations
- Context management for async operations
- Performance timing instrumentation
"""

import asyncio
import contextvars
import functools
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)

_trace_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "trace_context", default={}
)


def asyncio_iscoroutinefunction(func: Any) -> bool:
    """Check if a function is a coroutine function safely."""
    return asyncio.iscoroutinefunction(func)


def generate_trace_id() -> str:
    """Generate a unique trace ID."""
    return uuid.uuid4().hex[:16]


def generate_span_id() -> str:
    """Generate a unique span ID."""
    return uuid.uuid4().hex[:8]


def get_current_trace_id() -> str | None:
    """Get the current trace ID from context."""
    ctx = _trace_context.get()
    return ctx.get("trace_id")


def get_current_span_id() -> str | None:
    """Get the current span ID from context."""
    ctx = _trace_context.get()
    return ctx.get("span_id")


def set_trace_context(trace_id: str, span_id: str | None = None) -> contextvars.Token:
    """
    Set the trace context for the current execution.

    Args:
        trace_id: The trace ID to set
        span_id: Optional span ID to set

    Returns:
        Token that can be used to reset the context
    """
    ctx = {"trace_id": trace_id}
    if span_id:
        ctx["span_id"] = span_id
    return _trace_context.set(ctx)


def reset_trace_context(token: contextvars.Token) -> None:
    """Reset the trace context to its previous value."""
    _trace_context.reset(token)


@dataclass
class Span:
    """Represents a traced operation span."""

    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    error: str | None = None

    def end(self, status: str = "ok", error: str | None = None) -> None:
        """End the span and record its duration."""
        self.end_time = time.time()
        self.status = status
        self.error = error

    @property
    def duration_ms(self) -> float | None:
        """Get the span duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary for logging/export."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": (
                datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None
            ),
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "status": self.status,
            "error": self.error,
        }


class SpanContext:
    """Context manager for creating and managing spans."""

    def __init__(
        self,
        name: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.trace_id = trace_id or get_current_trace_id() or generate_trace_id()
        self.parent_span_id = parent_span_id or get_current_span_id()
        self.span_id = generate_span_id()
        self.attributes = attributes or {}
        self.span: Span | None = None
        self._token: contextvars.Token | None = None

    def __enter__(self) -> Span:
        self.span = Span(
            name=self.name,
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            attributes=self.attributes,
        )
        self._token = set_trace_context(self.trace_id, self.span_id)

        logger.debug(
            f"Starting span: {self.name}",
            extra={
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "parent_span_id": self.parent_span_id,
            },
        )

        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.span:
            if exc_val:
                self.span.end(status="error", error=str(exc_val))
            else:
                self.span.end()

            logger.debug(
                f"Ended span: {self.name} ({self.span.duration_ms:.2f}ms)",
                extra={
                    "trace_id": self.trace_id,
                    "span_id": self.span.span_id,
                    "duration_ms": self.span.duration_ms,
                    "status": self.span.status,
                },
            )

        if self._token:
            reset_trace_context(self._token)

        return False


class AsyncSpanContext:
    """Async context manager for creating and managing spans."""

    def __init__(
        self,
        name: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.trace_id = trace_id or get_current_trace_id() or generate_trace_id()
        self.parent_span_id = parent_span_id or get_current_span_id()
        self.span_id = generate_span_id()
        self.attributes = attributes or {}
        self.span: Span | None = None
        self._token: contextvars.Token | None = None

    async def __aenter__(self) -> Span:
        self.span = Span(
            name=self.name,
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            attributes=self.attributes,
        )
        self._token = set_trace_context(self.trace_id, self.span_id)

        logger.debug(
            f"Starting async span: {self.name}",
            extra={
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "parent_span_id": self.parent_span_id,
            },
        )

        return self.span

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.span:
            if exc_val:
                self.span.end(status="error", error=str(exc_val))
            else:
                self.span.end()

            logger.debug(
                f"Ended async span: {self.name} ({self.span.duration_ms:.2f}ms)",
                extra={
                    "trace_id": self.trace_id,
                    "span_id": self.span.span_id,
                    "duration_ms": self.span.duration_ms,
                    "status": self.span.status,
                },
            )

        if self._token:
            reset_trace_context(self._token)

        return False


def traced(
    name: str | None = None, attributes: dict[str, Any] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to automatically trace function execution.

    Args:
        name: Optional span name (defaults to function name)
        attributes: Optional attributes to add to the span

    Example:
        @traced("process_request")
        def process_request(data: dict) -> dict:
            ...

        @traced()
        async def async_operation():
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        span_name = name or func.__name__

        if asyncio_iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                async with AsyncSpanContext(span_name, attributes=attributes) as span:
                    span.attributes["function"] = func.__name__
                    span.attributes["module"] = func.__module__
                    return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with SpanContext(span_name, attributes=attributes) as span:
                    span.attributes["function"] = func.__name__
                    span.attributes["module"] = func.__module__
                    return func(*args, **kwargs)

            return sync_wrapper

    return decorator


@dataclass
class PerformanceMetrics:
    """Collects performance metrics for monitoring."""

    operation_times: dict[str, list[float]] = field(default_factory=dict)
    operation_counts: dict[str, int] = field(default_factory=dict)
    error_counts: dict[str, int] = field(default_factory=dict)

    def record_operation(self, operation: str, duration_ms: float, success: bool = True) -> None:
        """Record an operation's performance."""
        if operation not in self.operation_times:
            self.operation_times[operation] = []
            self.operation_counts[operation] = 0
            self.error_counts[operation] = 0

        self.operation_times[operation].append(duration_ms)
        self.operation_counts[operation] += 1

        if not success:
            self.error_counts[operation] += 1

        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]

    def get_percentile(self, operation: str, percentile: float) -> float | None:
        """Get a percentile value for an operation's duration."""
        times = self.operation_times.get(operation, [])
        if not times:
            return None

        sorted_times = sorted(times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def get_summary(self, operation: str) -> dict[str, Any] | None:
        """Get a summary of metrics for an operation."""
        times = self.operation_times.get(operation, [])
        if not times:
            return None

        return {
            "operation": operation,
            "count": self.operation_counts.get(operation, 0),
            "error_count": self.error_counts.get(operation, 0),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p50_ms": self.get_percentile(operation, 50),
            "p95_ms": self.get_percentile(operation, 95),
            "p99_ms": self.get_percentile(operation, 99),
        }

    def get_all_summaries(self) -> list[dict[str, Any]]:
        """Get summaries for all operations."""
        summaries = []
        for operation in self.operation_times:
            summary = self.get_summary(operation)
            if summary:
                summaries.append(summary)
        return summaries


_global_metrics = PerformanceMetrics()


def get_performance_metrics() -> PerformanceMetrics:
    """Get the global performance metrics instance."""
    return _global_metrics


def reset_performance_metrics() -> None:
    """Reset global performance metrics (useful for testing)."""
    global _global_metrics
    _global_metrics = PerformanceMetrics()


def timed(operation_name: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to time function execution and record metrics.

    Args:
        operation_name: Optional name for the operation (defaults to function name)

    Example:
        @timed("model_selection")
        def select_model(requirements):
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        op_name = operation_name or func.__name__

        if asyncio_iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                start = time.time()
                success = True
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    success = False
                    raise
                finally:
                    duration_ms = (time.time() - start) * 1000
                    _global_metrics.record_operation(op_name, duration_ms, success)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                start = time.time()
                success = True
                try:
                    return func(*args, **kwargs)
                except Exception:
                    success = False
                    raise
                finally:
                    duration_ms = (time.time() - start) * 1000
                    _global_metrics.record_operation(op_name, duration_ms, success)

            return sync_wrapper

    return decorator
