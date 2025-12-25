"""
Async/Sync compatibility utilities.

Provides background task management with shutdown guarantees.
"""
import asyncio
import logging
from typing import Any, Awaitable, Set

from lattice_lock.exceptions import BackgroundTaskError

logger = logging.getLogger(__name__)


class BackgroundTaskQueue:
    """
    Background task queue with lifecycle management.
    
    Ensures tasks are tracked and can be awaited during shutdown.
    Prevents task submission after shutdown initiated.
    """
    
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()
        self._shutdown = False
    
    def enqueue(self, coro: Awaitable[Any]) -> asyncio.Task | None:
        """
        Enqueue a coroutine for background execution.
        
        Args:
            coro: Coroutine to execute
            
        Returns:
            Task if enqueued, None if no event loop
            
        Raises:
            RuntimeError: If called after shutdown initiated
        """
        if self._shutdown:
            logger.error(f"Task rejected after shutdown: {coro}")
            raise RuntimeError("Cannot enqueue tasks after shutdown initiated")
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No event loop available for background task")
            return None
        
        task = loop.create_task(self._run_with_cleanup(coro))
        self._tasks.add(task)
        return task
    
    async def _run_with_cleanup(self, coro: Awaitable[Any]) -> Any:
        """Run coroutine and remove from tracking on completion."""
        try:
            return await coro
        finally:
            current = asyncio.current_task()
            if current:
                self._tasks.discard(current)
    
    async def wait_all(self, timeout: float = 5.0) -> None:
        """
        Wait for all pending tasks to complete.
        
        Args:
            timeout: Maximum seconds to wait
            
        Raises:
            BackgroundTaskError: If tasks don't complete within timeout
        """
        self._shutdown = True
        
        if not self._tasks:
            return
        
        logger.info(f"Waiting for {len(self._tasks)} background tasks...")
        
        done, pending = await asyncio.wait(
            self._tasks,
            timeout=timeout,
            return_when=asyncio.ALL_COMPLETED,
        )
        
        if pending:
            logger.critical(f"UNFINISHED TASKS: {len(pending)} tasks did not complete")
            for task in pending:
                task.cancel()
            raise BackgroundTaskError(
                f"{len(pending)} background tasks failed to complete within {timeout}s"
            )
        
        logger.info("All background tasks completed")
    
    def pending_count(self) -> int:
        """Get count of pending tasks."""
        return len(self._tasks)
    
    def reset(self) -> None:
        """Reset queue state for testing."""
        self._tasks.clear()
        self._shutdown = False


# Global background queue
_background_queue: BackgroundTaskQueue | None = None


def get_background_queue() -> BackgroundTaskQueue:
    """Get the global background task queue."""
    global _background_queue
    if _background_queue is None:
        _background_queue = BackgroundTaskQueue()
    return _background_queue


def reset_background_queue() -> None:
    """Reset background queue for testing."""
    global _background_queue
    _background_queue = None
