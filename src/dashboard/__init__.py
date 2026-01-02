"""
Lattice Lock Dashboard Module

Provides real-time monitoring dashboard for Lattice Lock projects
with FastAPI backend, WebSocket support, and metrics aggregation.
"""

from .aggregator import Cache, DashboardSummary, DataAggregator, ProjectInfo
from .backend import app, create_app, get_aggregator, get_ws_manager, router, run_server
from .generator import DashboardGenerator
from .metrics import MetricsCollector, MetricsSnapshot, ProjectHealthTrend
from .websocket import ConnectionInfo, WebSocketManager

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
    # Generator
    "DashboardGenerator",
]
