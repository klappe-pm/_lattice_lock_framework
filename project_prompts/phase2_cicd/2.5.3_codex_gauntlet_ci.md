# Prompt 2.5.3 - Gauntlet CI Integration

**Tool:** Codex CLI
**Epic:** 2.5 - Gauntlet Test Runner
**Phase:** 2 - CI/CD Integration

## Context

Gauntlet needs CI-specific features including machine-readable output, JUnit reports, and integration with GitHub PR checks for test result annotations.

## Goal

Implement CI-specific features for Gauntlet integration.

## Steps

1. Add CI output formats to Gauntlet CLI:
   - `--format json` for machine-readable output
   - `--format junit` for JUnit XML reports
   - `--format github` for GitHub Actions annotations

2. Implement JUnit XML output:
   - Test suite per contract file
   - Test case per ensures clause
   - Failure details with assertion info

3. Implement GitHub Actions integration:
   - Annotations for failed tests
   - Summary comment on PR
   - Test result artifacts

4. Add parallel test execution:
   - `--parallel` flag for concurrent tests
   - Worker count configuration
   - Result aggregation

5. Create GitHub Action for Gauntlet:
   ```yaml
   # action.yml
   name: 'Lattice Lock Gauntlet'
   description: 'Run Gauntlet semantic tests'
   inputs:
     coverage-threshold:
       description: 'Minimum coverage percentage'
       default: '80'
   ```

6. Write integration tests in `tests/test_gauntlet_ci.py`:
   - Test each output format
   - Test parallel execution
   - Test GitHub integration

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- All output formats work correctly
- JUnit reports compatible with CI tools
- Parallel execution improves performance
- Integration tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use pytest-xdist for parallel execution
- Follow JUnit XML schema exactly
