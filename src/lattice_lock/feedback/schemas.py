"""
Feedback Data Schemas

Defines the data models for the feedback collection system.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
    source: str = Field(
        ..., description="Source of the feedback (e.g., 'user', 'agent:prompt_architect')"
    )
    content: str = Field(..., description="The main content of the feedback")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context or data")

    model_config = ConfigDict(frozen=True)
