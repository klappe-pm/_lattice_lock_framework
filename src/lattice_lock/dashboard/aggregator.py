"""
Data Aggregator for Dashboard Backend

Collects validation status from all projects, aggregates error counts and trends,
calculates health scores, and caches results for performance.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class HealthLevel(str, Enum):
    """Health level classification for projects."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ValidationStatus:
    """Status of a single validation run."""
    timestamp: datetime
    passed: bool
    error_count: int
    warning_count: int
    duration_ms: float
    validator_type: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthScore:
    """Health score for a project or the overall system."""
    score: float  # 0.0 to 100.0
    level: HealthLevel
    factors: dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def calculate(
        cls,
        validation_success_rate: float,
        error_trend: float,
        recent_failures: int,
        response_time_score: float,
    ) -> "HealthScore":
        """Calculate health score from multiple factors.
        
        Args:
            validation_success_rate: Percentage of successful validations (0-100)
            error_trend: Trend direction (-1 to 1, negative is improving)
            recent_failures: Number of failures in last 24 hours
            response_time_score: Score based on response times (0-100)
        
        Returns:
            HealthScore with calculated values
        """
        factors = {
            "validation_success_rate": validation_success_rate,
            "error_trend": max(0, 100 - (error_trend * 50)),
            "recent_failures": max(0, 100 - (recent_failures * 10)),
            "response_time": response_time_score,
        }
        
        weights = {
            "validation_success_rate": 0.4,
            "error_trend": 0.2,
            "recent_failures": 0.25,
            "response_time": 0.15,
        }
        
        score = sum(factors[k] * weights[k] for k in factors)
        
        if score >= 80:
            level = HealthLevel.HEALTHY
        elif score >= 50:
            level = HealthLevel.WARNING
        else:
            level = HealthLevel.CRITICAL
        
        return cls(score=score, level=level, factors=factors)


@dataclass
class ProjectStatus:
    """Status information for a single project."""
    project_id: str
    name: str
    path: str
    health: HealthScore
    last_validation: Optional[ValidationStatus]
    validation_history: list[ValidationStatus] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "path": self.path,
            "health": {
                "score": self.health.score,
                "level": self.health.level.value,
                "factors": self.health.factors,
            },
            "last_validation": {
                "timestamp": self.last_validation.timestamp.isoformat(),
                "passed": self.last_validation.passed,
                "error_count": self.last_validation.error_count,
                "warning_count": self.last_validation.warning_count,
                "duration_ms": self.last_validation.duration_ms,
            } if self.last_validation else None,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "last_updated": self.last_updated.isoformat(),
        }


