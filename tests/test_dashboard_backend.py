"""
Unit tests for the Dashboard Backend module.

Tests data aggregation, WebSocket connections, and metrics calculation.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lattice_lock.dashboard.aggregator import (
    DataAggregator,
    HealthLevel,
    HealthScore,
    ProjectStatus,
    ValidationStatus,
)
from lattice_lock.dashboard.metrics import (
    ErrorMetrics,
    MetricsCollector,
    ValidationMetrics,
)
from lattice_lock.dashboard.websocket import (
    ConnectionManager,
    EventType,
    WebSocketManager,
    WebSocketMessage,
)


class TestHealthScore:
    """Tests for HealthScore calculation."""

    def test_healthy_score(self) -> None:
        """Test that high scores result in healthy level."""
        score = HealthScore.calculate(
            validation_success_rate=95.0,
            error_trend=-0.1,
            recent_failures=0,
            response_time_score=90.0,
        )
        assert score.level == HealthLevel.HEALTHY
        assert score.score >= 80.0

    def test_warning_score(self) -> None:
        """Test that medium scores result in warning level."""
        score = HealthScore.calculate(
            validation_success_rate=60.0,
            error_trend=0.5,
            recent_failures=3,
            response_time_score=50.0,
        )
        assert score.level == HealthLevel.WARNING
        assert 50.0 <= score.score < 80.0

    def test_critical_score(self) -> None:
        """Test that low scores result in critical level."""
        score = HealthScore.calculate(
            validation_success_rate=20.0,
            error_trend=1.0,
            recent_failures=10,
            response_time_score=20.0,
        )
        assert score.level == HealthLevel.CRITICAL
        assert score.score < 50.0

    def test_factors_are_recorded(self) -> None:
        """Test that all factors are recorded in the score."""
        score = HealthScore.calculate(
            validation_success_rate=80.0,
            error_trend=0.0,
            recent_failures=1,
            response_time_score=70.0,
        )
        assert "validation_success_rate" in score.factors
        assert "error_trend" in score.factors
        assert "recent_failures" in score.factors
        assert "response_time" in score.factors


class TestDataAggregator:
    """Tests for DataAggregator."""

    @pytest.fixture
    def aggregator(self) -> DataAggregator:
        """Create a DataAggregator instance."""
        return DataAggregator(cache_ttl_seconds=1)

    @pytest.mark.asyncio
    async def test_register_project(self, aggregator: DataAggregator) -> None:
        """Test project registration."""
        status = await aggregator.register_project(
            project_id="test-project",
            name="Test Project",
            path="/path/to/project",
        )
        assert status.project_id == "test-project"
        assert status.name == "Test Project"
        assert status.health.level == HealthLevel.UNKNOWN

    @pytest.mark.asyncio
    async def test_register_project_idempotent(self, aggregator: DataAggregator) -> None:
        """Test that registering the same project twice returns the same status."""
        status1 = await aggregator.register_project(
            project_id="test-project",
            name="Test Project",
            path="/path/to/project",
        )
        status2 = await aggregator.register_project(
            project_id="test-project",
            name="Different Name",
            path="/different/path",
        )
        assert status1 is status2

    @pytest.mark.asyncio
    async def test_record_validation(self, aggregator: DataAggregator) -> None:
        """Test recording validation results."""
        await aggregator.register_project(
            project_id="test-project",
            name="Test Project",
            path="/path/to/project",
        )
        
        await aggregator.record_validation(
            project_id="test-project",
            passed=True,
            error_count=0,
            warning_count=2,
            duration_ms=150.0,
            validator_type="schema",
        )
        
        project = await aggregator.get_project_status("test-project")
        assert project is not None
        assert project.last_validation is not None
        assert project.last_validation.passed is True
        assert project.last_validation.error_count == 0
        assert project.last_validation.warning_count == 2

    @pytest.mark.asyncio
    async def test_get_summary_empty(self, aggregator: DataAggregator) -> None:
        """Test summary with no projects."""
        summary = await aggregator.get_summary()
        assert summary["total_projects"] == 0
        assert summary["overall_health"] == 100.0

    @pytest.mark.asyncio
    async def test_get_summary_with_projects(self, aggregator: DataAggregator) -> None:
        """Test summary with registered projects."""
        await aggregator.register_project("p1", "Project 1", "/p1")
        await aggregator.register_project("p2", "Project 2", "/p2")
        
        summary = await aggregator.get_summary()
        assert summary["total_projects"] == 2

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, aggregator: DataAggregator) -> None:
        """Test that cache is invalidated after recording validation."""
        await aggregator.register_project("p1", "Project 1", "/p1")
        
        # Get summary to populate cache
        summary1 = await aggregator.get_summary()
        
        # Record validation (should invalidate cache)
        await aggregator.record_validation(
            project_id="p1",
            passed=False,
            error_count=5,
            warning_count=0,
            duration_ms=100.0,
            validator_type="schema",
        )
        
        # Get summary again
        summary2 = await aggregator.get_summary()
        assert summary2["total_errors"] == 5

    @pytest.mark.asyncio
    async def test_get_error_trends(self, aggregator: DataAggregator) -> None:
        """Test error trend calculation."""
        await aggregator.register_project("p1", "Project 1", "/p1")
        
        # Record some validations
        for i in range(5):
            await aggregator.record_validation(
                project_id="p1",
                passed=i % 2 == 0,
                error_count=i,
                warning_count=0,
                duration_ms=100.0,
                validator_type="schema",
            )
        
        trends = await aggregator.get_error_trends(hours=24)
        assert trends["total_validations"] == 5
        assert trends["total_errors"] == 10  # 0+1+2+3+4


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        """Create a MetricsCollector instance."""
        return MetricsCollector(retention_hours=24)

    def test_record_validation(self, collector: MetricsCollector) -> None:
        """Test recording validation metrics."""
        collector.record_validation(
            passed=True,
            error_count=0,
            warning_count=1,
            duration_ms=150.0,
            validator_type="schema",
        )
        
        metrics = collector.get_validation_metrics()
        assert metrics.total_validations == 1
        assert metrics.successful_validations == 1
        assert metrics.failed_validations == 0

    def test_success_rate_calculation(self, collector: MetricsCollector) -> None:
        """Test success rate calculation."""
        for i in range(10):
            collector.record_validation(
                passed=i < 7,  # 7 successes, 3 failures
                error_count=0 if i < 7 else 1,
                warning_count=0,
                duration_ms=100.0,
                validator_type="schema",
            )
        
        metrics = collector.get_validation_metrics()
        assert metrics.success_rate == 70.0
        assert metrics.failure_rate == 30.0

    def test_percentile_calculation(self, collector: MetricsCollector) -> None:
        """Test response time percentile calculation."""
        durations = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        for d in durations:
            collector.record_validation(
                passed=True,
                error_count=0,
                warning_count=0,
                duration_ms=float(d),
                validator_type="schema",
            )
        
        metrics = collector.get_validation_metrics()
        assert metrics.p50_duration_ms > 0
        assert metrics.p95_duration_ms > metrics.p50_duration_ms
        assert metrics.p99_duration_ms >= metrics.p95_duration_ms

    def test_error_metrics(self, collector: MetricsCollector) -> None:
        """Test error metrics collection."""
        collector.record_validation(
            passed=False,
            error_count=2,
            warning_count=0,
            duration_ms=100.0,
            validator_type="schema",
            error_types=["missing_field", "invalid_type"],
        )
        collector.record_validation(
            passed=False,
            error_count=1,
            warning_count=0,
            duration_ms=100.0,
            validator_type="schema",
            error_types=["missing_field"],
        )
        
        error_metrics = collector.get_error_metrics()
        assert error_metrics.error_counts["missing_field"] == 2
        assert error_metrics.error_counts["invalid_type"] == 1

    def test_validator_breakdown(self, collector: MetricsCollector) -> None:
        """Test metrics breakdown by validator type."""
        collector.record_validation(
            passed=True,
            error_count=0,
            warning_count=0,
            duration_ms=100.0,
            validator_type="schema",
        )
        collector.record_validation(
            passed=True,
            error_count=0,
            warning_count=0,
            duration_ms=200.0,
            validator_type="env",
        )
        
        breakdown = collector.get_validator_breakdown()
        assert "schema" in breakdown
        assert "env" in breakdown
        assert breakdown["schema"]["total"] == 1
        assert breakdown["env"]["total"] == 1

    def test_health_snapshot(self, collector: MetricsCollector) -> None:
        """Test health snapshot recording."""
        collector.record_health_snapshot(
            score=85.0,
            level="healthy",
            project_count=5,
        )
        
        trends = collector.get_health_trends(hours=24)
        assert len(trends) == 1
        assert trends[0]["score"] == 85.0
        assert trends[0]["level"] == "healthy"


class TestValidationMetrics:
    """Tests for ValidationMetrics dataclass."""

    def test_success_rate_empty(self) -> None:
        """Test success rate with no validations."""
        metrics = ValidationMetrics()
        assert metrics.success_rate == 100.0
        assert metrics.failure_rate == 0.0

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        metrics = ValidationMetrics(
            total_validations=10,
            successful_validations=8,
            failed_validations=2,
            total_errors=5,
            total_warnings=3,
            avg_duration_ms=150.5,
            p50_duration_ms=100.0,
            p95_duration_ms=300.0,
            p99_duration_ms=500.0,
        )
        
        d = metrics.to_dict()
        assert d["total_validations"] == 10
        assert d["success_rate"] == 80.0
        assert d["failure_rate"] == 20.0


class TestWebSocketMessage:
    """Tests for WebSocketMessage."""

    def test_to_json(self) -> None:
        """Test JSON serialization."""
        msg = WebSocketMessage(
            event_type=EventType.VALIDATION_COMPLETE,
            data={"project_id": "test", "passed": True},
        )
        
        json_str = msg.to_json()
        assert "validation_complete" in json_str
        assert "project_id" in json_str

    def test_from_json(self) -> None:
        """Test JSON deserialization."""
        msg = WebSocketMessage(
            event_type=EventType.HEALTH_UPDATED,
            data={"overall_health": 85.0},
        )
        
        json_str = msg.to_json()
        parsed = WebSocketMessage.from_json(json_str)
        
        assert parsed.event_type == EventType.HEALTH_UPDATED
        assert parsed.data["overall_health"] == 85.0


class TestConnectionManager:
    """Tests for ConnectionManager."""

    @pytest.fixture
    def manager(self) -> ConnectionManager:
        """Create a ConnectionManager instance."""
        return ConnectionManager(heartbeat_interval=1.0, connection_timeout=5.0)

    @pytest.mark.asyncio
    async def test_connect_disconnect(self, manager: ConnectionManager) -> None:
        """Test connection and disconnection."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        mock_ws.close = AsyncMock()
        
        await manager.connect("conn-1", mock_ws)
        assert manager.get_connection_count() == 1
        
        await manager.disconnect("conn-1")
        assert manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_send_to(self, manager: ConnectionManager) -> None:
        """Test sending message to specific connection."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await manager.connect("conn-1", mock_ws)
        
        # Reset mock after connection (which sends connection_established message)
        mock_ws.send_text.reset_mock()
        
        msg = WebSocketMessage(
            event_type=EventType.HEARTBEAT,
            data={},
        )
        
        result = await manager.send_to("conn-1", msg)
        assert result is True
        mock_ws.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_nonexistent(self, manager: ConnectionManager) -> None:
        """Test sending to non-existent connection."""
        msg = WebSocketMessage(event_type=EventType.HEARTBEAT, data={})
        result = await manager.send_to("nonexistent", msg)
        assert result is False

    @pytest.mark.asyncio
    async def test_broadcast(self, manager: ConnectionManager) -> None:
        """Test broadcasting to all connections."""
        mock_ws1 = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_text = AsyncMock()
        
        await manager.connect("conn-1", mock_ws1)
        await manager.connect("conn-2", mock_ws2)
        
        msg = WebSocketMessage(event_type=EventType.HEALTH_UPDATED, data={})
        sent_count = await manager.broadcast(msg)
        
        assert sent_count == 2
        mock_ws1.send_text.assert_called()
        mock_ws2.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self, manager: ConnectionManager) -> None:
        """Test broadcasting with exclusions."""
        mock_ws1 = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_text = AsyncMock()
        
        await manager.connect("conn-1", mock_ws1)
        await manager.connect("conn-2", mock_ws2)
        
        # Reset mocks after connection (which sends connection_established messages)
        mock_ws1.send_text.reset_mock()
        mock_ws2.send_text.reset_mock()
        
        msg = WebSocketMessage(event_type=EventType.HEALTH_UPDATED, data={})
        sent_count = await manager.broadcast(msg, exclude={"conn-1"})
        
        assert sent_count == 1
        mock_ws1.send_text.assert_not_called()
        mock_ws2.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_get_connection_info(self, manager: ConnectionManager) -> None:
        """Test getting connection information."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await manager.connect("conn-1", mock_ws)
        
        info = manager.get_connection_info()
        assert len(info) == 1
        assert info[0]["connection_id"] == "conn-1"
        assert "connected_at" in info[0]
        assert "message_count" in info[0]


