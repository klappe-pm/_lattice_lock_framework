# Task 6.1.4 - Provider Client Hardening & Bedrock Behavior

**Tool:** Devin AI
**Phase:** 6.1 - Breaking Issues / Orchestrator Contract Hardening
**Dependencies:** 6.1.3 (Provider Client and Fallback Strategy Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.1.4 - Provider Client Hardening & Bedrock Behavior

### Context

- Design doc from 6.1.3 specifies the provider strategy (refer to that output)
- Files to modify:
  - `src/lattice_lock_orchestrator/api_clients.py`
  - `src/lattice_lock_orchestrator/registry.py`
  - `src/lattice_lock_orchestrator/core.py`
  - `src/lattice_lock_orchestrator/types.py` (if adding provider status)

### Current Issues

- `BedrockClient._call_api()` raises `NotImplementedError`
- No validation of provider availability before model selection
- Silent failures possible when credentials are missing
- Fallback behavior unclear when provider fails

### Goals

1. Implement the provider strategy from 6.1.3 design doc:
   - Either implement minimal Bedrock client OR gate behind feature flag
   - Add provider maturity/status field if specified
   - Implement credential validation

2. Add provider availability checks:
   - Validate required environment variables at startup
   - Log warnings for unavailable providers
   - Exclude unavailable providers from model selection

3. Improve fallback behavior:
   - Ensure fallback chains skip unavailable providers
   - Add clear error messages when no providers available
   - Log fallback attempts for debugging

4. Add tests verifying:
   - All registered models have working clients OR are safely skipped
   - Fallback behavior when primary provider fails
   - Proper error messages for missing credentials
   - Bedrock behavior matches design doc decision

### Constraints

- Must not break existing functionality for working providers
- Graceful degradation when providers unavailable
- Clear error messages for users
- Tests must pass before PR

### Output

- Modified files with clear diffs
- New/updated tests in `tests/test_api_clients.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] No `NotImplementedError` raised during normal operation
- [ ] Missing credentials produce clear warning, not crash
- [ ] Fallback chains work when primary provider unavailable
- [ ] All existing tests still pass
- [ ] New tests cover provider availability scenarios
