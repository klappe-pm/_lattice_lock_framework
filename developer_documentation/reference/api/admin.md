# Admin Module

The `lattice_lock.admin` module provides the backend API for monitoring and managing Lattice Lock projects. It includes a FastAPI application, authentication, and data models for project status and errors.

## Overview

The Admin API exposes endpoints for project registration, health monitoring, error tracking, and rollback management.

## Modules

### API Application (`api.py`)

Configures and runs the FastAPI application.

#### Functions

- `create_app(cors_origins: list[str] | None = None, debug: bool = False) -> FastAPI`: Creates the FastAPI app.
- `run_server(host: str, port: int, reload: bool, cors_origins: list[str] | None, debug: bool)`: Runs the API server.

### Authentication (`auth.py`)

Handles user authentication and authorization.

#### Classes

- `Role(Enum)`: User roles (ADMIN, OPERATOR, VIEWER).
- `User(BaseModel)`: User model.
- `TokenData(BaseModel)`: JWT token payload.

#### Functions

- `create_access_token(username: str, role: Role, expires_delta: timedelta | None) -> str`: Creates a JWT access token.
- `verify_token(token: str) -> TokenData`: Verifies a JWT token.
- `get_current_user(token: str) -> TokenData`: Dependency to get the current user.
- `require_roles(*allowed_roles: Role)`: Dependency to enforce role-based access.

### Routes (`routes.py`)

Defines the API endpoints.

#### Endpoints

- `GET /api/v1/health`: API health check.
- `GET /api/v1/projects`: List all projects.
- `POST /api/v1/projects`: Register a new project.
- `GET /api/v1/projects/{project_id}/status`: Get project status.
- `GET /api/v1/projects/{project_id}/errors`: Get project errors.
- `POST /api/v1/projects/{project_id}/rollback`: Trigger a rollback.

### Models (`models.py`)

Internal data models for the application.

#### Classes

- `Project`: Represents a registered project.
- `ProjectError`: Represents an error in a project.
- `ProjectStatus(Enum)`: Status of a project (HEALTHY, WARNING, ERROR).
- `ProjectStore`: Thread-safe in-memory store for projects.

### Schemas (`schemas.py`)

Pydantic schemas for API requests and responses.

#### Classes

- `ProjectSummary`: Summary of a project.
- `ProjectStatusResponse`: Detailed project status.
- `ErrorDetail`: Details of an error.
- `RollbackRequest`: Request body for rollback.
- `RollbackResponse`: Response for rollback.

## Usage Examples

### Running the Server

```python
from lattice_lock.admin.api import run_server

if __name__ == "__main__":
    run_server(host="0.0.0.0", port=8000, debug=True)
```

### Registering a Project (Client Side)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/projects",
    json={
        "name": "My Project",
        "path": "/path/to/project"
    }
)
print(response.json())
```
