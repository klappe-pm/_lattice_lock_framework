"""
Lattice Lock Dashboard Backend

FastAPI application providing dashboard endpoints for project monitoring,
metrics visualization, and real-time updates via WebSocket.
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .aggregator import DataAggregator
from .mock_data import mock_data_updater
from .websocket import WebSocketManager

# Configure logging
logger = logging.getLogger("lattice_lock.dashboard")

# API version
API_VERSION = "1.0.0"


# Shared state management moved to app.state
# Use dependency injection to access these

from fastapi import Depends, Request


def get_aggregator(request: Request) -> DataAggregator:
    """Get the shared DataAggregator instance from app state."""
    return request.app.state.aggregator


def get_ws_manager(request: Request) -> WebSocketManager:
    """Get the shared WebSocketManager instance from app state."""
    return request.app.state.ws_manager


# Pydantic models for API responses
class SummaryResponse(BaseModel):
    """Dashboard summary response."""

    total_projects: int = Field(description="Total number of registered projects")
    healthy_projects: int = Field(description="Number of healthy projects")
    at_risk_projects: int = Field(description="Number of at-risk projects")
    error_projects: int = Field(description="Number of projects with errors")
    avg_health_score: float = Field(description="Average health score across all projects")
    total_validations: int = Field(description="Total validation count")
    overall_success_rate: float = Field(description="Overall validation success rate")
    last_update: float = Field(description="Timestamp of last update")


class ProjectResponse(BaseModel):
    """Project information response."""

    id: str = Field(description="Project identifier")
    name: str = Field(description="Project name")
    status: str = Field(description="Current project status")
    last_updated: float = Field(description="Last update timestamp")
    health_score: int = Field(description="Project health score (0-100)")
    error_count: int = Field(description="Total error count")
    warning_count: int = Field(description="Total warning count")
    validation_count: int = Field(description="Total validation count")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional details")


class MetricsResponse(BaseModel):
    """Metrics data response."""

    total_validations: int = Field(description="Total validation count")
    success_rate: float = Field(description="Validation success rate (%)")
    avg_response_time: float = Field(description="Average response time (seconds)")
    error_counts: dict[str, int] = Field(description="Error counts by type")
    health_score: int = Field(description="Overall health score (0-100)")
    timestamp: float = Field(description="Metrics timestamp")
    response_time_p50: float = Field(description="50th percentile response time")
    response_time_p95: float = Field(description="95th percentile response time")
    response_time_p99: float = Field(description="99th percentile response time")
    validations_per_minute: float = Field(description="Current validation rate")
    error_rate: float = Field(description="Error rate (%)")


class ProjectUpdateRequest(BaseModel):
    """Request to update a project's status."""

    status: str = Field(description="New status value")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional details")
    duration: float = Field(default=0.1, description="Operation duration for metrics")


class ConnectionStatsResponse(BaseModel):
    """WebSocket connection statistics response."""

    total_connections: int = Field(description="Number of active WebSocket connections")
    connections: list[dict[str, Any]] = Field(description="Details of each connection")


# Create the API router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get Dashboard Summary",
    description="Get an overall summary of all projects and system health.",
)
async def get_summary(aggregator: DataAggregator = Depends(get_aggregator)) -> SummaryResponse:
    """
    Get dashboard summary.

    Returns aggregated statistics about all registered projects including
    health scores, validation counts, and success rates.
    """
    # aggregator = get_aggregator() # DI handled by Depends
    summary = aggregator.get_project_summary()

    return SummaryResponse(
        total_projects=summary.total_projects,
        healthy_projects=summary.healthy_projects,
        at_risk_projects=summary.at_risk_projects,
        error_projects=summary.error_projects,
        avg_health_score=summary.avg_health_score,
        total_validations=summary.total_validations,
        overall_success_rate=summary.overall_success_rate,
        last_update=summary.last_update,
    )


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
    summary="List All Projects",
    description="Get a list of all registered projects with their current status.",
)
async def get_projects(
    aggregator: DataAggregator = Depends(get_aggregator),
) -> list[ProjectResponse]:
    """
    Get all projects.

    Returns a list of all registered projects sorted by last update time
    (most recent first).
    """
    # aggregator = get_aggregator() # DI
    projects = aggregator.get_all_projects()

    return [
        ProjectResponse(
            id=p["id"],
            name=p["name"],
            status=p["status"],
            last_updated=p["last_updated"],
            health_score=p["health_score"],
            error_count=p["error_count"],
            warning_count=p["warning_count"],
            validation_count=p["validation_count"],
            details=p["details"],
        )
        for p in projects
    ]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Get Project Details",
    description="Get detailed information about a specific project.",
    responses={
        404: {"description": "Project not found"},
    },
)
async def get_project(
    project_id: str, aggregator: DataAggregator = Depends(get_aggregator)
) -> ProjectResponse:
    """
    Get a specific project.

    Returns detailed information about a single project by ID.
    """
    # aggregator = get_aggregator() # DI
    project = aggregator.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        last_updated=project.last_updated,
        health_score=project.health_score,
        error_count=project.error_count,
        warning_count=project.warning_count,
        validation_count=project.validation_count,
        details=project.details,
    )


