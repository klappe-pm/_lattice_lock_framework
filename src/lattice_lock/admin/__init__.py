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
    GET  /api/v1/projects/{id}/rollback/checkpoints - List rollback checkpoints
"""

# Authentication exports
from lattice_lock.admin.auth import (
    AuthConfig,
    Role,
    User,
    TokenData,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_api_key,
    get_current_user,
    require_roles,
    require_permission,
    require_admin,
    require_operator,
    require_viewer,
    generate_api_key,
    revoke_token,
    is_token_revoked,
    revoke_api_key,
    list_api_keys,
    rotate_api_key,
    create_user,
    get_user,
    authenticate_user,
    configure,
    get_config,
    oauth2_scheme,
    api_key_header,
)
from lattice_lock.admin.auth_routes import router as auth_router

# Application exports
from lattice_lock.admin.api import create_app, run_server

# Model exports
from lattice_lock.admin.models import (
    Project,
    ProjectError,
    ProjectStatus,
    ProjectStore,
    ProjectValidation,
    RollbackInfo,
    ValidationStatus,
    get_project_store,
    reset_project_store,
)

# Route exports
from lattice_lock.admin.routes import (
    add_rollback_checkpoint,
    record_project_error,
    update_validation_status,
    router as admin_router,
    API_VERSION,
)

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
    RollbackCheckpoint,
    RollbackRequest,
    RollbackResponse,
    ValidationStatusResponse,
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
    "ProjectStore",
    "ProjectValidation",
    "RollbackInfo",
    "ValidationStatus",
    "get_project_store",
    "reset_project_store",
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
    "RollbackCheckpoint",
    "RollbackRequest",
    "RollbackResponse",
    "ValidationStatusResponse",
    # Helper Functions
    "record_project_error",
    "add_rollback_checkpoint",
    "update_validation_status",
]
