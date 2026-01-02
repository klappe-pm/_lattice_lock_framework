"""
Core types for the Consensus Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VoteStrategy(str, Enum):
    """Strategy for determining consensus."""

    MAJORITY = "majority"
    UNANIMOUS = "unanimous"
    WEIGHTED = "weighted"
    HIERARCHICAL = "hierarchical"


@dataclass
class ConsensusRequest:
    """Request to reach consensus among multiple model outputs."""

    task: str
    candidates: list[str]
    context: dict[str, Any] | None = field(default_factory=dict)
    stance: str | None = None  # Stance steering (e.g., "aggressive", "conservative")
    # Voting strategy defaults to MAJORITY
    strategy: VoteStrategy = VoteStrategy.MAJORITY
