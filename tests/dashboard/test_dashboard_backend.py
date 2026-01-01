"""
Tests for the Lattice Lock Dashboard Backend.

Tests cover:
- MetricsCollector for validation metrics
- DataAggregator for project data aggregation
- FastAPI backend endpoints
- WebSocket connections for real-time updates
"""

import pytest
from fastapi.testclient import TestClient

from lattice_lock.dashboard.aggregator import DataAggregator
from lattice_lock.dashboard.backend import create_app
from lattice_lock.dashboard.metrics import MetricsCollector
from lattice_lock.dashboard.websocket import WebSocketManager

# ============================================================================
# Metrics Tests
# ============================================================================


class TestMetricsCollector:
    """Tests for the MetricsCollector class."""

    def test_initial_state(self):
        """Test initial state of a new collector."""
        collector = MetricsCollector()

        snapshot = collector.get_snapshot()
        assert snapshot.total_validations == 0
        assert snapshot.success_rate == 100.0
        assert snapshot.avg_response_time == 0.0
        assert snapshot.error_counts == {}
        assert snapshot.health_score == 100

    def test_record_successful_validation(self):
        """Test recording a successful validation."""
        collector = MetricsCollector()
        collector.record_validation(success=True, duration=0.1)

        snapshot = collector.get_snapshot()
        assert snapshot.total_validations == 1
        assert snapshot.success_rate == 100.0
        assert snapshot.avg_response_time == 0.1
        assert snapshot.health_score == 100

    def test_record_failed_validation(self):
        """Test recording a failed validation with error type."""
        collector = MetricsCollector()
        collector.record_validation(success=False, duration=0.5, error_type="validation_error")

        snapshot = collector.get_snapshot()
        assert snapshot.total_validations == 1
        assert snapshot.success_rate == 0.0
        assert snapshot.error_counts["validation_error"] == 1
        assert snapshot.health_score < 100

    def test_mixed_validations(self):
        """Test a mix of successful and failed validations."""
        collector = MetricsCollector()
        collector.record_validation(success=True, duration=0.1)
        collector.record_validation(success=False, duration=0.5, error_type="validation_error")

        snapshot = collector.get_snapshot()
        assert snapshot.total_validations == 2
        assert snapshot.success_rate == 50.0
        assert snapshot.error_counts["validation_error"] == 1
        assert snapshot.health_score < 100

    def test_multiple_error_types(self):
        """Test tracking multiple error types."""
        collector = MetricsCollector()
        collector.record_validation(success=False, duration=0.1, error_type="schema_error")
        collector.record_validation(success=False, duration=0.2, error_type="schema_error")
        collector.record_validation(success=False, duration=0.3, error_type="config_error")

        snapshot = collector.get_snapshot()
        assert snapshot.error_counts["schema_error"] == 2
        assert snapshot.error_counts["config_error"] == 1

    def test_response_time_percentiles(self):
        """Test response time percentile calculations."""
        collector = MetricsCollector()

        # Record 100 validations with increasing durations
        for i in range(100):
            collector.record_validation(success=True, duration=i * 0.01)

        snapshot = collector.get_snapshot()
        # P50 should be around 0.5
        assert 0.4 <= snapshot.response_time_p50 <= 0.6
        # P95 should be around 0.95
        assert snapshot.response_time_p95 > snapshot.response_time_p50
        # P99 should be around 0.99
        assert snapshot.response_time_p99 > snapshot.response_time_p95

    def test_project_specific_metrics(self):
        """Test recording metrics for specific projects."""
        collector = MetricsCollector()
        collector.record_validation(success=True, duration=0.1, project_id="proj1")
        collector.record_validation(success=False, duration=0.2, project_id="proj1")
        collector.record_validation(success=True, duration=0.1, project_id="proj2")

        # Check project-specific health trends
        trend = collector.get_project_health_trend("proj1")
        assert trend is not None
        assert trend.project_id == "proj1"
        assert len(trend.health_scores) >= 2

    def test_reset(self):
        """Test resetting the collector."""
        collector = MetricsCollector()
        collector.record_validation(success=True, duration=0.1)
        collector.record_validation(success=False, duration=0.2, error_type="error")

        collector.reset()

        snapshot = collector.get_snapshot()
        assert snapshot.total_validations == 0
        assert snapshot.error_counts == {}


# ============================================================================
# Aggregator Tests
# ============================================================================


