import pytest
import time
from aiohttp import web
from lattice_lock.dashboard.metrics import MetricsCollector
from lattice_lock.dashboard.aggregator import DataAggregator
from lattice_lock.dashboard.backend import create_app

# Metrics Tests
def test_metrics_collector():
    collector = MetricsCollector()
    collector.record_validation(True, 0.1)
    collector.record_validation(False, 0.5, "validation_error")
    
    snapshot = collector.get_snapshot()
    assert snapshot.total_validations == 2
    assert snapshot.success_rate == 50.0
    assert snapshot.error_counts["validation_error"] == 1
    assert snapshot.health_score < 100

# Aggregator Tests
def test_aggregator():
    agg = DataAggregator()
    agg.update_project_status("proj1", "healthy")
    agg.update_project_status("proj2", "error")
    
    summary = agg.get_project_summary()
    assert summary["total_projects"] == 2
    assert summary["healthy_projects"] == 1
    assert summary["at_risk_projects"] == 1
    
    projects = agg.get_all_projects()
    assert len(projects) == 2
    assert projects[0]["id"] == "proj1"

# Backend Integration Tests
from aiohttp.test_utils import TestServer, TestClient
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    app = create_app()
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_backend_summary(client):
    resp = await client.get('/dashboard/summary')
    assert resp.status == 200
    data = await resp.json()
    assert "total_projects" in data

@pytest.mark.asyncio
async def test_backend_metrics(client):
    resp = await client.get('/dashboard/metrics')
    assert resp.status == 200
    data = await resp.json()
    assert "health_score" in data

@pytest.mark.asyncio
async def test_websocket_connection(client):
    async with client.ws_connect('/dashboard/live') as ws:
        await ws.send_str('ping')
        msg = await ws.receive_str()
        assert msg == 'pong'
        
        # We can't easily test broadcast here without triggering it from backend
        # but connection establishment proves it works.
