"""
Lattice Lock Admin API Pydantic Schemas

Request and response schemas for the Admin API endpoints.
Uses Pydantic for validation and serialization.
"""

from typing import Any

from pydantic import BaseModel, Field


class ProjectSummary(BaseModel):
    """Summary of a project for list responses."""

    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project path on the filesystem")
    status: str = Field(..., description="Current project status")
    registered_at: float = Field(..., description="Unix timestamp of registration")
    last_activity: float = Field(..., description="Unix timestamp of last activity")
    error_count: int = Field(..., description="Count of unresolved errors")


class ProjectListResponse(BaseModel):
    """Response for listing all projects."""

    projects: list[ProjectSummary] = Field(
        default_factory=list,
        description="List of registered projects",
    )
    total: int = Field(..., description="Total number of projects")


class ValidationStatusResponse(BaseModel):
    """Validation status for a project."""

    schema_status: str = Field(..., description="Schema validation status")
    sheriff_status: str = Field(..., description="Sheriff AST validation status")
    gauntlet_status: str = Field(..., description="Gauntlet contract test status")
    last_validated: float | None = Field(
        None,
        description="Unix timestamp of last validation",
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="List of validation error messages",
    )


class ProjectStatusResponse(BaseModel):
    """Response for project status endpoint."""

    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project path on the filesystem")
    status: str = Field(..., description="Current project health status")
    registered_at: float = Field(..., description="Unix timestamp of registration")
    last_activity: float = Field(..., description="Unix timestamp of last activity")
    validation: ValidationStatusResponse = Field(
        ...,
        description="Validation status details",
    )
    error_count: int = Field(..., description="Count of unresolved errors")
    rollback_checkpoints_count: int = Field(
        ...,
        description="Number of available rollback checkpoints",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional project metadata",
    )


class ErrorDetail(BaseModel):
    """Details of a single error."""

    id: str = Field(..., description="Unique error identifier")
    error_code: str = Field(..., description="Lattice Lock error code")
    message: str = Field(..., description="Error message")
    severity: str = Field(..., description="Error severity level")
    category: str = Field(..., description="Error category")
    timestamp: float = Field(..., description="Unix timestamp when error occurred")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error details",
    )
    resolved: bool = Field(..., description="Whether the error has been resolved")
    resolved_at: float | None = Field(
        None,
        description="Unix timestamp when error was resolved",
    )


class ErrorListResponse(BaseModel):
    """Response for listing project errors."""

    project_id: str = Field(..., description="Project identifier")
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="List of errors",
    )
    total: int = Field(..., description="Total number of errors returned")
    has_more: bool = Field(
        False,
        description="Whether there are more errors beyond the limit",
    )


class RollbackCheckpoint(BaseModel):
    """Information about a rollback checkpoint."""

    checkpoint_id: str = Field(..., description="Unique checkpoint identifier")
    timestamp: float = Field(..., description="Unix timestamp of checkpoint creation")
    description: str = Field(..., description="Description of the checkpoint")
    files_count: int = Field(..., description="Number of files in the checkpoint")


class RollbackRequest(BaseModel):
    """Request body for triggering a rollback."""

    checkpoint_id: str | None = Field(
        None,
        description="Specific checkpoint ID to rollback to. If not provided, rolls back to the most recent checkpoint.",
    )
    dry_run: bool = Field(
        False,
        description="If true, only simulate the rollback without making changes",
    )
    reason: str = Field(
        "",
        description="Reason for the rollback",
    )


class RollbackResponse(BaseModel):
    """Response for rollback operation."""

    success: bool = Field(..., description="Whether the rollback was successful")
    message: str = Field(..., description="Status message")
    project_id: str = Field(..., description="Project identifier")
    checkpoint_id: str | None = Field(
        None,
        description="Checkpoint that was rolled back to",
    )
    files_restored: int = Field(0, description="Number of files restored")
    dry_run: bool = Field(False, description="Whether this was a dry run")
    rollback_diff: dict[str, Any] | None = Field(
        None,
        description="Diff of changes made during rollback",
    )


class HealthResponse(BaseModel):
    """Response for API health check endpoint."""

    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")
    timestamp: float = Field(..., description="Current server timestamp")
    projects_count: int = Field(..., description="Number of registered projects")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(
        None,
        description="Additional error details",
    )


class RegisterProjectRequest(BaseModel):
    """Request body for registering a new project."""

    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    path: str = Field(
        ...,
        description="Project path on the filesystem",
        min_length=1,
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Additional project metadata",
    )


class RegisterProjectResponse(BaseModel):
    """Response for registering a new project."""

    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project path")
    status: str = Field(..., description="Initial project status")
    message: str = Field(..., description="Status message")
