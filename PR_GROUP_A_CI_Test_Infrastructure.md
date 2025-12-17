# Pull Request: Group A - CI and Test Infrastructure

## Summary

Fixes CI pipeline failures by correcting test directory paths in Makefile and GitHub Actions workflows. Resolves potential test failures in Gauntlet and Bedrock suites. Additionally fixes blocking `NameError` and circular imports in the prompt architect agent to enable test collection.

## Motivation and Context

### Problem Statement
- CI pipelines were failing due to incorrect `tests/unit` directory references (directory does not exist).
- Test execution was blocked by `NameError: name 'Dict' is not defined` in `quality_scorer.py`.
- Test execution was blocked by a circular import between `agent.py` and `subagents.prompt_generator.py`.
- `bcrypt` module is missing in the environment, causing `test_admin_auth.py` and `test_admin_api.py` to fail collection (not fixed in this PR, but noted).

### Why This Matters
- **Developer Experience**: `make test` was broken.
- **CI Stability**: Pipelines could not run tests.
- **Code Quality**: Circular imports and missing types indicate fragile code.

## Changes Made

### Detailed Changes

#### Makefile
**File:** `Makefile`
**Changes:** Updated test command to point to `tests/` root and exclude integration tests.

**Before:**
```makefile
test:
	pytest tests/unit
```

**After:**
```makefile
test:
	pytest tests/ -m "not integration" --tb=short
```

#### CI Workflow
**File:** `.github/workflows/ci.yml`
**Changes:** Updated test step to match Makefile.

**Before:**
```yaml
      - name: Unit Tests
        run: pytest tests/unit
```

**After:**
```yaml
      - name: Unit Tests
        run: pytest tests/ -m "not integration" --tb=short
```

#### Quality Scorer
**File:** `src/lattice_lock_agents/prompt_architect/validators/quality_scorer.py`
**Changes:** Added missing `Dict` import.

**Before:**
```python
from typing import Any, Optional
```

**After:**
```python
from typing import Any, Optional, Dict
```

#### Prompt Architect Agent
**File:** `src/lattice_lock_agents/prompt_architect/agent.py`
**Changes:** Resolved circular import by moving `PromptGenerator` import to `TYPE_CHECKING` block and local scope.

**Rationale:** `PromptGenerator` imports `validators` -> `__init__` -> `agent` -> `PromptGenerator`, creating a cycle.

### Files Modified
- [x] `Makefile` - Updated test path
- [x] `.github/workflows/ci.yml` - Updated test path
- [x] `src/lattice_lock_agents/prompt_architect/validators/quality_scorer.py` - Fixed NameError
- [x] `src/lattice_lock_agents/prompt_architect/agent.py` - Fixed circular import

## Testing

### Test Strategy
- Verified test paths exist.
- Ran `pytest tests/test_gauntlet_cli.py` (7 passed).
- Ran `pytest tests/test_gauntlet_ci.py` (7 passed).
- Ran `pytest tests/test_bedrock_implementation.py` (Skipped: boto3 missing).
- Attempted `make test` (Partial success, blocked by missing `bcrypt`).

### Test Results

**Gauntlet CLI Tests:**
```
tests/test_gauntlet_cli.py::test_generate_mode PASSED
tests/test_gauntlet_cli.py::test_run_mode_default PASSED
... (7 passed)
```

**Gauntlet CI Tests:**
```
tests/test_gauntlet_ci.py::test_format_json PASSED
... (7 passed)
```

**Note:** Full test suite collection (`make test`) still fails on `test_admin_api.py` and `test_admin_auth.py` due to missing `bcrypt` in the environment. This is unrelated to the changes in this PR and requires environment setup.

## Security Considerations
None. Infrastructure and bug fixes only.

## Deployment Notes
None.
