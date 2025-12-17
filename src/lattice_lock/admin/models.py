"""
Lattice Lock Admin API Data Models

In-memory data models and storage for project management and monitoring.
These models represent the state of registered projects and their errors.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProjectStatus(Enum):
    """Status of a registered project."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value


class ValidationStatus(Enum):
    """Status of project validation."""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    NOT_RUN = "not_run"

    def __str__(self) -> str:
        return self.value


@dataclass
class ProjectError:
    """Represents an error that occurred in a project."""

    id: str
    error_code: str
    message: str
    severity: str
    category: str
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity,
            "category": self.category,
            "timestamp": self.timestamp,
            "details": self.details,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }


@dataclass
class ProjectValidation:
    """Represents validation results for a project."""

    schema_status: ValidationStatus = ValidationStatus.NOT_RUN
    sheriff_status: ValidationStatus = ValidationStatus.NOT_RUN
    gauntlet_status: ValidationStatus = ValidationStatus.NOT_RUN
    last_validated: float | None = None
    validation_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "schema_status": str(self.schema_status),
            "sheriff_status": str(self.sheriff_status),
            "gauntlet_status": str(self.gauntlet_status),
            "last_validated": self.last_validated,
            "validation_errors": self.validation_errors,
        }


@dataclass
class RollbackInfo:
    """Information about a rollback checkpoint."""

    checkpoint_id: str
    timestamp: float
    description: str
    files_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "files_count": self.files_count,
        }


@dataclass
class Project:
    """Represents a registered Lattice Lock project."""

    id: str
    name: str
    path: str
    status: ProjectStatus = ProjectStatus.UNKNOWN
    registered_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    validation: ProjectValidation = field(default_factory=ProjectValidation)
    errors: list[ProjectError] = field(default_factory=list)
    rollback_checkpoints: list[RollbackInfo] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "status": str(self.status),
            "registered_at": self.registered_at,
            "last_activity": self.last_activity,
            "validation": self.validation.to_dict(),
            "error_count": len([e for e in self.errors if not e.resolved]),
            "rollback_checkpoints_count": len(self.rollback_checkpoints),
            "metadata": self.metadata,
        }

    def add_error(self, error: ProjectError) -> None:
        """Add an error to the project."""
        self.errors.append(error)
        self.last_activity = time.time()
        self._update_status()

    def resolve_error(self, error_id: str) -> bool:
        """Resolve an error by ID."""
        for error in self.errors:
            if error.id == error_id:
                error.resolved = True
                error.resolved_at = time.time()
                self._update_status()
                return True
        return False

    def _update_status(self) -> None:
        """Update project status based on current state."""
        unresolved_errors = [e for e in self.errors if not e.resolved]

        if not unresolved_errors:
            # Check validation status
            if self.validation.schema_status == ValidationStatus.FAILED:
                self.status = ProjectStatus.ERROR
            elif self.validation.sheriff_status == ValidationStatus.FAILED:
                self.status = ProjectStatus.ERROR
            elif self.validation.gauntlet_status == ValidationStatus.FAILED:
                self.status = ProjectStatus.WARNING
            elif self.validation.last_validated is None:
                self.status = ProjectStatus.UNKNOWN
            else:
                self.status = ProjectStatus.HEALTHY
        else:
            critical_errors = [e for e in unresolved_errors if e.severity in ("critical", "high")]
            if critical_errors:
                self.status = ProjectStatus.ERROR
            else:
                self.status = ProjectStatus.WARNING


class ProjectStore:
    """Thread-safe in-memory store for projects.

    This is a simple in-memory implementation for the Admin API.
    In production, this would be replaced with a database.
    """

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._lock = threading.RLock()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a unique project ID."""
        with self._lock:
            project_id = f"proj_{self._next_id:04d}"
            self._next_id += 1
            return project_id

    def register_project(
        self,
        name: str,
        path: str,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        """Register a new project."""
        with self._lock:
            project_id = self._generate_id()
            project = Project(
                id=project_id,
                name=name,
                path=path,
                metadata=metadata or {},
            )
            self._projects[project_id] = project
            return project

    def get_project(self, project_id: str) -> Project | None:
        """Get a project by ID."""
        with self._lock:
            return self._projects.get(project_id)

    def list_projects(self) -> list[Project]:
        """List all registered projects."""
        with self._lock:
            return list(self._projects.values())

    def update_project(self, project: Project) -> None:
        """Update a project in the store."""
        with self._lock:
            if project.id in self._projects:
                self._projects[project.id] = project

    def delete_project(self, project_id: str) -> bool:
        """Delete a project by ID."""
        with self._lock:
            if project_id in self._projects:
                del self._projects[project_id]
                return True
            return False

    def get_project_errors(
        self,
        project_id: str,
        include_resolved: bool = False,
        limit: int = 100,
    ) -> list[ProjectError]:
        """Get errors for a project."""
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return []

            errors = project.errors
            if not include_resolved:
                errors = [e for e in errors if not e.resolved]

            # Sort by timestamp descending (most recent first)
            errors = sorted(errors, key=lambda e: e.timestamp, reverse=True)

            return errors[:limit]

    def add_project_error(
        self,
        project_id: str,
        error: ProjectError,
    ) -> bool:
        """Add an error to a project."""
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return False
            project.add_error(error)
            return True

    def clear(self) -> None:
        """Clear all projects (for testing)."""
        with self._lock:
            self._projects.clear()
            self._next_id = 1


# Global project store instance
_project_store: ProjectStore | None = None


def get_project_store() -> ProjectStore:
    """Get the global project store instance."""
    global _project_store
    if _project_store is None:
        _project_store = ProjectStore()
    return _project_store


def reset_project_store() -> None:
    """Reset the global project store (for testing)."""
    global _project_store
    _project_store = ProjectStore()
