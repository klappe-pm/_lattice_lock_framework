"""
Dashboard Backend with FastAPI Endpoints

Provides REST API endpoints and WebSocket endpoint for the Admin Dashboard.

Endpoints:
- GET /dashboard/summary - Overall summary
- GET /dashboard/projects - Project list with status
- GET /dashboard/metrics - Metrics data
- WS /dashboard/live - Real-time updates
"""

import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Optional

from .aggregator import DataAggregator, HealthLevel
from .metrics import MetricsCollector
from .websocket import WebSocketManager, EventType

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    WebSocket = None
    WebSocketDisconnect = None
    Query = None
    HTTPException = None
    JSONResponse = None
    CORSMiddleware = None


class DashboardBackend:
    """Backend service for the Admin Dashboard.
    
    Integrates data aggregation, metrics collection, and WebSocket
    management to provide a complete dashboard backend.
    """
    
    def __init__(
        self,
        cache_ttl_seconds: int = 30,
        metrics_retention_hours: int = 168,
    ):
        """Initialize the dashboard backend.
        
        Args:
            cache_ttl_seconds: TTL for cached data
            metrics_retention_hours: How long to retain metrics
        """
        self.aggregator = DataAggregator(cache_ttl_seconds=cache_ttl_seconds)
        self.metrics = MetricsCollector(retention_hours=metrics_retention_hours)
        self.websocket_manager = WebSocketManager()
        self._started = False
    
    async def start(self) -> None:
        """Start the backend services."""
        if self._started:
            return
        await self.websocket_manager.start()
        self._started = True
    
    async def stop(self) -> None:
        """Stop the backend services."""
        if not self._started:
            return
        await self.websocket_manager.stop()
        self._started = False
    
    async def register_project(
        self,
        project_id: str,
        name: str,
        path: str,
    ) -> dict[str, Any]:
        """Register a new project for monitoring.
        
        Args:
            project_id: Unique project identifier
            name: Project name
            path: Project path
        
        Returns:
            Project status dictionary
        """
        status = await self.aggregator.register_project(project_id, name, path)
        return status.to_dict()
    
    async def record_validation(
        self,
        project_id: str,
        passed: bool,
        error_count: int,
        warning_count: int,
        duration_ms: float,
        validator_type: str,
        error_types: Optional[list[str]] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record a validation result.
        
        Args:
            project_id: Project identifier
            passed: Whether validation passed
            error_count: Number of errors
            warning_count: Number of warnings
            duration_ms: Validation duration
            validator_type: Type of validator
            error_types: List of error types encountered
            details: Additional details
        """
        # Record in aggregator
        await self.aggregator.record_validation(
            project_id=project_id,
            passed=passed,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
            validator_type=validator_type,
            details=details,
        )
        
        # Record in metrics
        self.metrics.record_validation(
            passed=passed,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
            validator_type=validator_type,
            error_types=error_types,
        )
        
        # Broadcast via WebSocket
        await self.websocket_manager.broadcast_validation_complete(
            project_id=project_id,
            passed=passed,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
        )
        
        # Check for status changes and broadcast
        project = await self.aggregator.get_project_status(project_id)
        if project:
            summary = await self.aggregator.get_summary()
            await self.websocket_manager.broadcast_health_updated(
                overall_health=summary["overall_health"],
                healthy_count=summary["healthy_projects"],
                warning_count=summary["warning_projects"],
                critical_count=summary["critical_projects"],
            )
            
            # Record health snapshot for trends
            self.metrics.record_health_snapshot(
                score=summary["overall_health"],
                level=project.health.level.value,
                project_count=summary["total_projects"],
            )
    
    async def get_summary(self) -> dict[str, Any]:
        """Get overall dashboard summary."""
        return await self.aggregator.get_summary()
    
    async def get_projects(self) -> list[dict[str, Any]]:
        """Get all projects with their status."""
        projects = await self.aggregator.get_all_projects()
        return [p.to_dict() for p in projects]
    
    async def get_project(self, project_id: str) -> Optional[dict[str, Any]]:
        """Get a specific project's status."""
        project = await self.aggregator.get_project_status(project_id)
        return project.to_dict() if project else None
    
    async def get_metrics(
        self,
        hours: Optional[int] = None,
        validator_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get metrics data.
        
        Args:
            hours: Number of hours to look back
            validator_type: Filter by validator type
        
        Returns:
            Dictionary with metrics data
        """
        validation_metrics = self.metrics.get_validation_metrics(
            hours=hours,
            validator_type=validator_type,
        )
        error_metrics = self.metrics.get_error_metrics(hours=hours)
        response_times = self.metrics.get_response_time_percentiles()
        health_trends = self.metrics.get_health_trends(hours=hours or 24)
        validator_breakdown = self.metrics.get_validator_breakdown(hours=hours or 24)
        
        return {
            "validation": validation_metrics.to_dict(),
            "errors": error_metrics.to_dict(),
            "response_times": response_times,
            "health_trends": health_trends,
            "validator_breakdown": validator_breakdown,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def get_error_trends(self, hours: int = 24) -> dict[str, Any]:
        """Get error trends over time."""
        return await self.aggregator.get_error_trends(hours=hours)
    
    def get_websocket_stats(self) -> dict[str, Any]:
        """Get WebSocket connection statistics."""
        return self.websocket_manager.get_stats()


def create_app(
    backend: Optional[DashboardBackend] = None,
    cors_origins: Optional[list[str]] = None,
) -> "FastAPI":
    """Create a FastAPI application for the dashboard backend.
    
    Args:
        backend: Optional pre-configured backend instance
        cors_origins: List of allowed CORS origins
    
    Returns:
        Configured FastAPI application
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "FastAPI is required for the dashboard backend. "
            "Install it with: pip install fastapi uvicorn"
        )
    
    _backend = backend or DashboardBackend()
    
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifecycle."""
        await _backend.start()
        yield
        await _backend.stop()
    
    app = FastAPI(
        title="Lattice Lock Dashboard API",
        description="Backend API for the Lattice Lock Admin Dashboard",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Store backend reference
    app.state.backend = _backend
    
    @app.get("/dashboard/summary")
    async def get_summary() -> dict[str, Any]:
        """Get overall dashboard summary.
        
        Returns summary statistics including:
        - Total number of projects
        - Health status breakdown (healthy, warning, critical)
        - Overall health score
        - Total errors and warnings
        """
        return await _backend.get_summary()
    
    @app.get("/dashboard/projects")
    async def get_projects(
        health_level: Optional[str] = Query(
            None,
            description="Filter by health level (healthy, warning, critical)",
        ),
    ) -> list[dict[str, Any]]:
        """Get all projects with their status.
        
        Args:
            health_level: Optional filter by health level
        
        Returns:
            List of project status objects
        """
        projects = await _backend.get_projects()
        
        if health_level:
            try:
                level = HealthLevel(health_level)
                projects = [
                    p for p in projects
                    if p["health"]["level"] == level.value
                ]
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid health level: {health_level}. "
                           f"Valid values: healthy, warning, critical",
                )
        
        return projects
    
    @app.get("/dashboard/projects/{project_id}")
    async def get_project(project_id: str) -> dict[str, Any]:
        """Get status for a specific project.
        
        Args:
            project_id: Project identifier
        
        Returns:
            Project status object
        """
        project = await _backend.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project not found: {project_id}",
            )
        return project
    
    @app.get("/dashboard/metrics")
    async def get_metrics(
        hours: Optional[int] = Query(
            None,
            description="Number of hours to look back",
            ge=1,
            le=168,
        ),
        validator_type: Optional[str] = Query(
            None,
            description="Filter by validator type (schema, env, structure, etc.)",
        ),
    ) -> dict[str, Any]:
        """Get metrics data.
        
        Returns validation metrics, error metrics, response time percentiles,
        health trends, and validator breakdown.
        """
        return await _backend.get_metrics(hours=hours, validator_type=validator_type)
    
    @app.get("/dashboard/errors/trends")
    async def get_error_trends(
        hours: int = Query(
            24,
            description="Number of hours to look back",
            ge=1,
            le=168,
        ),
    ) -> dict[str, Any]:
        """Get error trends over time.
        
        Returns error counts, rates, and hourly breakdown.
        """
        return await _backend.get_error_trends(hours=hours)
    
    @app.get("/dashboard/websocket/stats")
    async def get_websocket_stats() -> dict[str, Any]:
        """Get WebSocket connection statistics.
        
        Returns active connection count, topic subscriptions, and connection info.
        """
        return _backend.get_websocket_stats()
    
    @app.post("/dashboard/projects")
    async def register_project(
        project_id: str = Query(..., description="Unique project identifier"),
        name: str = Query(..., description="Project name"),
        path: str = Query(..., description="Project path"),
    ) -> dict[str, Any]:
        """Register a new project for monitoring.
        
        Args:
            project_id: Unique identifier for the project
            name: Human-readable project name
            path: Path to the project directory
        
        Returns:
            Registered project status
        """
        return await _backend.register_project(project_id, name, path)
    
    @app.post("/dashboard/validations")
    async def record_validation(
        project_id: str = Query(..., description="Project identifier"),
        passed: bool = Query(..., description="Whether validation passed"),
        error_count: int = Query(0, description="Number of errors", ge=0),
        warning_count: int = Query(0, description="Number of warnings", ge=0),
        duration_ms: float = Query(..., description="Validation duration in ms", ge=0),
        validator_type: str = Query(..., description="Type of validator"),
    ) -> dict[str, str]:
        """Record a validation result.
        
        This endpoint is called after each validation run to record the result
        and trigger real-time updates to connected clients.
        """
        await _backend.record_validation(
            project_id=project_id,
            passed=passed,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
            validator_type=validator_type,
        )
        return {"status": "recorded"}
    
    @app.websocket("/dashboard/live")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time updates.
        
        Clients connect to receive real-time notifications about:
        - Validation completions
        - Project status changes
        - Health updates
        - Error detections
        
        The server sends periodic heartbeat messages to maintain the connection.
        """
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        try:
            await _backend.websocket_manager.connect(
                connection_id=connection_id,
                websocket=websocket,
            )
            
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                # Handle client messages (e.g., subscribe to topics)
                try:
                    import json
                    message = json.loads(data)
                    
                    if message.get("action") == "subscribe":
                        topic = message.get("topic")
                        if topic:
                            await _backend.websocket_manager.subscribe(
                                connection_id, topic
                            )
                    elif message.get("action") == "unsubscribe":
                        topic = message.get("topic")
                        if topic:
                            await _backend.websocket_manager.unsubscribe(
                                connection_id, topic
                            )
                except (json.JSONDecodeError, KeyError):
                    pass  # Ignore invalid messages
                    
        except WebSocketDisconnect:
            await _backend.websocket_manager.disconnect(connection_id)
        except Exception:
            await _backend.websocket_manager.disconnect(connection_id)
    
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint for load balancers and monitoring."""
        return {"status": "healthy"}
    
    return app


# Create default app instance for uvicorn
app: Optional["FastAPI"] = None

if FASTAPI_AVAILABLE:
    try:
        app = create_app()
    except Exception:
        app = None
