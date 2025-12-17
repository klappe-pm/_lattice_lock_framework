# Prompt 2.1.2 - Reusable Workflow Components

**Tool:** Claude Code CLI
**Epic:** 2.1 - GitHub Actions Integration
**Phase:** 2 - CI/CD Integration

## Context

GitHub Actions supports reusable workflows that can be called from other workflows. Creating reusable components allows projects to share common validation steps and reduces duplication.

## Goal

Create reusable GitHub Actions workflow components for Lattice Lock validation.

## Steps

1. Create `.github/workflows/` in the framework repo with reusable workflows:
   ```
   .github/workflows/
   ├── reusable-validate.yml
   ├── reusable-sheriff.yml
   ├── reusable-gauntlet.yml
   └── reusable-full-check.yml
   ```

2. Create `reusable-validate.yml`:
   - `workflow_call` trigger
   - Input: `python-version` (default: 3.10)
   - Input: `working-directory` (default: .)
   - Run lattice-lock validate

3. Create `reusable-sheriff.yml`:
   - `workflow_call` trigger
   - Input: `source-directory` (default: src/)
   - Run Sheriff AST validation

4. Create `reusable-gauntlet.yml`:
   - `workflow_call` trigger
   - Input: `test-directory` (default: tests/)
   - Run Gauntlet semantic tests

5. Create `reusable-full-check.yml`:
   - Combines all validation steps
   - Outputs: validation-passed, sheriff-passed, gauntlet-passed

6. Update template generation to reference reusable workflows:
   ```yaml
   jobs:
     validate:
       uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate.yml@main
   ```

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Reusable workflows can be called from other repos
- All inputs have sensible defaults
- Workflows pass when validation succeeds
- Documentation includes usage examples

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Follow GitHub reusable workflow best practices
- Test with actual GitHub Actions runs
