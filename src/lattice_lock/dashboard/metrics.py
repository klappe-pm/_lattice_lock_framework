"""
Metrics Collector for Dashboard Backend

Provides validation success/failure rates, error frequency by type,
response time percentiles, and project health trends.
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class ValidationMetrics:
    """Metrics for validation operations."""
    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_validations == 0:
            return 100.0
        return (self.successful_validations / self.total_validations) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate as percentage."""
        if self.total_validations == 0:
            return 0.0
        return (self.failed_validations / self.total_validations) * 100
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_validations": self.total_validations,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "success_rate": round(self.success_rate, 2),
            "failure_rate": round(self.failure_rate, 2),
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "p50_duration_ms": round(self.p50_duration_ms, 2),
            "p95_duration_ms": round(self.p95_duration_ms, 2),
            "p99_duration_ms": round(self.p99_duration_ms, 2),
        }


@dataclass
class ErrorMetrics:
    """Metrics for errors by type."""
    error_counts: dict[str, int] = field(default_factory=dict)
    error_trends: dict[str, float] = field(default_factory=dict)
    most_common_errors: list[tuple[str, int]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error_counts": self.error_counts,
            "error_trends": self.error_trends,
            "most_common_errors": [
                {"type": t, "count": c} for t, c in self.most_common_errors
            ],
        }


@dataclass
class HealthTrend:
    """Health trend data point."""
    timestamp: datetime
    score: float
    level: str
    project_count: int


