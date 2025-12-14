
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class UsageRecord:
    """Record of a single LLM usage event."""
    timestamp: datetime
    session_id: str
    trace_id: str
    model_id: str
    provider: str
    task_type: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "model_id": self.model_id,
            "provider": self.provider,
            "task_type": self.task_type,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "metadata": self.metadata
        }
