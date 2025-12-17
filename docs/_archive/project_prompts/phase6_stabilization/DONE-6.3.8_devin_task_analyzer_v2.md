# Task 6.3.8 - Task Analyzer v2 Implementation

**Tool:** Devin AI
**Phase:** 6.3 - Orchestrator Feature Completeness
**Dependencies:** 6.3.7 (Task Analyzer v2 Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.3.8 - Task Analyzer v2 Implementation

### Context

- Design doc from 6.3.7 specifies the improved analyzer (refer to that output)
- Files to modify:
  - `src/lattice_lock_orchestrator/scorer.py` - Update analyzer
  - `src/lattice_lock_orchestrator/types.py` - Add any new types

### Goals

1. Implement improved `TaskAnalyzer`:
   - Better pattern matching (not just simple keywords)
   - Context-aware classification
   - Confidence scores per task type

2. Add `get_task_scores()` method:
   - Return dict mapping TaskType to confidence (0.0-1.0)
   - Support multi-label classification

3. Create curated test set:
   - At least 50 labeled prompts
   - Cover all task types
   - Include edge cases and ambiguous prompts

4. Add comprehensive tests:
   - Test each task type detection
   - Test confidence scoring
   - Test edge cases
   - Measure accuracy against test set

### Constraints

- Must not break existing functionality
- Maintain backwards compatibility with existing interface
- No external dependencies (unless design doc specifies)
- Tests must pass before PR

### Output

- Modified: `src/lattice_lock_orchestrator/scorer.py`
- New file: `tests/fixtures/task_analyzer_test_set.json`
- New/updated tests: `tests/test_task_analyzer.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] Improved accuracy on test set (target: >80%)
- [ ] Confidence scores returned for all task types
- [ ] No regression on existing functionality
- [ ] All existing tests still pass
- [ ] New tests cover analyzer improvements
- [ ] Edge cases handled correctly
