# Task 6.1.2 - Align ModelCapabilities and CLI Implementation

**Tool:** Devin AI
**Phase:** 6.1 - Breaking Issues / Orchestrator Contract Hardening
**Dependencies:** 6.1.1 (Orchestrator Capabilities Contract Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.1.2 - Align ModelCapabilities and CLI Implementation

### Context

- Design doc from 6.1.1 specifies the contract (refer to that output)
- Files to modify:
  - `src/lattice_lock_orchestrator/types.py`
  - `src/lattice_lock_orchestrator/registry.py`
  - `scripts/orchestrator_cli.py`

### Current Issues

The CLI references attributes that don't exist on `ModelCapabilities`:
- `model.supports_reasoning` (line 86)
- `model.code_specialized` (line 88)
- `model.task_scores` (lines 95, 150)
- `TaskType.VISION` (line 277)

### Goals

1. Implement the agreed contract from the 6.1.1 design doc:
   - Add missing fields to `ModelCapabilities` dataclass
   - Update `TaskType` enum as specified
   - Ensure all fields have appropriate defaults

2. Fix `TaskType.VISION` usage:
   - Either add `VISION` to the enum (if design doc recommends)
   - Or remove/replace references in CLI

3. Update model definitions in registry:
   - Ensure all registered models have the new required fields
   - Use safe defaults where values are unknown

4. Add unit tests ensuring:
   - CLI 'list' command doesn't crash on missing attributes
   - CLI 'analyze' command works for all task types
   - All models in registry have valid capabilities
   - Vision tasks either route correctly or are clearly not supported

### Constraints

- Must not break existing functionality
- All new fields need safe defaults for backwards compatibility
- Tests must pass before PR
- Follow existing code style and patterns

### Output

- Modified files with clear diffs
- New test file: `tests/test_model_capabilities.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `python scripts/orchestrator_cli.py list --verbose` runs without errors
- [ ] `python scripts/orchestrator_cli.py analyze "Write a Python function"` works
- [ ] All existing tests still pass
- [ ] New tests cover the fixed attributes
- [ ] No `AttributeError` when accessing model capabilities
