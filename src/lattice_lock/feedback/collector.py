import asyncio
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .schemas import FeedbackCategory, FeedbackItem, FeedbackPriority

logger = logging.getLogger(__name__)




class FeedbackCollector:
    """
    Collects and manages feedback items, persisting them to a JSON file.
    
    All public methods are synchronous for ease of use. Async internals
    are used for I/O operations but wrapped for sync access.
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
        Ensure the storage directory exists and initialize the storage file.
        
        Creates parent directories for the configured storage path if missing and
        creates the storage file containing an empty JSON array ("[]") when the file
        does not already exist.
        """
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # Create empty file if it doesn't exist
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")

    def _load_feedback_sync(self) -> list[FeedbackItem]:
        """
        Load stored feedback items from the JSON storage file.
        
        Invalid feedback entries in the file are skipped; if the storage file is missing, empty, or contains invalid JSON, an empty list is returned.
        
        Returns:
            list[FeedbackItem]: Parsed feedback items; empty list if none could be loaded.
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
        Persist the given feedback items to the collector's storage file as a JSON array.
        
        The items are serialized and written to the configured storage path; any error during serialization or file write is logged and propagated.
        
        Parameters:
            items (list[FeedbackItem]): Feedback items to persist.
        
        Raises:
            Exception: Propagates any exception that occurs during serialization or file writing.
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
        Create and persist a new feedback item and return its identifier.
        
        Parameters:
            content (str): The textual feedback content.
            category (FeedbackCategory): Category for the feedback; defaults to FeedbackCategory.OTHER.
            priority (FeedbackPriority): Priority level for the feedback; defaults to FeedbackPriority.MEDIUM.
            source (str): Origin of the feedback (e.g., "user"); defaults to "user".
            metadata (dict | None): Optional additional data to store with the feedback.
        
        Returns:
            feedback_id (str): ID of the created feedback item.
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
        Retrieve a specific feedback item by ID.
        
        Returns:
            The matching FeedbackItem, or None if no item has the given id.
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
        Return feedback items, optionally filtered by category and/or source.
        
        Both filters are applied together when provided (logical AND). If a filter is None, it is not applied.
        
        Parameters:
            category (FeedbackCategory | None): If provided, only include items whose `category` equals this value.
            source (str | None): If provided, only include items whose `source` equals this value.
        
        Returns:
            list[FeedbackItem]: Feedback items that match the given filters.
        """
        items = self._load_feedback_sync()
        filtered = items

        if category:
            filtered = [i for i in filtered if i.category == category]

        if source:
            filtered = [i for i in filtered if i.source == source]

        return filtered

    def clear(self) -> None:
        """
        Remove all stored feedback items and persist an empty collection to storage.
        
        Primarily intended for use in tests.
        """
        self._save_feedback_sync([])