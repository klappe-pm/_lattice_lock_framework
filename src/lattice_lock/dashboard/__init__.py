"""
Lattice Lock Dashboard Module

Provides a backend for the Admin Dashboard with data aggregation,
real-time updates via WebSocket, and metrics calculation.

Usage:
    from lattice_lock.dashboard import DashboardBackend, create_app
    
    app = create_app()
    # Run with: uvicorn lattice_lock.dashboard:app --reload
"""

from .aggregator import DataAggregator, ProjectStatus, HealthScore
from .metrics import MetricsCollector, ValidationMetrics, ErrorMetrics
from .websocket import WebSocketManager, ConnectionManager
from .backend import create_app, DashboardBackend

__all__ = [
    "DataAggregator",
    "ProjectStatus",
    "HealthScore",
    "MetricsCollector",
    "ValidationMetrics",
    "ErrorMetrics",
    "WebSocketManager",
    "ConnectionManager",
    "create_app",
    "DashboardBackend",
]
