from typing import Dict, List, Optional
import time
from .metrics import MetricsCollector, MetricsSnapshot

class DataAggregator:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.projects: Dict[str, Dict] = {}
        self._last_update = 0.0

    def update_project_status(self, project_id: str, status: str, details: Optional[Dict] = None):
        """Update the status of a specific project."""
        self.projects[project_id] = {
            "id": project_id,
            "status": status,
            "last_updated": time.time(),
            "details": details or {}
        }
        self._last_update = time.time()
        
        # Update metrics based on status
        success = status == "healthy" or status == "valid"
        # Simulate duration for now as we don't have it passed in yet
        self.metrics.record_validation(success, 0.1, error_type=None if success else "validation_error")

    def get_project_summary(self) -> Dict:
        """Get a summary of all projects."""
        total = len(self.projects)
        healthy = len([p for p in self.projects.values() if p["status"] in ["healthy", "valid"]])
        
        return {
            "total_projects": total,
            "healthy_projects": healthy,
            "at_risk_projects": total - healthy,
            "last_update": self._last_update
        }

    def get_all_projects(self) -> List[Dict]:
        return list(self.projects.values())

    def get_metrics(self) -> MetricsSnapshot:
        return self.metrics.get_snapshot()