class TestWebSocketManager:
    """Tests for WebSocketManager."""

    @pytest.fixture
    def ws_manager(self) -> WebSocketManager:
        """Create a WebSocketManager instance."""
        return WebSocketManager()

    @pytest.mark.asyncio
    async def test_connect_with_topics(self, ws_manager: WebSocketManager) -> None:
        """Test connecting with topic subscriptions."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await ws_manager.connect(
            connection_id="conn-1",
            websocket=mock_ws,
            topics=["project-updates", "errors"],
        )
        
        stats = ws_manager.get_stats()
        assert stats["active_connections"] == 1
        assert "project-updates" in stats["topics"]
        assert "errors" in stats["topics"]

    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self, ws_manager: WebSocketManager) -> None:
        """Test topic subscription and unsubscription."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await ws_manager.connect("conn-1", mock_ws)
        
        await ws_manager.subscribe("conn-1", "new-topic")
        stats = ws_manager.get_stats()
        assert "new-topic" in stats["topics"]
        
        await ws_manager.unsubscribe("conn-1", "new-topic")
        stats = ws_manager.get_stats()
        assert stats["topics"].get("new-topic", 0) == 0

    @pytest.mark.asyncio
    async def test_broadcast_validation_complete(self, ws_manager: WebSocketManager) -> None:
        """Test broadcasting validation completion."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await ws_manager.connect("conn-1", mock_ws)
        
        sent = await ws_manager.broadcast_validation_complete(
            project_id="test-project",
            passed=True,
            error_count=0,
            warning_count=1,
            duration_ms=150.0,
        )
        
        assert sent == 1
        mock_ws.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_health_updated(self, ws_manager: WebSocketManager) -> None:
        """Test broadcasting health update."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await ws_manager.connect("conn-1", mock_ws)
        
        sent = await ws_manager.broadcast_health_updated(
            overall_health=85.0,
            healthy_count=3,
            warning_count=1,
            critical_count=0,
        )
        
        assert sent == 1

    @pytest.mark.asyncio
    async def test_broadcast_error_detected(self, ws_manager: WebSocketManager) -> None:
        """Test broadcasting error detection."""
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await ws_manager.connect("conn-1", mock_ws)
        
        sent = await ws_manager.broadcast_error_detected(
            project_id="test-project",
            error_type="validation_error",
            error_message="Missing required field",
            severity="high",
        )
        
        assert sent == 1


