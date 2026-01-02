"""
Lattice Lock Dashboard Data Aggregator

Collects and aggregates validation status from all projects,
calculates health scores, and caches results for performance.
"""

import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from .metrics import MetricsCollector, MetricsSnapshot, ProjectHealthTrend


@dataclass
class ProjectInfo:
    """Information about a registered project."""

    id: str
    name: str
    status: str  # "healthy", "valid", "warning", "error", "unknown"
    last_updated: float
    health_score: int = 100
    error_count: int = 0
    warning_count: int = 0
    validation_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class DashboardSummary:
    """Summary statistics for the dashboard."""

    total_projects: int
    healthy_projects: int
    at_risk_projects: int
    error_projects: int
    avg_health_score: float
    total_validations: int
    overall_success_rate: float
    last_update: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


class Cache:
    """Simple time-based cache for aggregated data."""

    def __init__(self, ttl_seconds: float = 5.0):
        """
        Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live for cached data in seconds
        """
        self._cache: dict[str, tuple] = {}  # key -> (value, timestamp)
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get cached value if still valid."""
        with self._lock:
            if key not in self._cache:
                return None

            value, timestamp = self._cache[key]
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                return None

            return value

    def set(self, key: str, value: Any) -> None:
        """Set cached value with current timestamp."""
        with self._lock:
            self._cache[key] = (value, time.time())

    def invalidate(self, key: str | None = None) -> None:
        """Invalidate cache entry or entire cache."""
        with self._lock:
            if key is None:
                self._cache.clear()
            elif key in self._cache:
                del self._cache[key]


class DataAggregator:
    """
    Aggregates data from multiple sources for the dashboard.

    Collects validation status from all projects, aggregates error counts
    and trends, calculates health scores, and caches results for performance.
    """

    # Status values that indicate a healthy project
    HEALTHY_STATUSES = {"healthy", "valid", "passing"}
    # Status values that indicate a warning state
    WARNING_STATUSES = {"warning", "degraded"}
    # Status values that indicate an error state
    ERROR_STATUSES = {"error", "failing", "critical"}

    def __init__(self, cache_ttl: float = 5.0):
        """
        Initialize the data aggregator.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.metrics = MetricsCollector()
        self.projects: dict[str, ProjectInfo] = {}
        self._last_update = 0.0
        self._cache = Cache(ttl_seconds=cache_ttl)
        self._lock = threading.Lock()

    def register_project(
        self,
        project_id: str,
        name: str | None = None,
        status: str = "unknown",
        details: dict[str, Any] | None = None,
    ) -> ProjectInfo:
        """
        Register a new project or update existing one.

        Args:
            project_id: Unique project identifier
            name: Human-readable project name
            status: Initial status
            details: Additional project details

        Returns:
            ProjectInfo for the registered project
        """
        with self._lock:
            if project_id in self.projects:
                # Update existing project
                project = self.projects[project_id]
                if name:
                    project.name = name
                if details:
                    project.details.update(details)
            else:
                # Create new project
                project = ProjectInfo(
                    id=project_id,
                    name=name or project_id,
                    status=status,
                    last_updated=time.time(),
                    details=details or {},
                )
                self.projects[project_id] = project

            self._cache.invalidate()
            return project

    def update_project_status(
        self,
        project_id: str,
        status: str,
        details: dict[str, Any] | None = None,
        duration: float = 0.1,
    ) -> ProjectInfo | None:
        """
        Update the status of a specific project.

        Args:
            project_id: Project identifier
            status: New status value
            details: Optional additional details
            duration: Time taken for the operation (for metrics)

        Returns:
            Updated ProjectInfo or None if project not found
        """
        with self._lock:
            if project_id not in self.projects:
                # Auto-register project if not found
                self.projects[project_id] = ProjectInfo(
                    id=project_id,
                    name=project_id,
                    status=status,
                    last_updated=time.time(),
                    details=details or {},
                )

            project = self.projects[project_id]
            _old_status = project.status  # Reserved for status change tracking
            project.status = status
            project.last_updated = time.time()

            if details:
                project.details.update(details)

            # Update counters based on status
            if status in self.ERROR_STATUSES:
                project.error_count += 1
            elif status in self.WARNING_STATUSES:
                project.warning_count += 1

            project.validation_count += 1

            # Calculate health score
            project.health_score = self._calculate_health_score(project)

            self._last_update = time.time()

            # Record in metrics
            success = status in self.HEALTHY_STATUSES
            error_type = None if success else f"status_{status}"
            self.metrics.record_validation(
                success=success,
                duration=duration,
                error_type=error_type,
                project_id=project_id,
            )

            # Invalidate cache on status change
            self._cache.invalidate()

            return project

    def _calculate_health_score(self, project: ProjectInfo) -> int:
        """
        Calculate health score for a project.

        Score is 0-100 based on status, error rate, and recent activity.
        """
        if project.validation_count == 0:
            return 100

        # Base score from current status
        if project.status in self.HEALTHY_STATUSES:
            base_score = 100
        elif project.status in self.WARNING_STATUSES:
            base_score = 70
        elif project.status in self.ERROR_STATUSES:
            base_score = 30
        else:
            base_score = 50

        # Penalty for error ratio
        if project.validation_count > 0:
            error_ratio = project.error_count / project.validation_count
            base_score -= int(error_ratio * 30)

        return max(0, min(100, base_score))

    def get_project(self, project_id: str) -> ProjectInfo | None:
        """Get project information by ID."""
        return self.projects.get(project_id)

    def get_project_summary(self) -> DashboardSummary:
        """
        Get a summary of all projects.

        Returns cached result if available and fresh.
        """
        cache_key = "project_summary"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        with self._lock:
            total = len(self.projects)
            healthy = sum(1 for p in self.projects.values() if p.status in self.HEALTHY_STATUSES)
            error = sum(1 for p in self.projects.values() if p.status in self.ERROR_STATUSES)
            at_risk = total - healthy - error

            avg_health = 0.0
            if self.projects:
                avg_health = sum(p.health_score for p in self.projects.values()) / total

            metrics = self.metrics.get_snapshot()

            summary = DashboardSummary(
                total_projects=total,
                healthy_projects=healthy,
                at_risk_projects=at_risk,
                error_projects=error,
                avg_health_score=round(avg_health, 2),
                total_validations=metrics.total_validations,
                overall_success_rate=metrics.success_rate,
                last_update=self._last_update,
            )

            self._cache.set(cache_key, summary)
            return summary

    def get_all_projects(self) -> list[dict[str, Any]]:
        """
        Get all projects as a list of dictionaries.

        Returns:
            List of project dictionaries sorted by last_updated (newest first)
        """
        cache_key = "all_projects"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        with self._lock:
            projects = sorted(
                [p.to_dict() for p in self.projects.values()],
                key=lambda x: x["last_updated"],
                reverse=True,
            )
            self._cache.set(cache_key, projects)
            return projects

    def get_metrics(self) -> MetricsSnapshot:
        """Get current metrics snapshot."""
        return self.metrics.get_snapshot()

    def get_project_health_trend(self, project_id: str) -> ProjectHealthTrend | None:
        """Get health trend data for a specific project."""
        return self.metrics.get_project_health_trend(project_id)

    def get_error_summary(self) -> dict[str, int]:
        """
        Get summary of errors by type.

        Returns:
            Dictionary mapping error types to counts
        """
        return self.metrics.get_snapshot().error_counts.copy()

    def remove_project(self, project_id: str) -> bool:
        """
        Remove a project from tracking.

        Args:
            project_id: Project to remove

        Returns:
            True if project was removed, False if not found
        """
        with self._lock:
            if project_id in self.projects:
                del self.projects[project_id]
                self._cache.invalidate()
                return True
            return False

    def clear_all(self) -> None:
        """Clear all project data and metrics."""
        with self._lock:
            self.projects.clear()
            self.metrics.reset()
            self._cache.invalidate()
            self._last_update = 0.0
