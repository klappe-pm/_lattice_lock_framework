# Task 6.3.4 - Cost Tracking Implementation

**Tool:** Devin AI
**Phase:** 6.3 - Orchestrator Feature Completeness
**Dependencies:** 6.3.3 (Cost & Telemetry Strategy Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.3.4 - Cost Tracking Implementation

### Context

- Design doc from 6.3.3 specifies the cost tracking strategy (refer to that output)
- Files to create/modify:
  - `src/lattice_lock_orchestrator/cost_tracker.py` - New module
  - `src/lattice_lock_orchestrator/core.py` - Integration
  - `scripts/orchestrator_cli.py` - CLI commands

### Goals

1. Implement `CostTracker` class:
   - Record usage after each API call
   - Store data according to design doc strategy
   - Provide aggregation methods

2. Integrate with `ModelOrchestrator`:
   - Record usage in `_call_model()` method
   - Extract token counts from API responses
   - Handle providers that don't return counts

3. Implement CLI commands:
   - `orchestrator_cli.py cost` - Show session cost
   - `orchestrator_cli.py cost --detailed` - Show breakdown
   - Replace "not yet implemented" message

4. Add tests:
   - Test usage recording
   - Test cost aggregation
   - Test CLI output
   - Test persistence (if applicable)

### Constraints

- Must not break existing functionality
- Minimal performance impact on API calls
- Clear output formatting
- Tests must pass before PR

### Output

- New file: `src/lattice_lock_orchestrator/cost_tracker.py`
- Modified: `src/lattice_lock_orchestrator/core.py`
- Modified: `scripts/orchestrator_cli.py`
- New tests: `tests/test_cost_tracker.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `CostTracker` records usage correctly
- [ ] `orchestrator_cli.py cost` shows actual costs
- [ ] Cost breakdown by model/provider works
- [ ] All existing tests still pass
- [ ] New tests cover cost tracking scenarios
