# Admin API

The `lattice_lock.admin` module provides the backend for the Lattice Lock Dashboard and administrative tools.

## Overview

This module exposes a FastAPI application that serves as the control plane for Lattice Lock projects.

## Functions

### `create_app`

```python
def create_app(cors_origins: list[str] | None = None, debug: bool = False) -> FastAPI:
```

Create and configure the FastAPI application.

**Arguments:**
- `cors_origins` (list[str] | None): List of allowed CORS origins.
- `debug` (bool): Enable debug mode.

**Returns:**
- `FastAPI`: Configured application instance.

### `run_server`

```python
def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    cors_origins: list[str] | None = None,
    debug: bool = False,
) -> None:
```

Run the Admin API server using Uvicorn.

**Arguments:**
- `host` (str): Host to bind to.
- `port` (int): Port to listen on.
- `reload` (bool): Enable auto-reload.
- `cors_origins` (list[str] | None): CORS origins.
- `debug` (bool): Debug mode.

## Usage Example

```python
from lattice_lock.admin.api import run_server

if __name__ == "__main__":
    run_server(port=9000, debug=True)
```
