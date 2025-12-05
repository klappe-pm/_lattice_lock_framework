"""
Lattice Lock Dashboard Module

Provides real-time monitoring dashboard for Lattice Lock projects
with FastAPI backend, WebSocket support, and metrics aggregation.
"""

from .aggregator import (
    DataAggregator,
    DashboardSummary,
    ProjectInfo,
    Cache,
)
from .backend import (
    app,
    create_app,
    router,
    run_server,
    get_aggregator,
    get_ws_manager,
)
from .metrics import (
    MetricsCollector,
    MetricsSnapshot,
    ProjectHealthTrend,
)
from .websocket import (
    WebSocketManager,
    ConnectionInfo,
)

__all__ = [
    # Backend
    "app",
    "create_app",
    "router",
    "run_server",
    "get_aggregator",
    "get_ws_manager",
    # Aggregator
    "DataAggregator",
    "DashboardSummary",
    "ProjectInfo",
    "Cache",
    # Metrics
    "MetricsCollector",
    "MetricsSnapshot",
    "ProjectHealthTrend",
    # WebSocket
    "WebSocketManager",
    "ConnectionInfo",
]
