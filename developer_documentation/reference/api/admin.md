# Admin Module

The `lattice_lock.admin` module provides the backend for the Lattice Lock Admin Dashboard and CLI management tools. It exposes a REST API for project monitoring, health checks, and rollback operations.

## Overview

This module is built with FastAPI and provides a comprehensive set of endpoints to manage the lifecycle of Lattice Lock projects. It handles project registration, error tracking, and validation status updates.

## Application

### create_app

Creates and configures the FastAPI application.

```python
def create_app(
    cors_origins: list[str] | None = None,
    debug: bool = False,
) -> FastAPI:
    ...
```

**Arguments:**

-   `cors_origins` (list[str] | None): List of allowed CORS origins. Defaults to `["*"]`.
-   `debug` (bool): Enable debug mode with verbose logging.

### run_server

Runs the Admin API server using Uvicorn.

```python
def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    cors_origins: list[str] | None = None,
    debug: bool = False,
) -> None:
    ...
```

## Data Models

### Project

Represents a registered Lattice Lock project.

```python
@dataclass
class Project:
    id: str
    name: str
    path: str
    status: ProjectStatus
    registered_at: float
    last_activity: float
    validation: ProjectValidation
    errors: list[ProjectError]
    rollback_checkpoints: list[RollbackInfo]
    metadata: dict[str, Any]
```

### ProjectStatus

Enum representing the health status of a project.

-   `HEALTHY`: Project is valid and error-free.
-   `WARNING`: Non-critical issues detected (e.g., Gauntlet failures).
-   `ERROR`: Critical issues detected (e.g., Schema or Sheriff failures).
-   `UNKNOWN`: Status cannot be determined.

## API Endpoints

The Admin API exposes the following endpoints (prefix: `/api/v1`):

### Health & Monitoring

-   `GET /health`: Check API health status.
-   `GET /projects`: List all registered projects.
-   `GET /projects/{id}/status`: Get detailed status for a specific project.
-   `GET /projects/{id}/errors`: Get recent errors for a project.

### Management

-   `POST /projects`: Register a new project.
-   `POST /projects/{id}/rollback`: Trigger a rollback to a previous checkpoint.
-   `GET /projects/{id}/rollback/checkpoints`: List available rollback checkpoints.

## Usage Example

### Starting the Server

```python
from lattice_lock.admin import run_server

if __name__ == "__main__":
    run_server(port=8000, debug=True)
```

### interacting with the Store (Internal)

```python
from lattice_lock.admin.models import get_project_store

store = get_project_store()
projects = store.list_projects()

for project in projects:
    print(f"{project.name}: {project.status}")
```
