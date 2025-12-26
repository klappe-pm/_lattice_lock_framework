"""
Lattice Lock Admin API Data Models

SQLAlchemy data models for project management and monitoring.
These models represent the state of registered projects and their errors.
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
import json

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, Enum as SQLEnum, Integer, DateTime, Table
from sqlalchemy.orm import Relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base

class ProjectStatus(str, Enum):
    """Status of a registered project."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class ValidationStatus(str, Enum):
    """Status of project validation."""
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    NOT_RUN = "not_run"

class ProjectError(Base):
    """Represents an error that occurred in a project."""
    __tablename__ = "project_errors"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    error_code: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(String(500))
    severity: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[float] = mapped_column(Float, default=lambda: datetime.utcnow().timestamp())
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    project: Mapped["Project"] = Relationship(back_populates="errors")

    def to_dict(self) -> dict[str, Any]:
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

class RollbackCheckpoint(Base):
    """Represents a file system rollback checkpoint."""
    __tablename__ = "rollback_checkpoints"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    description: Mapped[str] = mapped_column(String(200)) # e.g. "Pre-refactor"
    files_count: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[float] = mapped_column(Float, default=lambda: datetime.utcnow().timestamp())
    
    project: Mapped["Project"] = Relationship(back_populates="rollback_checkpoints")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "files_count": self.files_count,
            "timestamp": self.timestamp,
        }

class Project(Base):
    """Represents a registered Lattice Lock project."""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    path: Mapped[str] = mapped_column(String(500))
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.UNKNOWN)
    registered_at: Mapped[float] = mapped_column(Float, default=lambda: datetime.utcnow().timestamp())
    last_activity: Mapped[float] = mapped_column(Float, default=lambda: datetime.utcnow().timestamp())
    
    # Validation fields
    schema_status: Mapped[ValidationStatus] = mapped_column(SQLEnum(ValidationStatus), default=ValidationStatus.NOT_RUN)
    sheriff_status: Mapped[ValidationStatus] = mapped_column(SQLEnum(ValidationStatus), default=ValidationStatus.NOT_RUN)
    gauntlet_status: Mapped[ValidationStatus] = mapped_column(SQLEnum(ValidationStatus), default=ValidationStatus.NOT_RUN)
    last_validated: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    validation_errors: Mapped[List[str]] = mapped_column(JSON, default=list)

    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    errors: Mapped[List["ProjectError"]] = Relationship(back_populates="project", cascade="all, delete-orphan")
    rollback_checkpoints: Mapped[List["RollbackCheckpoint"]] = Relationship(back_populates="project", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "status": str(self.status),
            "registered_at": self.registered_at,
            "last_activity": self.last_activity,
            "validation": {
                "schema_status": str(self.schema_status),
                "sheriff_status": str(self.sheriff_status),
                "gauntlet_status": str(self.gauntlet_status),
                "last_validated": self.last_validated,
                "validation_errors": self.validation_errors,
            },
            "error_count": len([e for e in self.errors if not e.resolved]),
            "rollback_checkpoints_count": len(self.rollback_checkpoints),
            "metadata": self.metadata_json,
        }
