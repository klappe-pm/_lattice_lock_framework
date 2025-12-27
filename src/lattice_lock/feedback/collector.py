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
        Initialize the FeedbackCollector.

        Args:
            storage_path: Path to the JSON file where feedback will be stored.
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Ensure the storage directory and file exist."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # Create empty file if it doesn't exist
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")

    def _load_feedback_sync(self) -> list[FeedbackItem]:
        """Load feedback items from storage synchronously."""
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
        """Save feedback items to storage synchronously."""
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
        Submit a new piece of feedback.
        
        Returns:
            The feedback item ID.
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
        List feedback items, optionally filtered.
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
