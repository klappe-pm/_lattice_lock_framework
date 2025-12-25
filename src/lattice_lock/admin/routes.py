"""
Lattice Lock Admin API Routes

Defines the REST API endpoints for project management and monitoring.
"""

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from lattice_lock.admin.auth import require_admin, require_operator, require_viewer
from lattice_lock.admin.models import (
    Project,
    ProjectError,
    ValidationStatus,
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

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from lattice_lock.admin.db import get_db
from lattice_lock.admin.models import Project, ProjectError

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
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Health check endpoint."""
    result = await db.execute(select(func.count(Project.id)))
    projects_count = result.scalar() or 0

    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=time.time(),
        projects_count=projects_count,
        uptime_seconds=get_server_uptime(),
    )


@router.get(
    "/projects",
    response_model=ProjectListResponse,
    summary="List Projects",
    dependencies=[Depends(require_viewer)],
)
async def list_projects(db: AsyncSession = Depends(get_db)) -> ProjectListResponse:
    """List all registered projects."""
    result = await db.execute(select(Project))
    projects = result.scalars().all()

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
    dependencies=[Depends(require_admin)],
)
async def register_project(
    request: RegisterProjectRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterProjectResponse:
    """Register a new project."""
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    project = Project(
        id=project_id,
        name=request.name,
        path=request.path,
        metadata_json=request.metadata or {},
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

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
    dependencies=[Depends(require_viewer)],
)
async def get_project_status(project_id: str, db: AsyncSession = Depends(get_db)) -> ProjectStatusResponse:
    """Get project status."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

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
            schema_status=str(project.schema_status),
            sheriff_status=str(project.sheriff_status),
            gauntlet_status=str(project.gauntlet_status),
            last_validated=project.last_validated,
            validation_errors=project.validation_errors,
        ),
        error_count=len([e for e in project.errors if not e.resolved]),
        rollback_checkpoints_count=0, # Placeholder for now
        metadata=project.metadata_json,
    )


@router.get(
    "/projects/{project_id}/errors",
    response_model=ErrorListResponse,
    summary="Get Project Errors",
    dependencies=[Depends(require_viewer)],
)
async def get_project_errors(
    project_id: str,
    include_resolved: bool = False,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> ErrorListResponse:
    """Get project errors."""
    query = select(ProjectError).where(ProjectError.project_id == project_id)
    if not include_resolved:
        query = query.where(ProjectError.resolved == False)
    
    query = query.order_by(ProjectError.timestamp.desc()).limit(limit + 1)
    result = await db.execute(query)
    errors = result.scalars().all()

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
    dependencies=[Depends(require_operator)],
)
async def trigger_rollback(
    project_id: str,
    request: RollbackRequest,
    db: AsyncSession = Depends(get_db),
) -> RollbackResponse:
    """Trigger a rollback."""
    # This remains a simulation for now, but uses the DB to check project existence
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    return RollbackResponse(
        success=True,
        message="Rollback simulation successful (Persistent DB integration active)",
        project_id=project_id,
        checkpoint_id="latest",
        files_restored=0,
        dry_run=request.dry_run,
        rollback_diff={},
    )


# Helper function to record errors from external sources
async def record_project_error(
    db: AsyncSession,
    project_id: str,
    error_code: str,
    message: str,
    severity: str,
    category: str,
    details: dict | None = None,
) -> bool:
    """Record an error for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return False
        
    error = ProjectError(
        id=f"err_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        error_code=error_code,
        message=message,
        severity=severity,
        category=category,
        timestamp=time.time(),
        details=details or {},
    )
    db.add(error)
    project.last_activity = time.time()
    await db.commit()
    return True


async def update_validation_status(
    db: AsyncSession,
    project_id: str,
    schema_status: str | None = None,
    sheriff_status: str | None = None,
    gauntlet_status: str | None = None,
    validation_errors: list[str] | None = None,
) -> bool:
    """Update validation status for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return False

    if schema_status:
        project.schema_status = schema_status
    if sheriff_status:
        project.sheriff_status = sheriff_status
    if gauntlet_status:
        project.gauntlet_status = gauntlet_status
    if validation_errors is not None:
        project.validation_errors = validation_errors

    project.last_validated = time.time()
    project.last_activity = time.time()
    await db.commit()
    return True
