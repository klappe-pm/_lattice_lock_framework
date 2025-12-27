import asyncio
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .schemas import FeedbackCategory, FeedbackItem, FeedbackPriority

logger = logging.getLogger(__name__)


def _run_sync(coro):
    """
    Execute an awaitable coroutine from synchronous code.
    
    If an asyncio event loop is already running in the current thread, the coroutine is executed in a new thread; otherwise it is run in the current thread. Exceptions raised by the coroutine propagate to the caller.
    
    Parameters:
        coro: An awaitable or coroutine object to execute.
    
    Returns:
        The value returned by the coroutine.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # We're in an async context, create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


class FeedbackCollector:
    """
    Collects and manages feedback items, persisting them to a JSON file.
    
    All public methods are synchronous for ease of use. File I/O is performed
    synchronously using Path.read_text/write_text.
    """

    def __init__(self, storage_path: Path):
        """
        Create a FeedbackCollector that persists feedback to the specified JSON file.
        
        Ensures the storage file and its parent directories exist, creating them and initializing the file with an empty JSON array if necessary.
        
        Parameters:
            storage_path (Path | str): Path to the JSON file used for storing feedback items.
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """
        Ensure the storage directory exists and initialize the storage file with an empty JSON array if missing.
        
        If the storage file does not exist, create parent directories as needed and write "[]" to the file.
        """
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # Create empty file if it doesn't exist
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")

    def _load_feedback_sync(self) -> list[FeedbackItem]:
        """
        Load feedback items from the storage file.
        
        Invalid or unparseable items are skipped (errors are logged). If the storage file is missing, empty, or contains invalid JSON, an empty list is returned.
        
        Returns:
            list[FeedbackItem]: Parsed feedback items present in storage.
        """
        try:
            if not self.storage_path.exists():
                return []

            content = self.storage_path.read_text(encoding="utf-8")
            if not content:
                return []
            data = json.loads(content)

            items = []
            for item_data in data:
                try:
                    items.append(FeedbackItem(**item_data))
                except ValidationError as e:
                    logger.error(f"Failed to parse feedback item: {e}")
                    continue
            return items

        except json.JSONDecodeError:
            logger.error(f"Corrupt feedback file at {self.storage_path}. Returning empty list.")
            return []
        except Exception as e:
            logger.error(f"Error loading feedback: {e}")
            return []

    def _save_feedback_sync(self, items: list[FeedbackItem]) -> None:
        """
        Persist a list of feedback items to the configured storage file as a JSON array.
        
        Parameters:
            items (list[FeedbackItem]): Feedback items to persist; each item will be converted to JSON-compatible data before writing.
        
        Raises:
            Exception: If serialization or writing to the storage file fails.
        """
        try:
            data = [item.model_dump(mode="json") for item in items]
            json_str = json.dumps(data, indent=2, default=str)
            self.storage_path.write_text(json_str, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise

    def submit(
        self,
        content: str,
        category: FeedbackCategory = FeedbackCategory.OTHER,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        source: str = "user",
        metadata: dict | None = None,
    ) -> str:
        """
        Create and persist a new feedback item.
        
        Parameters:
            content (str): Text of the feedback.
            category (FeedbackCategory): Feedback category; defaults to FeedbackCategory.OTHER.
            priority (FeedbackPriority): Feedback priority level; defaults to FeedbackPriority.MEDIUM.
            source (str): Origin of the feedback (for example, "user"); defaults to "user".
            metadata (dict | None): Optional additional metadata to attach to the item.
        
        Returns:
            str: The newly created feedback item's ID.
        """
        item = FeedbackItem(
            content=content,
            category=category,
            priority=priority,
            source=source,
            metadata=metadata or {},
        )

        items = self._load_feedback_sync()
        items.append(item)
        self._save_feedback_sync(items)

        logger.info(f"Feedback submitted: {item.id} [{category}]")
        return item.id

    def get(self, feedback_id: str) -> FeedbackItem | None:
        """
        Retrieve the feedback item with the given ID.
        
        Returns:
            The FeedbackItem with the matching ID, or `None` if no item matches.
        """
        items = self._load_feedback_sync()
        for item in items:
            if item.id == feedback_id:
                return item
        return None

    def list_feedback(
        self, category: FeedbackCategory | None = None, source: str | None = None
    ) -> list[FeedbackItem]:
        """
        Return feedback items stored in the collector, optionally filtered by category and source.
        
        Parameters:
            category (FeedbackCategory | None): If provided, only include items whose category equals this value.
            source (str | None): If provided, only include items whose source equals this value.
        
        Returns:
            list[FeedbackItem]: The list of matching feedback items; empty list if none match.
        """
        items = self._load_feedback_sync()
        filtered = items

        if category:
            filtered = [i for i in filtered if i.category == category]

        if source:
            filtered = [i for i in filtered if i.source == source]

        return filtered

    def clear(self) -> None:
        """Clear all feedback (primarily for testing)."""
        self._save_feedback_sync([])
