"""
Lattice Lock Admin API Routes

Defines the REST API endpoints for project management and monitoring.
"""

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from lattice_lock.admin.auth import require_admin, require_operator, require_viewer
from lattice_lock.admin.db import get_db
from lattice_lock.admin.models import Project, ProjectError
from lattice_lock.admin.schemas import (
    ErrorDetail,
    ErrorListResponse,
    HealthResponse,
    ProjectListResponse,
    ProjectStatusResponse,
    ProjectSummary,
    RegisterProjectRequest,
    RegisterProjectResponse,
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
    # Eager load errors to avoid MissingGreenlet error when accessing p.errors
    result = await db.execute(select(Project).options(selectinload(Project.errors)))
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
async def get_project_status(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectStatusResponse:
    """Get project status."""
    # Eager load relationships
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.errors), selectinload(Project.rollback_checkpoints))
    )
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
        rollback_checkpoints_count=len(project.rollback_checkpoints),
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
        query = query.where(ProjectError.resolved == False)  # noqa: E712

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
