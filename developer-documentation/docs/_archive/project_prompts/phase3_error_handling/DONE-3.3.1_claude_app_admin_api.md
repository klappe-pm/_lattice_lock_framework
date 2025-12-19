# Prompt 3.3.1 - Admin API Endpoints

**Tool:** Claude Code App
**Epic:** 3.3 - Admin API
**Phase:** 3 - Error Handling & Admin

## Context

The Lattice Lock Framework needs an Admin API for monitoring project status, viewing errors, and triggering administrative actions. The API should be RESTful and support the endpoints defined in the framework specification.

## Goal

Implement the Admin API REST endpoints for project management and monitoring.

## Steps

1. Create `src/lattice_lock/admin/` module:
   ```
   admin/
   ├── __init__.py
   ├── api.py
   ├── routes.py
   ├── models.py
   └── schemas.py
   ```

2. Create `routes.py` with endpoints:
   - `GET /api/v1/projects` - List all registered projects
   - `GET /api/v1/projects/{id}/status` - Project health and validation status
   - `GET /api/v1/projects/{id}/errors` - Recent errors and incidents
   - `POST /api/v1/projects/{id}/rollback` - Trigger rollback to previous state
   - `GET /api/v1/health` - API health check

3. Create `schemas.py` with Pydantic models:
   - `ProjectListResponse`
   - `ProjectStatusResponse`
   - `ErrorListResponse`
   - `RollbackRequest`
   - `RollbackResponse`

4. Create `api.py` with FastAPI app:
   - CORS configuration
   - Error handling middleware
   - Request logging
   - OpenAPI documentation

5. Add CLI command to start admin server:
   ```python
   @click.command()
   @click.option('--port', default=8080)
   def admin_server(port):
       ...
   ```

6. Write unit tests in `tests/test_admin_api.py`:
   - Test each endpoint
   - Test error responses
   - Test authentication (if enabled)

## Do NOT Touch

- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/commands/init.py` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- All endpoints return correct responses
- API documentation auto-generated
- Error handling consistent
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use FastAPI for the API framework
- Follow REST best practices
