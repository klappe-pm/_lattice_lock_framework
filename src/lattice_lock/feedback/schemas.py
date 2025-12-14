"""
Feedback Data Schemas

Defines the data models for the feedback collection system.
"""

from typing import Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

class FeedbackCategory(str, Enum):
    """Categories for feedback items."""
    BUG = "bug"
    FEATURE = "feature"
    QUALITY = "quality"
    METRIC = "metric"
    OTHER = "other"

class FeedbackPriority(str, Enum):
    """Priority levels for feedback."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FeedbackItem(BaseModel):
    """
    Represents a single piece of feedback.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    category: FeedbackCategory
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    source: str = Field(..., description="Source of the feedback (e.g., 'user', 'agent:prompt_architect')")
    content: str = Field(..., description="The main content of the feedback")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or data")

    model_config = ConfigDict(frozen=True)