class MetricsCollector:
    """Collects and calculates metrics for the dashboard.
    
    Tracks validation success/failure rates, error frequency,
    response times, and health trends over time.
    """
    
    def __init__(self, retention_hours: int = 168):
        """Initialize the metrics collector.
        
        Args:
            retention_hours: How long to retain metrics data (default: 7 days)
        """
        self._retention_hours = retention_hours
        self._validation_records: list[dict[str, Any]] = []
        self._error_records: list[dict[str, Any]] = []
        self._health_snapshots: list[HealthTrend] = []
        self._durations: list[float] = []
    
    def record_validation(
        self,
        passed: bool,
        error_count: int,
        warning_count: int,
        duration_ms: float,
        validator_type: str,
        error_types: Optional[list[str]] = None,
    ) -> None:
        """Record a validation result.
        
        Args:
            passed: Whether validation passed
            error_count: Number of errors found
            warning_count: Number of warnings found
            duration_ms: Validation duration in milliseconds
            validator_type: Type of validator used
            error_types: List of error type identifiers
        """
        now = datetime.utcnow()
        
        self._validation_records.append({
            "timestamp": now,
            "passed": passed,
            "error_count": error_count,
            "warning_count": warning_count,
            "duration_ms": duration_ms,
            "validator_type": validator_type,
        })
        
        self._durations.append(duration_ms)
        
        if error_types:
            for error_type in error_types:
                self._error_records.append({
                    "timestamp": now,
                    "error_type": error_type,
                })
        
        self._cleanup_old_records()
    
    def record_health_snapshot(
        self,
        score: float,
        level: str,
        project_count: int,
    ) -> None:
        """Record a health snapshot for trend tracking.
        
        Args:
            score: Overall health score
            level: Health level (healthy, warning, critical)
            project_count: Number of projects
        """
        self._health_snapshots.append(HealthTrend(
            timestamp=datetime.utcnow(),
            score=score,
            level=level,
            project_count=project_count,
        ))
        
        self._cleanup_old_records()
    
    def _cleanup_old_records(self) -> None:
        """Remove records older than retention period."""
        cutoff = datetime.utcnow() - timedelta(hours=self._retention_hours)
        
        self._validation_records = [
            r for r in self._validation_records
            if r["timestamp"] > cutoff
        ]
        
        self._error_records = [
            r for r in self._error_records
            if r["timestamp"] > cutoff
        ]
        
        self._health_snapshots = [
            s for s in self._health_snapshots
            if s.timestamp > cutoff
        ]
        
        # Keep only recent durations for percentile calculations
        if len(self._durations) > 10000:
            self._durations = self._durations[-10000:]
    
    def get_validation_metrics(
        self,
        hours: Optional[int] = None,
        validator_type: Optional[str] = None,
    ) -> ValidationMetrics:
        """Get validation metrics for the specified period.
        
        Args:
            hours: Number of hours to look back (None for all data)
            validator_type: Filter by validator type (None for all)
        
        Returns:
            ValidationMetrics with calculated values
        """
        records = self._validation_records
        
        if hours is not None:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            records = [r for r in records if r["timestamp"] > cutoff]
        
        if validator_type is not None:
            records = [r for r in records if r["validator_type"] == validator_type]
        
        if not records:
            return ValidationMetrics()
        
        durations = [r["duration_ms"] for r in records]
        sorted_durations = sorted(durations)
        
        metrics = ValidationMetrics(
            total_validations=len(records),
            successful_validations=sum(1 for r in records if r["passed"]),
            failed_validations=sum(1 for r in records if not r["passed"]),
            total_errors=sum(r["error_count"] for r in records),
            total_warnings=sum(r["warning_count"] for r in records),
            avg_duration_ms=statistics.mean(durations) if durations else 0,
            p50_duration_ms=self._percentile(sorted_durations, 50),
            p95_duration_ms=self._percentile(sorted_durations, 95),
            p99_duration_ms=self._percentile(sorted_durations, 99),
        )
        
        return metrics
    
    def get_error_metrics(self, hours: Optional[int] = None) -> ErrorMetrics:
        """Get error metrics for the specified period.
        
        Args:
            hours: Number of hours to look back (None for all data)
        
        Returns:
            ErrorMetrics with calculated values
        """
        records = self._error_records
        
        if hours is not None:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            records = [r for r in records if r["timestamp"] > cutoff]
        
        if not records:
            return ErrorMetrics()
        
        # Count errors by type
        error_counts: dict[str, int] = {}
        for r in records:
            error_type = r["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Calculate trends (compare recent half to older half)
        midpoint = datetime.utcnow() - timedelta(hours=(hours or self._retention_hours) / 2)
        recent = [r for r in records if r["timestamp"] > midpoint]
        older = [r for r in records if r["timestamp"] <= midpoint]
        
        error_trends: dict[str, float] = {}
        for error_type in error_counts:
            recent_count = sum(1 for r in recent if r["error_type"] == error_type)
            older_count = sum(1 for r in older if r["error_type"] == error_type)
            
            if older_count > 0:
                error_trends[error_type] = (recent_count - older_count) / older_count
            elif recent_count > 0:
                error_trends[error_type] = 1.0  # New error type
            else:
                error_trends[error_type] = 0.0
        
        # Get most common errors
        most_common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return ErrorMetrics(
            error_counts=error_counts,
            error_trends=error_trends,
            most_common_errors=most_common,
        )
    
    def get_health_trends(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get health trend data for the specified period.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of health trend data points
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        snapshots = [s for s in self._health_snapshots if s.timestamp > cutoff]
        
        return [
            {
                "timestamp": s.timestamp.isoformat(),
                "score": round(s.score, 2),
                "level": s.level,
                "project_count": s.project_count,
            }
            for s in snapshots
        ]
    
    def get_response_time_percentiles(self) -> dict[str, float]:
        """Get response time percentiles from all recorded durations.
        
        Returns:
            Dictionary with percentile values
        """
        if not self._durations:
            return {
                "p50": 0.0,
                "p75": 0.0,
                "p90": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
            }
        
        sorted_durations = sorted(self._durations)
        
        return {
            "p50": round(self._percentile(sorted_durations, 50), 2),
            "p75": round(self._percentile(sorted_durations, 75), 2),
            "p90": round(self._percentile(sorted_durations, 90), 2),
            "p95": round(self._percentile(sorted_durations, 95), 2),
            "p99": round(self._percentile(sorted_durations, 99), 2),
            "min": round(min(sorted_durations), 2),
            "max": round(max(sorted_durations), 2),
            "avg": round(statistics.mean(sorted_durations), 2),
        }
    
    def get_validator_breakdown(self, hours: int = 24) -> dict[str, dict[str, Any]]:
        """Get metrics breakdown by validator type.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary with metrics per validator type
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        records = [r for r in self._validation_records if r["timestamp"] > cutoff]
        
        validator_types = set(r["validator_type"] for r in records)
        
        breakdown = {}
        for vtype in validator_types:
            type_records = [r for r in records if r["validator_type"] == vtype]
            
            if type_records:
                durations = [r["duration_ms"] for r in type_records]
                breakdown[vtype] = {
                    "total": len(type_records),
                    "passed": sum(1 for r in type_records if r["passed"]),
                    "failed": sum(1 for r in type_records if not r["passed"]),
                    "errors": sum(r["error_count"] for r in type_records),
                    "warnings": sum(r["warning_count"] for r in type_records),
                    "avg_duration_ms": round(statistics.mean(durations), 2),
                }
        
        return breakdown
    
    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Calculate percentile from sorted data.
        
        Args:
            sorted_data: Sorted list of values
            percentile: Percentile to calculate (0-100)
        
        Returns:
            Percentile value
        """
        if not sorted_data:
            return 0.0
        
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        
        if f == c:
            return sorted_data[f]
        
        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)
