# Prompt 3.4.1 - Dashboard Backend

**Tool:** Codex CLI
**Epic:** 3.4 - Admin Dashboard
**Phase:** 3 - Error Handling & Admin

## Context

The Admin Dashboard needs a backend that aggregates data from multiple sources and provides real-time updates. This backend serves the dashboard frontend with project status, metrics, and alerts.

## Goal

Implement the dashboard backend with data aggregation and real-time updates.

## Steps

1. Create `src/lattice_lock/dashboard/` module:
   ```
   dashboard/
   ├── __init__.py
   ├── backend.py
   ├── aggregator.py
   ├── websocket.py
   └── metrics.py
   ```

2. Create `aggregator.py`:
   - Collect validation status from all projects
   - Aggregate error counts and trends
   - Calculate health scores
   - Cache results for performance

3. Create `websocket.py`:
   - WebSocket endpoint for real-time updates
   - Event broadcasting for status changes
   - Connection management
   - Heartbeat/keepalive

4. Create `metrics.py`:
   - Validation success/failure rates
   - Error frequency by type
   - Response time percentiles
   - Project health trends

5. Create `backend.py` with endpoints:
   - `GET /dashboard/summary` - Overall summary
   - `GET /dashboard/projects` - Project list with status
   - `GET /dashboard/metrics` - Metrics data
   - `WS /dashboard/live` - Real-time updates

6. Write unit tests in `tests/test_dashboard_backend.py`:
   - Test data aggregation
   - Test WebSocket connections
   - Test metrics calculation

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Dashboard backend serves aggregated data
- Real-time updates work via WebSocket
- Metrics are accurate and timely
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use FastAPI with WebSocket support
- Consider Redis for caching if needed
