import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class FeedbackCollector:
    """Collects and stores user feedback."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the feedback collector.
        
        Args:
            storage_path: Path to the JSON file where feedback is stored.
                          Defaults to ~/.lattice/feedback.json.
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".lattice" / "feedback.json"
            
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensure storage directory and file exist."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True)
            
        if not self.storage_path.exists():
            self._save_feedback([])

    def _load_feedback(self) -> List[Dict[str, Any]]:
        """Load feedback from storage."""
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_feedback(self, feedback: List[Dict[str, Any]]):
        """Save feedback to storage."""
        with open(self.storage_path, "w") as f:
            json.dump(feedback, f, indent=2)

    def submit_feedback(self, rating: int, comment: str, category: str = "general") -> Dict[str, Any]:
        """
        Submit new feedback.
        
        Args:
            rating: Integer rating (1-5)
            comment: Text comment
            category: Category of feedback (e.g., 'bug', 'feature', 'general')
            
        Returns:
            The submitted feedback entry
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
            
        entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "comment": comment,
            "category": category
        }
        
        feedback_list = self._load_feedback()
        feedback_list.append(entry)
        self._save_feedback(feedback_list)
        
        return entry

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of feedback."""
        feedback_list = self._load_feedback()
        total = len(feedback_list)
        
        if total == 0:
            return {
                "total": 0,
                "average_rating": 0.0,
                "categories": {}
            }
            
        total_rating = sum(f["rating"] for f in feedback_list)
        categories = {}
        for f in feedback_list:
            cat = f.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
            
        return {
            "total": total,
            "average_rating": round(total_rating / total, 2),
            "categories": categories
        }
