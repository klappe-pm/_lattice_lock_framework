import logging
from datetime import datetime
from typing import Any, Optional

from ..registry import ModelRegistry
from ..types import APIResponse
from .models import UsageRecord
from .storage import CostStorage

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks capabilities usage and estimates costs.
    """

    def __init__(self, registry: ModelRegistry, db_path: Optional[str] = None):
        self.registry = registry
        self.storage = CostStorage(db_path)
        self.current_session_id = datetime.now().strftime("sess_%Y%m%d_%H%M%S")

    def record_transaction(
        self,
        response: APIResponse,
        task_type: str = "general",
        trace_id: str = "unknown",
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Record a transaction and save to storage.
        """
        if not response or not response.model:
            return

        model_id = response.model
        model_caps = self.registry.models.get(model_id)

        input_tokens = response.usage.get("input_tokens", 0)
        output_tokens = response.usage.get("output_tokens", 0)

        cost = 0.0
        if model_caps:
            # Cost is per 1M tokens usually, assumed input/output cost in registry is per 1M
            input_cost = (input_tokens / 1_000_000) * model_caps.input_cost
            output_cost = (output_tokens / 1_000_000) * model_caps.output_cost
            cost = input_cost + output_cost

        record = UsageRecord(
            timestamp=datetime.now(),
            session_id=self.current_session_id,
            trace_id=trace_id,
            model_id=model_id,
            provider=response.provider,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            metadata=metadata or {},
        )

        self.storage.add_record(record)
        logger.debug(f"Recorded transaction: ${cost:.6f} for {model_id}")

    def get_session_cost(self) -> float:
        """Get current session total cost."""
        return self.storage.get_session_total(self.current_session_id)

    def get_report(self, days: int = 30) -> dict[str, Any]:
        """Get aggregated report."""
        return self.storage.get_aggregates(days)