class TestDataAggregator:
    """Tests for the DataAggregator class."""

    def test_initial_state(self):
        """Test initial state of a new aggregator."""
        agg = DataAggregator()
        summary = agg.get_project_summary()

        assert summary.total_projects == 0
        assert summary.healthy_projects == 0
        assert summary.at_risk_projects == 0

    def test_register_project(self):
        """Test registering a new project."""
        agg = DataAggregator()
        project = agg.register_project("proj1", name="Project One")

        assert project.id == "proj1"
        assert project.name == "Project One"
        assert project.status == "unknown"

    def test_update_project_status_healthy(self):
        """Test updating project status to healthy."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")

        summary = agg.get_project_summary()
        assert summary.total_projects == 1
        assert summary.healthy_projects == 1
        assert summary.at_risk_projects == 0

    def test_update_project_status_error(self):
        """Test updating project status to error."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "error")

        summary = agg.get_project_summary()
        assert summary.total_projects == 1
        assert summary.healthy_projects == 0
        assert summary.error_projects == 1

    def test_mixed_project_statuses(self):
        """Test aggregator with mixed project statuses."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")
        agg.update_project_status("proj2", "error")
        agg.update_project_status("proj3", "warning")

        summary = agg.get_project_summary()
        assert summary.total_projects == 3
        assert summary.healthy_projects == 1
        assert summary.error_projects == 1
        assert summary.at_risk_projects == 1

    def test_get_all_projects(self):
        """Test getting all projects list."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")
        agg.update_project_status("proj2", "error")

        projects = agg.get_all_projects()
        assert len(projects) == 2

        project_ids = [p["id"] for p in projects]
        assert "proj1" in project_ids
        assert "proj2" in project_ids

    def test_get_project(self):
        """Test getting a specific project."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")

        project = agg.get_project("proj1")
        assert project is not None
        assert project.id == "proj1"
        assert project.status == "healthy"

        # Non-existent project
        assert agg.get_project("nonexistent") is None

    def test_project_health_score(self):
        """Test project health score calculation."""
        agg = DataAggregator()

        # Healthy project should have high score
        agg.update_project_status("proj1", "healthy")
        project = agg.get_project("proj1")
        assert project.health_score >= 90

        # Error project should have lower score
        agg.update_project_status("proj2", "error")
        project = agg.get_project("proj2")
        assert project.health_score <= 50

    def test_caching(self):
        """Test that caching works for project summaries."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")

        # First call should compute
        summary1 = agg.get_project_summary()

        # Second call should return cached (within TTL)
        summary2 = agg.get_project_summary()

        # Both should have same data
        assert summary1.total_projects == summary2.total_projects

    def test_remove_project(self):
        """Test removing a project."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")
        agg.update_project_status("proj2", "healthy")

        assert agg.remove_project("proj1") is True
        assert agg.get_project("proj1") is None
        assert len(agg.get_all_projects()) == 1

        # Removing non-existent project
        assert agg.remove_project("nonexistent") is False

    def test_clear_all(self):
        """Test clearing all data."""
        agg = DataAggregator()
        agg.update_project_status("proj1", "healthy")
        agg.update_project_status("proj2", "error")

        agg.clear_all()

        assert len(agg.get_all_projects()) == 0
        summary = agg.get_project_summary()
        assert summary.total_projects == 0


# ============================================================================
# Backend Integration Tests
# ============================================================================


class TestDashboardBackend:
    """Tests for the FastAPI dashboard backend."""

    @pytest.fixture
    def client(self):
        """Create a test client without mock updates."""
        app = create_app(enable_mock_updates=False)
        # Use context manager to trigger lifespan events
        with TestClient(app) as client:
            yield client

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset global state before each test."""
        # State is now managed via app.state in lifespan, no global reset needed
        yield

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data

    def test_get_summary_empty(self, client):
        """Test getting summary with no projects."""
        response = client.get("/dashboard/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["total_projects"] == 0
        assert data["healthy_projects"] == 0
        assert data["at_risk_projects"] == 0

    def test_get_summary_with_projects(self, client):
        """Test getting summary with projects."""
        # Add some projects via update
        client.post("/dashboard/projects/proj1", json={"status": "healthy"})
        client.post("/dashboard/projects/proj2", json={"status": "error"})

        response = client.get("/dashboard/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["total_projects"] == 2
        assert data["healthy_projects"] == 1

    def test_get_projects_empty(self, client):
        """Test getting projects list when empty."""
        response = client.get("/dashboard/projects")
        assert response.status_code == 200

        data = response.json()
        assert data == []

    def test_get_projects_with_data(self, client):
        """Test getting projects list with data."""
        client.post("/dashboard/projects/proj1", json={"status": "healthy"})
        client.post("/dashboard/projects/proj2", json={"status": "error"})

        response = client.get("/dashboard/projects")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

        project_ids = [p["id"] for p in data]
        assert "proj1" in project_ids
        assert "proj2" in project_ids

    def test_get_specific_project(self, client):
        """Test getting a specific project."""
        client.post("/dashboard/projects/proj1", json={"status": "healthy"})

        response = client.get("/dashboard/projects/proj1")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "proj1"
        assert data["status"] == "healthy"

    def test_get_nonexistent_project(self, client):
        """Test getting a project that doesn't exist."""
        response = client.get("/dashboard/projects/nonexistent")
        assert response.status_code == 404

    def test_update_project_status(self, client):
        """Test updating a project's status."""
        response = client.post(
            "/dashboard/projects/proj1", json={"status": "healthy", "details": {"version": "1.0"}}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "proj1"
        assert data["status"] == "healthy"

    def test_get_metrics_empty(self, client):
        """Test getting metrics with no data."""
        response = client.get("/dashboard/metrics")
        assert response.status_code == 200

        data = response.json()
        assert data["total_validations"] == 0
        assert data["success_rate"] == 100.0
        assert data["health_score"] == 100

    def test_get_metrics_with_data(self, client):
        """Test getting metrics with validation data."""
        # Create some validations through project updates
        client.post("/dashboard/projects/proj1", json={"status": "healthy"})
        client.post("/dashboard/projects/proj1", json={"status": "error"})

        response = client.get("/dashboard/metrics")
        assert response.status_code == 200

        data = response.json()
        assert data["total_validations"] == 2
        assert data["success_rate"] < 100.0

    def test_get_connection_stats(self, client):
        """Test getting WebSocket connection statistics."""
        response = client.get("/dashboard/connections")
        assert response.status_code == 200

        data = response.json()
        assert "total_connections" in data
        assert "connections" in data
        assert data["total_connections"] == 0


# ============================================================================
# WebSocket Tests
# ============================================================================


class TestWebSocketManager:
    """Tests for the WebSocketManager class."""

    def test_initial_state(self):
        """Test initial state of WebSocket manager."""
        manager = WebSocketManager()

        assert manager.connection_count == 0
        assert manager.active_connections == []

    def test_connection_stats(self):
        """Test getting connection statistics."""
        manager = WebSocketManager()
        stats = manager.get_connection_stats()

        assert stats["total_connections"] == 0
        assert stats["connections"] == []


class TestWebSocketEndpoint:
    """Tests for the WebSocket endpoint."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Reset global state before each test."""
        # State is now managed via app.state in lifespan, no global reset needed
        yield

    def test_websocket_connection(self):
        """Test WebSocket connection establishment."""
        app = create_app(enable_mock_updates=False)

        with TestClient(app) as client:
            with client.websocket_connect("/dashboard/live") as websocket:
                # Should receive welcome message
                data = websocket.receive_json()
                assert data["type"] == "connected"
                assert "timestamp" in data

    def test_websocket_ping_pong(self):
        """Test WebSocket ping-pong."""
        app = create_app(enable_mock_updates=False)

        with TestClient(app) as client:
            with client.websocket_connect("/dashboard/live") as websocket:
                # Skip welcome message
                websocket.receive_json()

                # Send ping
                websocket.send_text("ping")

                # Should receive pong
                response = websocket.receive_text()
                assert response == "pong"

    def test_websocket_json_ping(self):
        """Test WebSocket JSON ping message."""
        app = create_app(enable_mock_updates=False)

        with TestClient(app) as client:
            with client.websocket_connect("/dashboard/live") as websocket:
                # Skip welcome message
                websocket.receive_json()

                # Send JSON ping
                websocket.send_json({"type": "ping"})

                # Should receive pong
                data = websocket.receive_json()
                assert data["type"] == "pong"
                assert "timestamp" in data


# ============================================================================
# OpenAPI Documentation Tests
# ============================================================================


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation availability."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        app = create_app(enable_mock_updates=False)
        return TestClient(app)

    def test_openapi_json(self, client):
        """Test OpenAPI JSON endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/dashboard/summary" in data["paths"]
        assert "/dashboard/projects" in data["paths"]
        assert "/dashboard/metrics" in data["paths"]

    def test_docs_endpoint(self, client):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
