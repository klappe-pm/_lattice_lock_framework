# Prompt 1.1.2 - Package Exports and Imports

**Tool:** Devin AI
**Epic:** 1.1 - Package Model Orchestrator
**Phase:** 1 - Foundation

## Context

After the package infrastructure is set up (1.1.1), the Model Orchestrator needs proper exports so users can import all necessary types and classes. The orchestrator has types in `src/lattice_lock_orchestrator/types.py` including TaskType, TaskRequirements, and APIResponse.

## Goal

Ensure all public APIs are properly exported and update existing scripts to use the new import paths.

## Steps

1. Update `src/lattice_lock/__init__.py` to export:
   - `ModelOrchestrator` from `lattice_lock_orchestrator.core`
   - `TaskType`, `TaskRequirements`, `APIResponse` from `lattice_lock_orchestrator.types`
   - `ModelRegistry` from `lattice_lock_orchestrator.registry`
   - `ModelScorer`, `TaskAnalyzer` from `lattice_lock_orchestrator.scorer`

2. Create `src/lattice_lock/types.py` as a convenience re-export module

3. Update `scripts/orchestrator_cli.py` to use new import paths:
   - Change `from src.lattice_lock_orchestrator.core import ...` to `from lattice_lock import ...`

4. Update any test files that import from the old paths

5. Add `__all__` to `src/lattice_lock/__init__.py` listing all public exports

6. Write additional tests in `tests/test_package_import.py`:
   - Test all exported types are importable
   - Test type annotations work correctly

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- All public types importable from `lattice_lock`
- `scripts/orchestrator_cli.py` works with new imports
- Existing functionality unchanged
- `__all__` properly defined

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Maintain backward compatibility where possible
