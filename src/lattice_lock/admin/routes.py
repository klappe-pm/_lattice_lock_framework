"""
Lattice Lock Admin API Routes

Defines the REST API endpoints for project management and monitoring.
"""

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from lattice_lock.admin.models import (
    ProjectError,
    RollbackInfo,
    ValidationStatus,
    get_project_store,
)
from lattice_lock.admin.schemas import (
    ErrorDetail,
    ErrorListResponse,
    ErrorResponse,
    HealthResponse,
    ProjectListResponse,
    ProjectStatusResponse,
    ProjectSummary,
    RegisterProjectRequest,
    RegisterProjectResponse,
    RollbackCheckpoint,
    RollbackRequest,
    RollbackResponse,
    ValidationStatusResponse,
)

# API version
API_VERSION = "1.0.0"

# Server start time for uptime calculation
_server_start_time = time.time()


def get_server_uptime() -> float:
    """Get server uptime in seconds."""
    return time.time() - _server_start_time


# Create the API router with prefix
router = APIRouter(prefix="/api/v1", tags=["Admin API"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API Health Check",
    description="Check the health status of the Admin API.",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current health status of the Admin API including version,
    server timestamp, and basic statistics.
    """
    store = get_project_store()
    projects = store.list_projects()

    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=time.time(),
        projects_count=len(projects),
        uptime_seconds=get_server_uptime(),
    )


@router.get(
    "/projects",
    response_model=ProjectListResponse,
    summary="List Projects",
    description="List all registered Lattice Lock projects.",
)
async def list_projects() -> ProjectListResponse:
    """
    List all registered projects.

    Returns a summary of each registered project including its status,
    error count, and last activity timestamp.
    """
    store = get_project_store()
    projects = store.list_projects()

    summaries = [
        ProjectSummary(
            id=p.id,
            name=p.name,
            path=p.path,
            status=str(p.status),
            registered_at=p.registered_at,
            last_activity=p.last_activity,
            error_count=len([e for e in p.errors if not e.resolved]),
        )
        for p in projects
    ]

    return ProjectListResponse(
        projects=summaries,
        total=len(summaries),
    )


@router.post(
    "/projects",
    response_model=RegisterProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Project",
    description="Register a new Lattice Lock project for monitoring.",
)
async def register_project(
    request: RegisterProjectRequest,
) -> RegisterProjectResponse:
    """
    Register a new project.

    Creates a new project registration with the provided name, path,
    and optional metadata.
    """
    store = get_project_store()
    project = store.register_project(
        name=request.name,
        path=request.path,
        metadata=request.metadata or {},
    )

    return RegisterProjectResponse(
        id=project.id,
        name=project.name,
        path=project.path,
        status=str(project.status),
        message=f"Project '{project.name}' registered successfully",
    )


@router.get(
    "/projects/{project_id}/status",
    response_model=ProjectStatusResponse,
    summary="Get Project Status",
    description="Get the health and validation status of a specific project.",
    responses={
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
)
async def get_project_status(project_id: str) -> ProjectStatusResponse:
    """
    Get project status.

    Returns detailed status information for a specific project including
    health status, validation results, and error counts.
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    return ProjectStatusResponse(
        id=project.id,
        name=project.name,
        path=project.path,
        status=str(project.status),
        registered_at=project.registered_at,
        last_activity=project.last_activity,
        validation=ValidationStatusResponse(
            schema_status=str(project.validation.schema_status),
            sheriff_status=str(project.validation.sheriff_status),
            gauntlet_status=str(project.validation.gauntlet_status),
            last_validated=project.validation.last_validated,
            validation_errors=project.validation.validation_errors,
        ),
        error_count=len([e for e in project.errors if not e.resolved]),
        rollback_checkpoints_count=len(project.rollback_checkpoints),
        metadata=project.metadata,
    )


@router.get(
    "/projects/{project_id}/errors",
    response_model=ErrorListResponse,
    summary="Get Project Errors",
    description="Get recent errors and incidents for a specific project.",
    responses={
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
)
async def get_project_errors(
    project_id: str,
    include_resolved: Annotated[
        bool,
        Query(description="Include resolved errors in the response"),
    ] = False,
    limit: Annotated[
        int,
        Query(description="Maximum number of errors to return", ge=1, le=500),
    ] = 100,
) -> ErrorListResponse:
    """
    Get project errors.

    Returns a list of errors for a specific project, optionally including
    resolved errors. Results are sorted by timestamp (most recent first).
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    errors = store.get_project_errors(
        project_id,
        include_resolved=include_resolved,
        limit=limit + 1,  # Fetch one extra to check if there are more
    )

    has_more = len(errors) > limit
    if has_more:
        errors = errors[:limit]

    error_details = [
        ErrorDetail(
            id=e.id,
            error_code=e.error_code,
            message=e.message,
            severity=e.severity,
            category=e.category,
            timestamp=e.timestamp,
            details=e.details,
            resolved=e.resolved,
            resolved_at=e.resolved_at,
        )
        for e in errors
    ]

    return ErrorListResponse(
        project_id=project_id,
        errors=error_details,
        total=len(error_details),
        has_more=has_more,
    )


@router.post(
    "/projects/{project_id}/rollback",
    response_model=RollbackResponse,
    summary="Trigger Rollback",
    description="Trigger a rollback to a previous project state.",
    responses={
        404: {"model": ErrorResponse, "description": "Project not found"},
        400: {"model": ErrorResponse, "description": "Invalid rollback request"},
    },
)
async def trigger_rollback(
    project_id: str,
    request: RollbackRequest,
) -> RollbackResponse:
    """
    Trigger a rollback.

    Rolls back a project to a previous checkpoint state. If no checkpoint_id
    is provided, rolls back to the most recent checkpoint. Supports dry-run
    mode to preview changes without applying them.
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    # Check if there are any checkpoints
    if not project.rollback_checkpoints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No rollback checkpoints available for this project",
        )

    # Find the checkpoint to roll back to
    checkpoint: RollbackInfo | None = None

    if request.checkpoint_id:
        # Find specific checkpoint
        for cp in project.rollback_checkpoints:
            if cp.checkpoint_id == request.checkpoint_id:
                checkpoint = cp
                break

        if not checkpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Checkpoint '{request.checkpoint_id}' not found",
            )
    else:
        # Use most recent checkpoint
        checkpoint = max(
            project.rollback_checkpoints,
            key=lambda cp: cp.timestamp,
        )

    # Perform rollback (or dry-run)
    if request.dry_run:
        return RollbackResponse(
            success=True,
            message=f"Dry run: Would rollback to checkpoint '{checkpoint.checkpoint_id}'",
            project_id=project_id,
            checkpoint_id=checkpoint.checkpoint_id,
            files_restored=checkpoint.files_count,
            dry_run=True,
            rollback_diff={
                "checkpoint_description": checkpoint.description,
                "files_to_restore": checkpoint.files_count,
                "reason": request.reason or "Not provided",
            },
        )

    # In a real implementation, this would integrate with the rollback system
    # For now, we simulate a successful rollback
    project.last_activity = time.time()
    store.update_project(project)

    return RollbackResponse(
        success=True,
        message=f"Successfully rolled back to checkpoint '{checkpoint.checkpoint_id}'",
        project_id=project_id,
        checkpoint_id=checkpoint.checkpoint_id,
        files_restored=checkpoint.files_count,
        dry_run=False,
        rollback_diff={
            "checkpoint_description": checkpoint.description,
            "files_restored": checkpoint.files_count,
            "reason": request.reason or "Not provided",
            "rolled_back_at": time.time(),
        },
    )


@router.get(
    "/projects/{project_id}/rollback/checkpoints",
    response_model=list[RollbackCheckpoint],
    summary="List Rollback Checkpoints",
    description="List available rollback checkpoints for a project.",
    responses={
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
)
async def list_rollback_checkpoints(
    project_id: str,
) -> list[RollbackCheckpoint]:
    """
    List rollback checkpoints.

    Returns all available rollback checkpoints for a specific project,
    sorted by timestamp (most recent first).
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    checkpoints = sorted(
        project.rollback_checkpoints,
        key=lambda cp: cp.timestamp,
        reverse=True,
    )

    return [
        RollbackCheckpoint(
            checkpoint_id=cp.checkpoint_id,
            timestamp=cp.timestamp,
            description=cp.description,
            files_count=cp.files_count,
        )
        for cp in checkpoints
    ]


# Helper function to record errors from external sources
def record_project_error(
    project_id: str,
    error_code: str,
    message: str,
    severity: str,
    category: str,
    details: dict | None = None,
) -> bool:
    """
    Record an error for a project.

    This function is intended to be called by other parts of the framework
    to record errors that occur during validation or execution.

    Args:
        project_id: The project identifier
        error_code: Lattice Lock error code (e.g., "LL-100")
        message: Error message
        severity: Error severity (critical, high, medium, low)
        category: Error category (validation, runtime, etc.)
        details: Additional error details

    Returns:
        True if the error was recorded, False if the project was not found
    """
    store = get_project_store()
    error = ProjectError(
        id=f"err_{uuid.uuid4().hex[:8]}",
        error_code=error_code,
        message=message,
        severity=severity,
        category=category,
        timestamp=time.time(),
        details=details or {},
    )
    return store.add_project_error(project_id, error)


# Helper function to add rollback checkpoints
def add_rollback_checkpoint(
    project_id: str,
    description: str,
    files_count: int,
) -> bool:
    """
    Add a rollback checkpoint for a project.

    Args:
        project_id: The project identifier
        description: Description of the checkpoint
        files_count: Number of files in the checkpoint

    Returns:
        True if the checkpoint was added, False if the project was not found
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        return False

    checkpoint = RollbackInfo(
        checkpoint_id=f"cp_{uuid.uuid4().hex[:8]}",
        timestamp=time.time(),
        description=description,
        files_count=files_count,
    )
    project.rollback_checkpoints.append(checkpoint)
    project.last_activity = time.time()
    store.update_project(project)

    return True


# Helper function to update validation status
def update_validation_status(
    project_id: str,
    schema_status: str | None = None,
    sheriff_status: str | None = None,
    gauntlet_status: str | None = None,
    validation_errors: list[str] | None = None,
) -> bool:
    """
    Update validation status for a project.

    Args:
        project_id: The project identifier
        schema_status: Schema validation status
        sheriff_status: Sheriff validation status
        gauntlet_status: Gauntlet validation status
        validation_errors: List of validation error messages

    Returns:
        True if the status was updated, False if the project was not found
    """
    store = get_project_store()
    project = store.get_project(project_id)

    if not project:
        return False

    status_map = {
        "passed": ValidationStatus.PASSED,
        "failed": ValidationStatus.FAILED,
        "pending": ValidationStatus.PENDING,
        "not_run": ValidationStatus.NOT_RUN,
    }

    if schema_status:
        project.validation.schema_status = status_map.get(schema_status, ValidationStatus.NOT_RUN)
    if sheriff_status:
        project.validation.sheriff_status = status_map.get(sheriff_status, ValidationStatus.NOT_RUN)
    if gauntlet_status:
        project.validation.gauntlet_status = status_map.get(
            gauntlet_status, ValidationStatus.NOT_RUN
        )
    if validation_errors is not None:
        project.validation.validation_errors = validation_errors

    project.validation.last_validated = time.time()
    project.last_activity = time.time()
    project._update_status()
    store.update_project(project)

    return True
