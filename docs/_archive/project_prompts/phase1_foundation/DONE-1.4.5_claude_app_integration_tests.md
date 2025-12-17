# Prompt 1.4.5 - CLI Integration Tests

**Tool:** Claude Code App
**Epic:** 1.4 - Scaffolding CLI
**Phase:** 1 - Foundation

## Context

The CLI commands need end-to-end integration tests that verify the full workflow: scaffolding a project, validating it, and running doctor checks. These tests ensure all components work together correctly.

## Goal

Write comprehensive integration tests for the CLI commands.

## Steps

1. Create `tests/integration/` directory structure:
   ```
   tests/integration/
   ├── __init__.py
   ├── conftest.py
   ├── test_cli_integration.py
   └── test_validate_integration.py
   ```

2. Create `tests/integration/conftest.py` with fixtures:
   - `temp_project_dir` - creates temporary directory for test projects
   - `cli_runner` - Click test runner
   - `sample_lattice_yaml` - valid lattice.yaml content
   - `sample_env_file` - valid .env content

3. Create `tests/integration/test_cli_integration.py`:
   - Test full workflow: init -> validate -> doctor
   - Test init creates all expected files
   - Test validate passes on freshly scaffolded project
   - Test doctor reports correct environment status

4. Create `tests/integration/test_validate_integration.py`:
   - Test validate catches schema errors
   - Test validate catches env errors
   - Test validate catches structure errors
   - Test --fix corrects fixable issues
   - Test exit codes are correct

5. Add integration test markers in `pytest.ini`:
   ```ini
   markers =
       integration: marks tests as integration tests
   ```

6. Ensure tests clean up temporary files after completion

## Do NOT Touch

- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/commands/init.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/templates/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Integration tests cover full CLI workflows
- Tests pass on clean environment
- Tests clean up after themselves
- Tests can be run with `pytest -m integration`

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Click's CliRunner for testing
- Use pytest's tmp_path fixture for temporary directories
