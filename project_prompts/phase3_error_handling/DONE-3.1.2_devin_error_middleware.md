# Prompt 3.1.2 - Error Handling Middleware

**Tool:** Devin AI
**Epic:** 3.1 - Error Boundary System
**Phase:** 3 - Error Handling & Admin

## Context

The error classification system needs middleware that intercepts errors, classifies them, logs them appropriately, and triggers recovery actions. This middleware integrates with all framework components.

## Goal

Implement error handling middleware that provides consistent error handling across the framework.

## Steps

1. Create `src/lattice_lock/errors/middleware.py`:
   - Error interception decorator
   - Automatic classification
   - Logging integration
   - Recovery action triggering

2. Implement error boundary decorator:
   ```python
   @error_boundary(
       recoverable_errors=[SchemaValidationError],
       on_error=handle_validation_error
   )
   def validate_schema(path: str) -> ValidationResult:
       ...
   ```

3. Implement logging integration:
   - Structured logging with error context
   - Log level based on severity
   - Include stack traces for debugging
   - Redact sensitive information

4. Implement recovery actions:
   - Retry logic for transient errors
   - Fallback strategies
   - Graceful degradation

5. Add telemetry hooks:
   - Error count metrics
   - Error rate tracking
   - Alert thresholds

6. Write unit tests in `tests/test_error_middleware.py`:
   - Test error interception
   - Test classification accuracy
   - Test recovery actions

## Do NOT Touch

- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- Errors consistently handled across framework
- Logging provides actionable information
- Recovery actions work correctly
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Python's logging module
- Consider structlog for structured logging
