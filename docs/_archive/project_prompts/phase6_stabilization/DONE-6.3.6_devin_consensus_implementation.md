# Task 6.3.6 - Consensus Strategy Implementation

**Tool:** Devin AI
**Phase:** 6.3 - Orchestrator Feature Completeness
**Dependencies:** 6.3.5 (Multi-Model Consensus Strategy Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.3.6 - Consensus Strategy Implementation

### Context

- Design doc from 6.3.5 specifies the consensus strategy (refer to that output)
- Files to create/modify:
  - `src/lattice_lock_orchestrator/consensus.py` - New module
  - `src/lattice_lock_orchestrator/core.py` - Integration
  - `scripts/orchestrator_cli.py` - CLI command

### Goals

1. Implement `ConsensusStrategy` class:
   - Select models for consensus
   - Execute parallel requests
   - Reconcile results using specified method

2. Implement reconciliation methods:
   - At minimum: majority vote
   - Optional: LLM-as-judge, merge

3. Integrate with `ModelOrchestrator`:
   - Add `route_with_consensus()` method
   - Support consensus via routing strategy flag

4. Update CLI:
   - Make `consensus` command functional
   - Add options for num models, reconciliation method
   - Display individual responses and final answer

5. Add tests:
   - Test model selection for consensus
   - Test reconciliation methods
   - Test CLI output
   - Mock API calls for testing

### Constraints

- Must not break existing functionality
- Handle partial failures (some models fail)
- Clear output showing consensus process
- Tests must pass before PR

### Output

- New file: `src/lattice_lock_orchestrator/consensus.py`
- Modified: `src/lattice_lock_orchestrator/core.py`
- Modified: `scripts/orchestrator_cli.py`
- New tests: `tests/test_consensus.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `ConsensusStrategy` executes multi-model requests
- [ ] At least one reconciliation method works
- [ ] `orchestrator_cli.py consensus "question"` works
- [ ] Partial failures handled gracefully
- [ ] All existing tests still pass
- [ ] New tests cover consensus scenarios