@router.post(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Update Project Status",
    description="Update the status of a specific project.",
)
async def update_project(
    project_id: str,
    request: Request,
    request_body: ProjectUpdateRequest,
) -> ProjectResponse:
    """
    Update a project's status.

    Updates the status of a project and broadcasts the change to
    all connected WebSocket clients.
    """

    aggregator = request.app.state.aggregator  # Alternative access pattern
    ws_manager = request.app.state.ws_manager

    project = aggregator.update_project_status(
        project_id=project_id,
        status=request_body.status,
        details=request_body.details,
        duration=request_body.duration,
    )

    # Broadcast update to WebSocket clients
    await ws_manager.broadcast_event(
        event_type="project_update",
        data={
            "project_id": project_id,
            "status": request_body.status,
            "health_score": project.health_score,
        },
        project_id=project_id,
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        last_updated=project.last_updated,
        health_score=project.health_score,
        error_count=project.error_count,
        warning_count=project.warning_count,
        validation_count=project.validation_count,
        details=project.details,
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get Metrics Data",
    description="Get current validation metrics and statistics.",
)
async def get_metrics(aggregator: DataAggregator = Depends(get_aggregator)) -> MetricsResponse:
    """
    Get metrics data.

    Returns current validation metrics including success rates,
    response times, error counts, and health scores.
    """
    # aggregator = get_aggregator() # DI
    snapshot = aggregator.get_metrics()

    return MetricsResponse(
        total_validations=snapshot.total_validations,
        success_rate=snapshot.success_rate,
        avg_response_time=snapshot.avg_response_time,
        error_counts=snapshot.error_counts,
        health_score=snapshot.health_score,
        timestamp=snapshot.timestamp,
        response_time_p50=snapshot.response_time_p50,
        response_time_p95=snapshot.response_time_p95,
        response_time_p99=snapshot.response_time_p99,
        validations_per_minute=snapshot.validations_per_minute,
        error_rate=snapshot.error_rate,
    )


@router.get(
    "/connections",
    response_model=ConnectionStatsResponse,
    summary="Get WebSocket Connection Stats",
    description="Get statistics about active WebSocket connections.",
)
async def get_connection_stats(
    ws_manager: WebSocketManager = Depends(get_ws_manager),
) -> ConnectionStatsResponse:
    """
    Get WebSocket connection statistics.

    Returns information about all active WebSocket connections.
    """
    # ws_manager = get_ws_manager() # DI
    stats = ws_manager.get_connection_stats()

    return ConnectionStatsResponse(
        total_connections=stats["total_connections"],
        connections=stats["connections"],
    )


@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time updates.

    Connect to receive real-time updates about project status changes,
    metrics updates, and system events.

    Message Types:
    - `connected`: Sent on connection establishment
    - `project_update`: Sent when a project status changes
    - `metrics_update`: Sent periodically with updated metrics
    - `heartbeat`: Sent periodically to keep connection alive
    """
    # Access via app state directly for WebSocket endpoint
    ws_manager = websocket.app.state.ws_manager
    await ws_manager.handle_connection(websocket)


# Mock data updater moved to mock_data.py


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    # Initialize shared state
    app.state.aggregator = DataAggregator()
    app.state.ws_manager = WebSocketManager()

    # Track background task for cleanup
    _background_task = None

    logger.info("Starting Lattice Lock Dashboard Backend v%s", API_VERSION)

    # Start background mock updater (for demo purposes)
    # In production, remove this or make it configurable
    if hasattr(app.state, "enable_mock_updates") and app.state.enable_mock_updates:
        _background_task = asyncio.create_task(
            mock_data_updater(app.state.aggregator, app.state.ws_manager)
        )

    yield

    # Shutdown
    if _background_task:
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass

    # Close WebSocket connections
    if hasattr(app.state, "ws_manager"):
        await app.state.ws_manager.close_all()

    logger.info("Shutting down Lattice Lock Dashboard Backend")


def create_app(
    cors_origins: Optional[list[str]] = None,
    debug: bool = False,
    enable_mock_updates: bool = True,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        cors_origins: List of allowed CORS origins. Defaults to ["*"].
        debug: Enable debug mode with additional logging.
        enable_mock_updates: Enable mock data updates for demo.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Lattice Lock Dashboard API",
        description="""
## Lattice Lock Dashboard API

Real-time monitoring dashboard for Lattice Lock projects.

### Features

- **Project Monitoring**: View and track all registered projects
- **Health Metrics**: Monitor validation success rates and health scores
- **Real-Time Updates**: WebSocket support for live updates
- **Performance Metrics**: Response time percentiles and error tracking

### WebSocket Usage

Connect to `/dashboard/live` to receive real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8080/dashboard/live');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```
        """,
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    # Use explicit origins if provided, otherwise default to typical local development
    if cors_origins is None:
        cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Store config in app state for lifespan access
    app.state.enable_mock_updates = enable_mock_updates

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include dashboard routes
    app.include_router(router)

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "name": "Lattice Lock Dashboard API",
            "version": API_VERSION,
            "docs": "/docs",
            "dashboard": "/dashboard/summary",
        }

    return app


# Default application instance
app = create_app()


def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = False,
    cors_origins: Optional[list[str]] = None,
    debug: bool = False,
) -> None:
    """
    Run the Dashboard API server.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 8080)
        reload: Enable auto-reload for development
        cors_origins: List of allowed CORS origins
        debug: Enable debug mode
    """
    import uvicorn

    global app
    app = create_app(cors_origins=cors_origins, debug=debug)

    log_level = "debug" if debug else "info"

    logger.info("Starting Dashboard API server on %s:%d", host, port)

    uvicorn.run(
        "lattice_lock.dashboard.backend:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()