class DataAggregator:
    """Aggregates data from multiple sources for the dashboard.
    
    Collects validation status, calculates health scores, and maintains
    cached results for performance.
    """
    
    def __init__(self, cache_ttl_seconds: int = 30):
        """Initialize the data aggregator.
        
        Args:
            cache_ttl_seconds: Time-to-live for cached data in seconds
        """
        self._projects: dict[str, ProjectStatus] = {}
        self._cache: dict[str, tuple[Any, float]] = {}
        self._cache_ttl = cache_ttl_seconds
        self._lock = asyncio.Lock()
        self._validation_history: list[ValidationStatus] = []
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache:
            return False
        _, timestamp = self._cache[key]
        return (time.time() - timestamp) < self._cache_ttl
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if valid."""
        if self._is_cache_valid(key):
            return self._cache[key][0]
        return None
    
    def _set_cached(self, key: str, value: Any) -> None:
        """Set cached data with current timestamp."""
        self._cache[key] = (value, time.time())
    
    async def register_project(
        self,
        project_id: str,
        name: str,
        path: str,
    ) -> ProjectStatus:
        """Register a new project for monitoring.
        
        Args:
            project_id: Unique identifier for the project
            name: Human-readable project name
            path: Path to the project directory
        
        Returns:
            ProjectStatus for the registered project
        """
        async with self._lock:
            if project_id in self._projects:
                return self._projects[project_id]
            
            health = HealthScore(
                score=100.0,
                level=HealthLevel.UNKNOWN,
                factors={},
            )
            
            status = ProjectStatus(
                project_id=project_id,
                name=name,
                path=path,
                health=health,
                last_validation=None,
            )
            
            self._projects[project_id] = status
            return status
    
    async def record_validation(
        self,
        project_id: str,
        passed: bool,
        error_count: int,
        warning_count: int,
        duration_ms: float,
        validator_type: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record a validation result for a project.
        
        Args:
            project_id: Project identifier
            passed: Whether validation passed
            error_count: Number of errors found
            warning_count: Number of warnings found
            duration_ms: Validation duration in milliseconds
            validator_type: Type of validator (schema, env, structure, etc.)
            details: Additional details about the validation
        """
        async with self._lock:
            if project_id not in self._projects:
                return
            
            validation = ValidationStatus(
                timestamp=datetime.utcnow(),
                passed=passed,
                error_count=error_count,
                warning_count=warning_count,
                duration_ms=duration_ms,
                validator_type=validator_type,
                details=details or {},
            )
            
            project = self._projects[project_id]
            project.last_validation = validation
            project.validation_history.append(validation)
            project.error_count = error_count
            project.warning_count = warning_count
            project.last_updated = datetime.utcnow()
            
            # Keep only last 100 validations per project
            if len(project.validation_history) > 100:
                project.validation_history = project.validation_history[-100:]
            
            # Recalculate health score
            project.health = self._calculate_project_health(project)
            
            # Add to global history
            self._validation_history.append(validation)
            if len(self._validation_history) > 1000:
                self._validation_history = self._validation_history[-1000:]
            
            # Invalidate cache
            self._cache.clear()
    
    def _calculate_project_health(self, project: ProjectStatus) -> HealthScore:
        """Calculate health score for a project based on its history."""
        if not project.validation_history:
            return HealthScore(score=100.0, level=HealthLevel.UNKNOWN, factors={})
        
        recent = project.validation_history[-20:]
        
        # Validation success rate
        success_count = sum(1 for v in recent if v.passed)
        success_rate = (success_count / len(recent)) * 100
        
        # Error trend (compare last 10 to previous 10)
        if len(recent) >= 10:
            recent_errors = sum(v.error_count for v in recent[-10:])
            older_errors = sum(v.error_count for v in recent[-20:-10]) if len(recent) >= 20 else recent_errors
            error_trend = (recent_errors - older_errors) / max(older_errors, 1)
        else:
            error_trend = 0
        
        # Recent failures (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_failures = sum(1 for v in recent if not v.passed and v.timestamp > cutoff)
        
        # Response time score
        avg_duration = sum(v.duration_ms for v in recent) / len(recent)
        response_time_score = max(0, 100 - (avg_duration / 100))  # Penalize slow validations
        
        return HealthScore.calculate(
            validation_success_rate=success_rate,
            error_trend=error_trend,
            recent_failures=recent_failures,
            response_time_score=response_time_score,
        )
    
    async def get_project_status(self, project_id: str) -> Optional[ProjectStatus]:
        """Get status for a specific project."""
        return self._projects.get(project_id)
    
    async def get_all_projects(self) -> list[ProjectStatus]:
        """Get status for all registered projects."""
        cached = self._get_cached("all_projects")
        if cached is not None:
            return cached
        
        result = list(self._projects.values())
        self._set_cached("all_projects", result)
        return result
    
    async def get_summary(self) -> dict[str, Any]:
        """Get overall dashboard summary.
        
        Returns:
            Dictionary with summary statistics
        """
        cached = self._get_cached("summary")
        if cached is not None:
            return cached
        
        projects = list(self._projects.values())
        
        if not projects:
            summary = {
                "total_projects": 0,
                "healthy_projects": 0,
                "warning_projects": 0,
                "critical_projects": 0,
                "overall_health": 100.0,
                "total_errors": 0,
                "total_warnings": 0,
                "last_updated": datetime.utcnow().isoformat(),
            }
        else:
            healthy = sum(1 for p in projects if p.health.level == HealthLevel.HEALTHY)
            warning = sum(1 for p in projects if p.health.level == HealthLevel.WARNING)
            critical = sum(1 for p in projects if p.health.level == HealthLevel.CRITICAL)
            
            overall_health = sum(p.health.score for p in projects) / len(projects)
            total_errors = sum(p.error_count for p in projects)
            total_warnings = sum(p.warning_count for p in projects)
            
            summary = {
                "total_projects": len(projects),
                "healthy_projects": healthy,
                "warning_projects": warning,
                "critical_projects": critical,
                "overall_health": round(overall_health, 2),
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "last_updated": datetime.utcnow().isoformat(),
            }
        
        self._set_cached("summary", summary)
        return summary
    
    async def get_error_trends(self, hours: int = 24) -> dict[str, Any]:
        """Get error trends over the specified time period.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary with error trend data
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_validations = [
            v for v in self._validation_history
            if v.timestamp > cutoff
        ]
        
        if not recent_validations:
            return {
                "period_hours": hours,
                "total_validations": 0,
                "total_errors": 0,
                "total_warnings": 0,
                "error_rate": 0.0,
                "hourly_breakdown": [],
            }
        
        # Group by hour
        hourly: dict[int, list[ValidationStatus]] = {}
        for v in recent_validations:
            hour_key = v.timestamp.hour
            if hour_key not in hourly:
                hourly[hour_key] = []
            hourly[hour_key].append(v)
        
        hourly_breakdown = []
        for hour in sorted(hourly.keys()):
            validations = hourly[hour]
            hourly_breakdown.append({
                "hour": hour,
                "validations": len(validations),
                "errors": sum(v.error_count for v in validations),
                "warnings": sum(v.warning_count for v in validations),
                "failures": sum(1 for v in validations if not v.passed),
            })
        
        total_errors = sum(v.error_count for v in recent_validations)
        total_warnings = sum(v.warning_count for v in recent_validations)
        failures = sum(1 for v in recent_validations if not v.passed)
        
        return {
            "period_hours": hours,
            "total_validations": len(recent_validations),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "error_rate": (failures / len(recent_validations)) * 100 if recent_validations else 0,
            "hourly_breakdown": hourly_breakdown,
        }
