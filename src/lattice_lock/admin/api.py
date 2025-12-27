"""
Lattice Lock Admin API Application

FastAPI application for the Admin API with CORS, error handling,
request logging, and OpenAPI documentation.
"""

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lattice_lock.admin.routes import API_VERSION, router
from lattice_lock.logging_config import set_trace_id

# Configure logging
logger = logging.getLogger("lattice_lock.admin")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Handles startup and shutdown events for the application.
    Ensures graceful shutdown by awaiting all background tasks.
    """
    from lattice_lock.utils.async_compat import get_background_queue

    # Startup
    logger.info(f"Starting Lattice Lock Admin API v{API_VERSION}")
    app.state.task_queue = get_background_queue()
    yield
    # Shutdown - CRITICAL: await all background tasks
    logger.info("Shutting down Lattice Lock Admin API - waiting for background tasks...")
    try:
        await app.state.task_queue.wait_all(timeout=10.0)
    except Exception as e:
        logger.error(f"Error waiting for background tasks: {e}")
    logger.info("Lattice Lock Admin API shutdown complete")


def create_app(
    cors_origins: list[str] | None = None,
    debug: bool = False,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        cors_origins: List of allowed CORS origins. Defaults to ["*"] if None.
        debug: Enable debug mode with additional logging.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Lattice Lock Admin API",
        description="""
## Lattice Lock Framework Admin API

REST API for monitoring and managing Lattice Lock projects.

### Features

- **Project Management**: Register and monitor Lattice Lock projects
- **Health Monitoring**: Track project health and validation status
- **Error Tracking**: View recent errors and incidents
- **Rollback Management**: Trigger rollbacks to previous states

### Authentication

Currently, the Admin API does not require authentication. In production
deployments, it is recommended to run the API behind a reverse proxy
with authentication enabled.

### Error Codes

All errors follow the Lattice Lock error code format:
- `LL-1xx`: Schema validation errors
- `LL-2xx`: Sheriff AST validation errors
- `LL-3xx`: Gauntlet contract test errors
- `LL-4xx`: Runtime errors
- `LL-5xx`: Configuration errors
- `LL-6xx`: Network errors
- `LL-7xx`: Agent errors
        """,
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    if cors_origins is None:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware with trace ID
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Any) -> Any:
        """Log all incoming requests with trace ID."""
        # Generate trace ID for this request (check header first for distributed tracing)
        trace_id = request.headers.get("X-Trace-ID") or set_trace_id()
        if not request.headers.get("X-Trace-ID"):
            set_trace_id(trace_id)

        start_time = time.time()

        # Log request
        if debug:
            logger.debug(f"Request: {request.method} {request.url.path} [trace_id={trace_id}]")

        # Process request
        response = await call_next(request)

        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)"
        )

        return response

    # Custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            error_detail = {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            errors.append(error_detail)

        logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            errors,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": {"errors": errors},
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(
            "Unexpected error on %s %s: %s",
            request.method,
            request.url.path,
            str(exc),
        )

        # In debug mode, include exception details
        if debug:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "InternalServerError",
                    "message": str(exc),
                    "details": {"type": type(exc).__name__},
                },
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": None,
            },
        )

    # Include API routes
    app.include_router(router)

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root endpoint redirecting to documentation."""
        return {
            "name": "Lattice Lock Admin API",
            "version": API_VERSION,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


# Default application instance
app = create_app()


def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    cors_origins: list[str] | None = None,
    debug: bool = False,
) -> None:
    """
    Run the Admin API server.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 8080)
        reload: Enable auto-reload for development
        cors_origins: List of allowed CORS origins
        debug: Enable debug mode
    """
    import uvicorn

    # Create app with specified configuration
    global app
    app = create_app(cors_origins=cors_origins, debug=debug)

    # Configure logging based on debug mode
    log_level = "debug" if debug else "info"

    logger.info(f"Starting Admin API server on {host}:{port}")

    uvicorn.run(
        "lattice_lock.admin.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )
