# Prompt 1.1.1 - Package Infrastructure Setup

**Tool:** Devin AI
**Epic:** 1.1 - Package Model Orchestrator
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework has an existing Model Orchestrator at `src/lattice_lock_orchestrator/` with modules for core routing, scoring, registry, and API clients. This needs to be packaged as an importable Python library so users can do `from lattice_lock import ModelOrchestrator`.

The current version is 2.1.0 (in `version.txt`). The framework specification is at `specifications/lattice_lock_framework_specifications.md`.

## Goal

Create the package infrastructure (pyproject.toml, version management) to make the Model Orchestrator installable as a Python package.

## Steps

1. Create `pyproject.toml` at the repo root with:
   - Package name: `lattice-lock`
   - Version read from `version.txt`
   - Dependencies: click, pydantic, pytest, httpx, python-dotenv
   - Entry points for CLI: `lattice-lock = lattice_lock_cli.__main__:main`
   - Python requires: `>=3.10`
   - Package discovery for `src/` layout

2. Create `src/lattice_lock/__init__.py` that:
   - Imports and re-exports `ModelOrchestrator` from `lattice_lock_orchestrator.core`
   - Imports and re-exports key types from `lattice_lock_orchestrator.types`
   - Sets `__version__` from `version.txt`

3. Update `version.txt` format if needed (ensure it's clean: just `2.1.0`)

4. Create `tests/test_package_import.py` to verify:
   - `from lattice_lock import ModelOrchestrator` works
   - `from lattice_lock import __version__` returns correct version
   - Basic instantiation doesn't error

5. Test with `pip install -e .` and verify imports work

6. Run any existing tests to ensure no regressions

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)
- Any files in `commands/` or `templates/` directories

## Success Criteria

- `pip install -e .` succeeds
- `from lattice_lock import ModelOrchestrator` works
- `from lattice_lock import __version__` returns `2.1.0`
- Existing tests still pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use src-layout for package structure
- Follow PEP 621 for pyproject.toml format
