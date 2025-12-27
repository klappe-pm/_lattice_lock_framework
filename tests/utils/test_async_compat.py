"""Tests for async compatibility utilities."""

import asyncio

import pytest
from lattice_lock.exceptions import BackgroundTaskError
from lattice_lock.utils.async_compat import (
    BackgroundTaskQueue,
    get_background_queue,
    reset_background_queue,
)


class TestBackgroundTaskQueue:
    """Tests for BackgroundTaskQueue."""

    @pytest.fixture(autouse=True)
    def reset_queue(self):
        """Reset queue before each test."""
        reset_background_queue()
        yield
        reset_background_queue()

    @pytest.mark.asyncio
    async def test_enqueue_and_wait(self):
        """Test basic enqueue and wait functionality."""
        queue = BackgroundTaskQueue()
        results = []

        async def task(value: int):
            await asyncio.sleep(0.01)
            results.append(value)

        queue.enqueue(task(1))
        queue.enqueue(task(2))
        queue.enqueue(task(3))

        assert queue.pending_count() == 3

        await queue.wait_all(timeout=5.0)

        assert sorted(results) == [1, 2, 3]
        assert queue.pending_count() == 0

    @pytest.mark.asyncio
    async def test_reject_after_shutdown(self):
        """Test that tasks are rejected after shutdown."""
        queue = BackgroundTaskQueue()

        async def dummy():
            pass

        await queue.wait_all()  # This sets _shutdown = True

        with pytest.raises(RuntimeError, match="Cannot enqueue.*shutdown"):
            queue.enqueue(dummy())

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """Test that timeout raises BackgroundTaskError."""
        queue = BackgroundTaskQueue()

        async def slow_task():
            await asyncio.sleep(10)  # Very slow

        queue.enqueue(slow_task())

        with pytest.raises(BackgroundTaskError, match="failed to complete"):
            await queue.wait_all(timeout=0.1)

    @pytest.mark.asyncio
    async def test_reset(self):
        """Test queue reset functionality."""
        queue = BackgroundTaskQueue()
        queue._shutdown = True

        queue.reset()

        assert queue._shutdown is False
        assert len(queue._tasks) == 0

    def test_global_queue_singleton(self):
        """Test global queue is singleton."""
        reset_background_queue()
        q1 = get_background_queue()
        q2 = get_background_queue()
        assert q1 is q2

    @pytest.mark.asyncio
    async def test_empty_wait_succeeds(self):
        """Test wait_all succeeds with no tasks."""
        queue = BackgroundTaskQueue()
        await queue.wait_all()  # Should not raise
        assert queue._shutdown is True

    @pytest.mark.asyncio
    async def test_task_cleanup_on_completion(self):
        """Test tasks are removed from tracking on completion."""
        queue = BackgroundTaskQueue()

        async def quick_task():
            return "done"

        queue.enqueue(quick_task())
        assert queue.pending_count() == 1

        # Wait a bit for task to complete
        await asyncio.sleep(0.05)

        # Task should self-cleanup
        assert queue.pending_count() == 0
