"""
Lattice Lock Admin API Module

Provides administrative endpoints for monitoring, management, and control
of Lattice Lock projects.

Usage:
    # Start the admin server
    from lattice_lock.admin import run_server
    run_server(host="0.0.0.0", port=8080)

    # Or use the CLI
    lattice-lock admin-server --port 8080

API Endpoints:
    GET  /api/v1/health                          - API health check
    GET  /api/v1/projects                        - List all projects
    POST /api/v1/projects                        - Register a new project
    GET  /api/v1/projects/{id}/status            - Get project status
    GET  /api/v1/projects/{id}/errors            - Get project errors
    POST /api/v1/projects/{id}/rollback          - Trigger rollback
"""

# Application exports
from lattice_lock.admin.api import create_app, run_server

# Authentication exports - from new auth package
from lattice_lock.admin.auth import (
    AuthConfig,
    Role,
    TokenData,
    User,
    api_key_header,
    authenticate_user,
    configure,
    create_access_token,
    create_refresh_token,
    create_user,
    generate_api_key,
    get_config,
    get_current_user,
    get_user,
    is_token_revoked,
    list_api_keys,
    login_for_access_token,
    oauth2_scheme,
    refresh_access_token,
    require_admin,
    require_operator,
    require_permission,
    require_roles,
    require_viewer,
    revoke_api_key,
    revoke_token,
    rotate_api_key,
    verify_api_key,
    verify_token,
)
from lattice_lock.admin.auth_routes import router as auth_router

# Model exports - only items that exist in models.py
from lattice_lock.admin.models import (
    Project,
    ProjectError,
    ProjectStatus,
    RollbackCheckpoint,
    ValidationStatus,
)

# Route exports - only items that exist
from lattice_lock.admin.routes import API_VERSION
from lattice_lock.admin.routes import router as admin_router

# Schema exports
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
    RollbackRequest,
    RollbackResponse,
    ValidationStatusResponse,
)

# Note: RollbackCheckpointSchema alias is available via schemas module if needed
# from lattice_lock.admin.schemas import RollbackCheckpoint as RollbackCheckpointSchema
# Service exports
from lattice_lock.admin.services import (
    add_rollback_checkpoint,
    record_project_error,
    update_validation_status,
)

__all__ = [
    # Application
    "create_app",
    "run_server",
    "API_VERSION",
    # Authentication Configuration
    "AuthConfig",
    "configure",
    "get_config",
    # Authentication Models
    "Role",
    "User",
    "TokenData",
    # Token operations
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "revoke_token",
    "is_token_revoked",
    "login_for_access_token",
    "refresh_access_token",
    # API key operations
    "verify_api_key",
    "generate_api_key",
    "revoke_api_key",
    "list_api_keys",
    "rotate_api_key",
    # User operations
    "create_user",
    "get_user",
    "authenticate_user",
    # Authentication Dependencies
    "get_current_user",
    "require_roles",
    "require_permission",
    "require_admin",
    "require_operator",
    "require_viewer",
    "oauth2_scheme",
    "api_key_header",
    # Routers
    "auth_router",
    "admin_router",
    # Project Models
    "Project",
    "ProjectError",
    "ProjectStatus",
    "RollbackCheckpoint",
    "ValidationStatus",
    # Schemas
    "ErrorDetail",
    "ErrorListResponse",
    "ErrorResponse",
    "HealthResponse",
    "ProjectListResponse",
    "ProjectStatusResponse",
    "ProjectSummary",
    "RegisterProjectRequest",
    "RegisterProjectResponse",
    "RollbackRequest",
    "RollbackResponse",
    "ValidationStatusResponse",
    # Helper Functions (Services)
    "add_rollback_checkpoint",
    "record_project_error",
    "update_validation_status",
]
