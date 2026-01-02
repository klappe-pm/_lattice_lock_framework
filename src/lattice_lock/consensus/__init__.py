"""
Consensus Engine Module.

Provides mechanisms for multi-model consensus and result synthesis.
"""

from .engine import ConsensusEngine
from .types import ConsensusRequest, VoteStrategy

__all__ = ["ConsensusEngine", "ConsensusRequest", "VoteStrategy"]
