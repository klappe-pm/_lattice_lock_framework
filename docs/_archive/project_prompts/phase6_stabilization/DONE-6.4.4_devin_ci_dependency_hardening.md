# Task 6.4.4 - CI Templates & Dependency Hardening

**Tool:** Devin AI
**Phase:** 6.4 - Engineering Framework & Tooling
**Dependencies:** 6.4.3 (CI Templates & Workflows Design)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.4.4 - CI Templates & Dependency Hardening

### Context

- Design doc from 6.4.3 specifies the CI templates (refer to that output)
- Files to create/modify:
  - `pyproject.toml` - Fix dependencies
  - `.github/workflows/ci.yml` - GitHub Actions workflow
  - `src/lattice_lock_cli/templates/ci/github/` - Template updates

### Current Issues

Running `pytest` produces collection errors:
```
ModuleNotFoundError: No module named 'click'
```

The `pyproject.toml` is missing required dependencies.

### Goals

1. Fix `pyproject.toml` dependencies:
   - Add all missing core dependencies
   - Add dev dependencies group
   - Add CLI dependencies group
   - Ensure `pip install -e ".[dev]"` works

2. Create/update GitHub Actions workflow:
   - Implement workflow from design doc
   - Ensure all steps pass
   - Add caching for pip

3. Verify test collection works:
   - Run `pytest --collect-only` without errors
   - Run full test suite
   - Document any tests that need API keys

4. Update CI templates:
   - Ensure templates match working workflow
   - Add comments explaining each step

5. Add CI verification test:
   - Test that validates CI config is valid YAML
   - Test that required deps are listed

### Constraints

- Must not break existing functionality
- All tests must pass locally before PR
- CI must pass on GitHub
- Tests must pass before PR

### Output

- Modified: `pyproject.toml`
- New/modified: `.github/workflows/ci.yml`
- Updated templates in `src/lattice_lock_cli/templates/ci/`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest --collect-only` has no import errors
- [ ] `pytest -m "not integration"` passes locally
- [ ] GitHub Actions workflow passes
- [ ] All existing tests still pass
- [ ] Dependencies are properly categorized
