"""
Feedback Collector Module

Handles the collection, storage, and retrieval of feedback items.
"""

import json
import logging
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

from .schemas import FeedbackItem, FeedbackCategory, FeedbackPriority

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
        self._ensure_storage()
    
    def _ensure_storage(self) -> None:
        """Ensure the storage file and directory exist."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.storage_path.exists():
            self._save_feedback([])

    def _load_feedback(self) -> List[FeedbackItem]:
        """Load feedback items from storage."""
        try:
            if not self.storage_path.exists():
                return []
                
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            items = []
            for item_data in data:
                try:
                    # Handle datetime serialization if it was stored as string
                    # Pydantic handles this automatically for valid ISO strings
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

    def _save_feedback(self, items: List[FeedbackItem]) -> None:
        """Save feedback items to storage."""
        try:
            data = [item.model_dump(mode='json') for item in items]
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
            raise

    def submit(
        self,
        content: str,
        category: FeedbackCategory = FeedbackCategory.OTHER,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        source: str = "user",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Submit a new piece of feedback.
        
        Args:
            content: The feedback message.
            category: Category of feedback.
            priority: Priority level.
            source: Source identifier.
            metadata: Optional additional data.
            
        Returns:
            The ID of the created feedback item.
        """
        item = FeedbackItem(
            content=content,
            category=category,
            priority=priority,
            source=source,
            metadata=metadata or {}
        )
        
        items = self._load_feedback()
        items.append(item)
        self._save_feedback(items)
        
        logger.info(f"Feedback submitted: {item.id} [{category}]")
        return item.id

    def get(self, feedback_id: str) -> Optional[FeedbackItem]:
        """
        Retrieve a specific feedback item by ID.
        
        Args:
            feedback_id: The ID to search for.
            
        Returns:
            The FeedbackItem if found, else None.
        """
        items = self._load_feedback()
        for item in items:
            if item.id == feedback_id:
                return item
        return None

    def list_feedback(
        self, 
        category: Optional[FeedbackCategory] = None,
        source: Optional[str] = None
    ) -> List[FeedbackItem]:
        """
        List feedback items, optionally filtered.
        
        Args:
            category: Filter by category.
            source: Filter by source.
            
        Returns:
            List of matching feedback items.
        """
        items = self._load_feedback()
        filtered = items
        
        if category:
            filtered = [i for i in filtered if i.category == category]
            
        if source:
            filtered = [i for i in filtered if i.source == source]
            
        return filtered

    def clear(self) -> None:
        """Clear all feedback (primarily for testing)."""
        self._save_feedback([])