class TestProjectStatus:
    """Tests for ProjectStatus."""

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        health = HealthScore(
            score=85.0,
            level=HealthLevel.HEALTHY,
            factors={"validation_success_rate": 90.0},
        )
        
        validation = ValidationStatus(
            timestamp=datetime.utcnow(),
            passed=True,
            error_count=0,
            warning_count=1,
            duration_ms=150.0,
            validator_type="schema",
        )
        
        status = ProjectStatus(
            project_id="test-project",
            name="Test Project",
            path="/path/to/project",
            health=health,
            last_validation=validation,
            error_count=0,
            warning_count=1,
        )
        
        d = status.to_dict()
        assert d["project_id"] == "test-project"
        assert d["name"] == "Test Project"
        assert d["health"]["score"] == 85.0
        assert d["health"]["level"] == "healthy"
        assert d["last_validation"]["passed"] is True

    def test_to_dict_no_validation(self) -> None:
        """Test conversion with no validation history."""
        health = HealthScore(
            score=100.0,
            level=HealthLevel.UNKNOWN,
            factors={},
        )
        
        status = ProjectStatus(
            project_id="test-project",
            name="Test Project",
            path="/path/to/project",
            health=health,
            last_validation=None,
        )
        
        d = status.to_dict()
        assert d["last_validation"] is None
