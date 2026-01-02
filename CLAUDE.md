# Lattice Lock Framework

## Quick Commands

- `make lint` - Run comprehensive linting (Ruff, Black, MyPy, Lattice Validate)
- `make test` - Run unit tests (pytest, skipping integration tests)
- `make ci` - Run full CI check (lint, type-check, test, security)
- `make format` - Auto-format code with Black and Ruff
- `lattice-lock validate` - Run static analysis on the codebase
- `lattice-lock test` - Run generated runtime tests

## Project Structure

- `src/lattice_lock/` - Core Python package
  - `orchestrator/` - Model routing & selection logic
  - `sheriff/` - Static analysis engine (AST-based)
  - `gauntlet/` - Runtime testing & generation
  - `cli/` - Command-line interface entry points
  - `consensus/` - specialized consensus logic
- `tests/` - Test suite (unit, integration, e2e)
- `docs/` - Comprehensive documentation
- `scripts/` - Utility and automation scripts

## Code Style

> **Single Source of Truth:** See `contributing.md` for full details.

- **Naming:** All files must be `lowercase_with_underscores.py`. Classes are `PascalCase`.
- **Formatting:** Black (88 chars), isort, Ruff.
- **Type Hints:** Required for all public functions and classes.
- **Docstrings:** Google-style docstrings required for public API.
- **Imports:** Absolute imports from `src/` preferred.

## Testing

- **Unit Tests:** `pytest tests/ -m "not integration"`
- **Integration Tests:** `pytest tests/integration/`
- **Coverage:** Minimum 70% required. use `--cov=src/lattice_lock`.
- **Markers:** Use `@pytest.mark.asyncio` for async tests.

## Key Patterns

- **Orchestrator:** Central entry point for model interactions. code: `ModelOrchestrator`
- **Sheriff:** Static analysis via AST visitation. code: `run_sheriff()`
- **Gauntlet:** Generates tests from `lattice.yaml` policies. code: `GauntletGenerator`
- **Consensus:** Multi-model agreement engine. code: `ConsensusEngine`
