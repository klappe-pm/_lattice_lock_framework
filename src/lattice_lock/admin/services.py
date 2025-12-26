"""
Lattice Lock Admin API Services

Provides business logic and database operations for the Admin API.
Used by routes and internal systems (like Sheriff/Gauntlet) to update project state.
"""

import time
import uuid
import logging
from typing import Dict, List, Optional, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Project, 
    ProjectError, 
    RollbackCheckpoint,
    ValidationStatus
)

logger = logging.getLogger(__name__)


async def record_project_error(
    db: AsyncSession,
    project_id: str,
    error_code: str,
    message: str,
    severity: str,
    category: str,
    details: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Record an error for a project.
    
    Args:
        db: Database session
        project_id: Project ID to record error for
        error_code: Error code string (e.g. LL-100)
        message: Human readable message
        severity: Error severity (low, medium, high, critical)
        category: Error category (validation, runtime, etc)
        details: Optional JSON details
        
    Returns:
        bool: True if project found and error recorded, False otherwise
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        logger.warning(f"Attempted to record error for non-existent project: {project_id}")
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
    
    # Update project status based on severity if needed
    if severity == "critical":
        project.status = "error"
    elif severity == "high" and project.status != "error":
         project.status = "warning"
        
    project.last_activity = time.time()
    await db.commit()
    logger.info(f"Recorded error {error_code} for project {project_id}")
    return True


async def add_rollback_checkpoint(
    db: AsyncSession,
    project_id: str,
    description: str,
    files_count: int,
) -> bool:
    """
    Add a rollback checkpoint entry to a project.
    
    Args:
        db: Database session
        project_id: Project ID
        description: Checkpoint description
        files_count: Number of files tracked
        
    Returns:
        bool: True if successful, False if project not found
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return False
        
    checkpoint = RollbackCheckpoint(
        id=f"cp_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        description=description,
        files_count=files_count,
        timestamp=time.time(),
    )
    db.add(checkpoint)
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
    """
    Update validation status for a project.

    Args:
        db: Database session
        project_id: Project ID
        schema_status: Status of schema validation
        sheriff_status: Status of policy validation
        gauntlet_status: Status of integration tests
        validation_errors: List of error strings
        
    Returns:
        bool: True if project found and updated
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return False

    if schema_status:
        try:
            project.schema_status = ValidationStatus(schema_status)
        except ValueError:
            pass # Keep existing logic or log warning
            
    if sheriff_status:
        try:
            project.sheriff_status = ValidationStatus(sheriff_status)
        except ValueError:
            pass

    if gauntlet_status:
        try:
            project.gauntlet_status = ValidationStatus(gauntlet_status)
        except ValueError:
            pass
            
    if validation_errors is not None:
        project.validation_errors = validation_errors

    # Determine overall status logic
    # This logic mimics what was in routes.py implicitly or explicitly
    all_passed = (
        project.schema_status == ValidationStatus.PASSED and
        project.sheriff_status == ValidationStatus.PASSED and
        # Gauntlet is optional for "healthy" base status often, but let's be strict if present
        (project.gauntlet_status == ValidationStatus.PASSED or project.gauntlet_status == ValidationStatus.NOT_RUN)
    )
    
    has_failures = (
        project.schema_status == ValidationStatus.FAILED or
        project.sheriff_status == ValidationStatus.FAILED
    )
    
    if all_passed:
        project.status = "healthy"
    elif has_failures:
        project.status = "error"
    elif project.gauntlet_status == ValidationStatus.FAILED:
         project.status = "warning"

    project.last_validated = time.time()
    project.last_activity = time.time()
    await db.commit()
    return True
