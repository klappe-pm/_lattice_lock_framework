# Prompt 3.3.2 - Admin Authentication

**Tool:** Claude Code App
**Epic:** 3.3 - Admin API
**Phase:** 3 - Error Handling & Admin

## Context

The Admin API needs authentication to protect administrative endpoints. The framework specification requires OAuth2/JWT authentication for admin endpoints.

## Goal

Implement authentication for the Admin API using OAuth2/JWT.

## Steps

1. Create `src/lattice_lock/admin/auth.py`:
   - JWT token generation and validation
   - OAuth2 password flow support
   - API key authentication (alternative)
   - Role-based access control

2. Implement JWT authentication:
   - Token generation with configurable expiry
   - Token validation middleware
   - Refresh token support
   - Token revocation

3. Implement API key authentication:
   - API key generation
   - Key storage and validation
   - Key rotation support

4. Add authentication to routes:
   ```python
   @router.get("/projects", dependencies=[Depends(verify_token)])
   async def list_projects():
       ...
   ```

5. Implement role-based access:
   - `admin` role: full access
   - `viewer` role: read-only access
   - `operator` role: can trigger rollbacks

6. Write unit tests in `tests/test_admin_auth.py`:
   - Test token generation
   - Test token validation
   - Test role-based access
   - Test API key authentication

## Do NOT Touch

- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/commands/init.py` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- JWT authentication works correctly
- API key authentication works as alternative
- Role-based access enforced
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use python-jose for JWT handling
- Never log or expose tokens/keys
