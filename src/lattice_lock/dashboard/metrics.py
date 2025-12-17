"""
Lattice Lock Dashboard Metrics Module

Collects and calculates validation metrics, error frequencies,
response time percentiles, and project health trends.
"""

import statistics
import time
from collections import deque
from dataclasses import dataclass


@dataclass
class MetricsSnapshot:
    """Snapshot of current metrics state."""

    total_validations: int
    success_rate: float
    avg_response_time: float
    error_counts: dict[str, int]
    health_score: int
    timestamp: float
    # Extended metrics
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    validations_per_minute: float = 0.0
    error_rate: float = 0.0


@dataclass
class ProjectHealthTrend:
    """Health trend data for a project."""

    project_id: str
    health_scores: list[float]
    timestamps: list[float]
    trend_direction: str  # "improving", "declining", "stable"
    trend_magnitude: float


class MetricsCollector:
    """
    Collects and calculates validation metrics.

    Tracks validation success/failure rates, error frequency by type,
    response time percentiles, and project health trends.
    """

    # Maximum number of response times to keep for percentile calculation
    MAX_RESPONSE_TIMES = 1000
    # Maximum health history entries per project
    MAX_HEALTH_HISTORY = 100

    def __init__(self):
        self.validation_count = 0
        self.success_count = 0
        self.error_counts: dict[str, int] = {}
        self.response_times: deque = deque(maxlen=self.MAX_RESPONSE_TIMES)
        self._start_time = time.time()

        # Validation timestamps for rate calculation
        self._validation_timestamps: deque = deque(maxlen=1000)

        # Project-specific metrics
        self._project_validations: dict[str, int] = {}
        self._project_successes: dict[str, int] = {}
        self._project_health_history: dict[str, deque] = {}

    def record_validation(
        self,
        success: bool,
        duration: float,
        error_type: str | None = None,
        project_id: str | None = None,
    ) -> None:
        """
        Record a validation result.

        Args:
            success: Whether the validation passed
            duration: Time taken for validation in seconds
            error_type: Type of error if validation failed
            project_id: Optional project identifier for per-project metrics
        """
        current_time = time.time()

        self.validation_count += 1
        self._validation_timestamps.append(current_time)

        if success:
            self.success_count += 1

        if error_type:
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        self.response_times.append(duration)

        # Update project-specific metrics
        if project_id:
            self._project_validations[project_id] = self._project_validations.get(project_id, 0) + 1
            if success:
                self._project_successes[project_id] = self._project_successes.get(project_id, 0) + 1

            # Record health score in project history
            health = self._calculate_project_health(project_id)
            if project_id not in self._project_health_history:
                self._project_health_history[project_id] = deque(maxlen=self.MAX_HEALTH_HISTORY)
            self._project_health_history[project_id].append((current_time, health))

    def _calculate_project_health(self, project_id: str) -> float:
        """Calculate health score for a specific project."""
        validations = self._project_validations.get(project_id, 0)
        successes = self._project_successes.get(project_id, 0)

        if validations == 0:
            return 100.0

        success_rate = (successes / validations) * 100
        # Health is primarily based on success rate
        return min(100.0, max(0.0, success_rate))

    def get_percentile(self, percentile: float) -> float:
        """
        Calculate response time percentile.

        Args:
            percentile: Percentile to calculate (0-100)

        Returns:
            Response time at the given percentile
        """
        if not self.response_times:
            return 0.0

        sorted_times = sorted(self.response_times)
        index = int((percentile / 100.0) * len(sorted_times))
        index = min(index, len(sorted_times) - 1)
        return sorted_times[index]

    def get_validations_per_minute(self) -> float:
        """Calculate the current validation rate per minute."""
        if not self._validation_timestamps:
            return 0.0

        current_time = time.time()
        # Count validations in the last minute
        one_minute_ago = current_time - 60
        recent_count = sum(1 for ts in self._validation_timestamps if ts >= one_minute_ago)

        return float(recent_count)

    def get_project_health_trend(self, project_id: str) -> ProjectHealthTrend | None:
        """
        Get health trend data for a project.

        Args:
            project_id: Project identifier

        Returns:
            ProjectHealthTrend or None if no data available
        """
        history = self._project_health_history.get(project_id)
        if not history or len(history) < 2:
            return None

        timestamps = [entry[0] for entry in history]
        scores = [entry[1] for entry in history]

        # Calculate trend direction and magnitude
        if len(scores) >= 2:
            recent_avg = statistics.mean(list(scores)[-5:])  # Last 5 entries
            older_avg = statistics.mean(list(scores)[:-5] or [scores[0]])

            diff = recent_avg - older_avg

            if diff > 5:
                direction = "improving"
            elif diff < -5:
                direction = "declining"
            else:
                direction = "stable"

            magnitude = abs(diff)
        else:
            direction = "stable"
            magnitude = 0.0

        return ProjectHealthTrend(
            project_id=project_id,
            health_scores=list(scores),
            timestamps=timestamps,
            trend_direction=direction,
            trend_magnitude=magnitude,
        )

    def get_snapshot(self) -> MetricsSnapshot:
        """
        Get current metrics snapshot.

        Returns:
            MetricsSnapshot with all current metrics
        """
        success_rate = (
            (self.success_count / self.validation_count * 100)
            if self.validation_count > 0
            else 100.0
        )

        avg_time = (
            sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        )

        # Calculate health score (0-100)
        # Base 100, deduct for failures and high latency
        health = 100.0
        if self.validation_count > 0:
            failure_rate = 100 - success_rate
            health -= failure_rate * 2  # Heavy penalty for failures

            if avg_time > 1.0:  # Penalty for >1s latency
                health -= (avg_time - 1.0) * 10

        health = max(0, min(100, int(health)))

        error_rate = (
            (self.validation_count - self.success_count) / self.validation_count * 100
            if self.validation_count > 0
            else 0.0
        )

        return MetricsSnapshot(
            total_validations=self.validation_count,
            success_rate=round(success_rate, 2),
            avg_response_time=round(avg_time, 4),
            error_counts=self.error_counts.copy(),
            health_score=health,
            timestamp=time.time(),
            response_time_p50=round(self.get_percentile(50), 4),
            response_time_p95=round(self.get_percentile(95), 4),
            response_time_p99=round(self.get_percentile(99), 4),
            validations_per_minute=round(self.get_validations_per_minute(), 2),
            error_rate=round(error_rate, 2),
        )

    def reset(self) -> None:
        """Reset all metrics to initial state."""
        self.validation_count = 0
        self.success_count = 0
        self.error_counts.clear()
        self.response_times.clear()
        self._start_time = time.time()
        self._validation_timestamps.clear()
        self._project_validations.clear()
        self._project_successes.clear()
        self._project_health_history.clear()
