"""
Async Compatibility Utilities.

Provides utilities for async/sync interoperability, background tasks,
and error boundary decorators.
"""

import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class BackgroundTaskQueue:
    """Queue for managing background tasks with graceful shutdown.
    
    Provides a way to enqueue background tasks that will be awaited
    during application shutdown.
    """
    
    _instance: "BackgroundTaskQueue | None" = None
    
    def __init__(self, max_workers: int = 4) -> None:
        self._tasks: set[asyncio.Task] = set()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = asyncio.Lock()
    
    @classmethod
    def get_instance(cls) -> "BackgroundTaskQueue":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        if cls._instance is not None:
            cls._instance._executor.shutdown(wait=False)
        cls._instance = None
    
    async def enqueue(self, coro: Awaitable[T]) -> asyncio.Task[T]:
        """Add a coroutine to the background queue.
        
        Args:
            coro: The coroutine to run in the background.
            
        Returns:
            The created task.
        """
        task = asyncio.create_task(self._wrap_task(coro))
        async with self._lock:
            self._tasks.add(task)
            task.add_done_callback(lambda t: asyncio.create_task(self._remove_task(t)))
        return task
    
    async def _wrap_task(self, coro: Awaitable[T]) -> T:
        """Wrap task with error logging."""
        try:
            return await coro
        except Exception as e:
            logger.error(f"Background task failed: {e}")
            raise
    
    async def _remove_task(self, task: asyncio.Task) -> None:
        """Remove completed task from set."""
        async with self._lock:
            self._tasks.discard(task)
    
    async def wait_all(self, timeout: float | None = None) -> None:
        """Wait for all background tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds.
        """
        async with self._lock:
            tasks = list(self._tasks)
        
        if tasks:
            await asyncio.wait(tasks, timeout=timeout)
    
    @property
    def pending_count(self) -> int:
        """Number of pending background tasks."""
        return len(self._tasks)


def get_background_queue() -> BackgroundTaskQueue:
    """Get the global background task queue."""
    return BackgroundTaskQueue.get_instance()


def error_boundary(
    *,
    retries: int = 0,
    on_error: Callable[[Exception], Any] | None = None,
    default: T | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for unified sync/async error handling.
    
    Provides retry logic and error recovery for both sync and async functions.
    
    Args:
        retries: Number of retry attempts (0 = no retries).
        on_error: Optional callback for error handling.
        default: Default value to return on error.
        
    Returns:
        Decorated function with error handling.
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_error: Exception | None = None
                for attempt in range(retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        if on_error:
                            on_error(e)
                        if attempt < retries:
                            await asyncio.sleep(0.1 * (2 ** attempt))
                            logger.warning(f"Retry {attempt + 1}/{retries} for {func.__name__}")
                
                if default is not None:
                    return default
                raise last_error  # type: ignore
            return async_wrapper  # type: ignore
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_error: Exception | None = None
                for attempt in range(retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        if on_error:
                            on_error(e)
                        if attempt < retries:
                            import time
                            time.sleep(0.1 * (2 ** attempt))
                            logger.warning(f"Retry {attempt + 1}/{retries} for {func.__name__}")
                
                if default is not None:
                    return default
                raise last_error  # type: ignore
            return sync_wrapper  # type: ignore
    return decorator


@asynccontextmanager
async def graceful_shutdown():
    """Context manager for graceful application shutdown.
    
    Ensures all background tasks complete before exiting.
    
    Usage:
        async with graceful_shutdown():
            # Application code
            pass
    """
    try:
        yield
    finally:
        queue = get_background_queue()
        if queue.pending_count > 0:
            logger.info(f"Waiting for {queue.pending_count} background tasks...")
            await queue.wait_all(timeout=10.0)
