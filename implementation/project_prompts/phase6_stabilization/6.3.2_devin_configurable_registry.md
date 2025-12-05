# Task 6.3.2 - Configurable Registry Implementation

**Tool:** Devin AI
**Phase:** 6.3 - Orchestrator Feature Completeness
**Dependencies:** 6.3.1 (Model Registry Source-of-Truth Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.3.2 - Configurable Registry Implementation

### Context

- Design doc from 6.3.1 specifies the registry format (refer to that output)
- Files to modify:
  - `models/model_registry.yaml` - New config file to create
  - `src/lattice_lock_orchestrator/registry.py` - Update loading logic
  - `src/lattice_lock_orchestrator/types.py` - Add any new fields

### Goals

1. Create `models/model_registry.yaml`:
   - Convert documented models from `model_registry.md` to YAML format
   - Include all 63 documented models (or subset based on design doc)
   - Follow schema from 6.3.1 design doc

2. Update `ModelRegistry` class:
   - Add `load_from_yaml()` method
   - Replace hardcoded `_load_*_models()` methods with config-driven loading
   - Add validation for registry format
   - Handle missing/malformed config gracefully

3. Add registry validation:
   - Validate required fields present
   - Validate field types
   - Validate provider references
   - Clear error messages for invalid entries

4. Add tests:
   - Test loading valid registry
   - Test error handling for malformed registry
   - Test all documented models load successfully
   - Test model lookup by ID and provider

### Constraints

- Must not break existing functionality
- Graceful fallback if YAML file missing (use hardcoded defaults)
- Clear error messages for configuration issues
- Tests must pass before PR

### Output

- New file: `models/model_registry.yaml`
- Modified: `src/lattice_lock_orchestrator/registry.py`
- New/updated tests: `tests/test_model_registry.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `models/model_registry.yaml` contains all documented models
- [ ] Registry loads from YAML successfully
- [ ] Invalid YAML produces clear error messages
- [ ] All existing tests still pass
- [ ] New tests cover registry loading scenarios
- [ ] `orchestrator_cli.py list` shows all models from YAML
