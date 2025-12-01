# Prompt 1.3.2 - Pre-commit Hook Integration

**Tool:** Codex CLI
**Epic:** 1.3 - Repository Structure Enforcement
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework needs automated enforcement of repository structure standards at commit time. Pre-commit hooks should run structure validation before allowing commits, catching violations early in the development workflow.

## Goal

Create pre-commit hook configuration that runs structure validation automatically.

## Steps

1. Create `.pre-commit-config.yaml` at repo root with:
   - Local hook for structure validation
   - Local hook for file naming validation
   - Standard hooks for trailing whitespace, end-of-file fixer
   - YAML syntax checking

2. Configure structure validation hook:
   ```yaml
   - repo: local
     hooks:
       - id: lattice-structure-check
         name: Lattice Structure Validation
         entry: python -m lattice_lock_validator.structure
         language: python
         types: [file]
         pass_filenames: false
   ```

3. Configure file naming hook:
   ```yaml
   - repo: local
     hooks:
       - id: lattice-naming-check
         name: File Naming Convention Check
         entry: python -m lattice_lock_validator.structure --naming-only
         language: python
         types: [file]
   ```

4. Add CLI entry point to structure.py:
   - `if __name__ == "__main__":` block
   - Parse `--naming-only` flag
   - Exit with appropriate codes (0=pass, 1=fail)

5. Create `scripts/setup_precommit.sh`:
   - Install pre-commit if not present
   - Run `pre-commit install`
   - Run initial validation

6. Write integration test in `tests/test_precommit_integration.py`:
   - Test hook runs on commit
   - Test hook blocks invalid commits
   - Test hook passes valid commits

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Pre-commit hooks install successfully
- Structure violations block commits
- Valid commits pass through
- Setup script works on fresh clone
- Integration tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use pre-commit framework (https://pre-commit.com/)
- Keep hooks fast (<5 seconds)
