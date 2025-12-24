import asyncio
import aiofiles
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .schemas import FeedbackCategory, FeedbackItem, FeedbackPriority

logger = logging.getLogger(__name__)

class FeedbackCollector:
    """
    Collects and manages feedback items, persisting them to a JSON file.
    """

    def __init__(self, storage_path: Path):
        """
        Initialize the FeedbackCollector.

        Args:
            storage_path: Path to the JSON file where feedback will be stored.
        """
        self.storage_path = storage_path
        # We can't really do async init well, so we preserve sync dir creation 
        # but the submit/list will handle the file existence.
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def _load_feedback(self) -> list[FeedbackItem]:
        """Load feedback items from storage asynchronously."""
        try:
            if not self.storage_path.exists():
                return []

            async with aiofiles.open(self.storage_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
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

    async def _save_feedback(self, items: list[FeedbackItem]) -> None:
        """Save feedback items to storage asynchronously."""
        try:
            data = [item.model_dump(mode="json") for item in items]
            json_str = json.dumps(data, indent=2, default=str)
            async with aiofiles.open(self.storage_path, mode="w", encoding="utf-8") as f:
                await f.write(json_str)
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise

    async def submit(
        self,
        content: str,
        category: FeedbackCategory = FeedbackCategory.OTHER,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        source: str = "user",
        metadata: dict | None = None,
    ) -> str:
        """
        Submit a new piece of feedback.
        """
        item = FeedbackItem(
            content=content,
            category=category,
            priority=priority,
            source=source,
            metadata=metadata or {},
        )

        items = await self._load_feedback()
        items.append(item)
        await self._save_feedback(items)

        logger.info(f"Feedback submitted: {item.id} [{category}]")
        return item.id

    async def get(self, feedback_id: str) -> FeedbackItem | None:
        """
        Retrieve a specific feedback item by ID.
        """
        items = await self._load_feedback()
        for item in items:
            if item.id == feedback_id:
                return item
        return None

    async def list_feedback(
        self, category: FeedbackCategory | None = None, source: str | None = None
    ) -> list[FeedbackItem]:
        """
        List feedback items, optionally filtered.
        """
        items = await self._load_feedback()
        filtered = items

        if category:
            filtered = [i for i in filtered if i.category == category]

        if source:
            filtered = [i for i in filtered if i.source == source]

        return filtered

    async def clear(self) -> None:
        """Clear all feedback (primarily for testing)."""
        await self._save_feedback([])
