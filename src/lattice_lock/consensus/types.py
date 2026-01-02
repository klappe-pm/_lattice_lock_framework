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


class StanceStrength(str, Enum):
    """Strength of the stance application."""

    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass
class ConsensusRequest:
    """Request to reach consensus among multiple model outputs."""

    task: str
    candidates: list[str]
    context: dict[str, Any] | None = field(default_factory=dict)
    stance: str | None = None  # Stance steering (e.g., "aggressive", "conservative")
    # Voting strategy defaults to MAJORITY
    strategy: VoteStrategy = VoteStrategy.MAJORITY
    rounds: int = 1  # Multi-round debate support
    strength: StanceStrength = StanceStrength.MODERATE
