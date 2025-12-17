# Prompt 2.1.1 - GitHub Actions Workflow Template

**Tool:** Claude Code CLI
**Epic:** 2.1 - GitHub Actions Integration
**Phase:** 2 - CI/CD Integration

## Context

The Lattice Lock Framework needs GitHub Actions workflow templates that run validation on every PR. The workflow should compile schemas, run Sheriff (AST validation), run Gauntlet (semantic tests), and test the orchestrator.

## Goal

Create GitHub Actions workflow templates for Lattice Lock CI/CD integration.

## Steps

1. Create `src/lattice_lock_cli/templates/ci/github_actions/` directory:
   ```
   github_actions/
   ├── lattice-lock.yml.j2
   ├── validate-only.yml.j2
   └── full-pipeline.yml.j2
   ```

2. Create `lattice-lock.yml.j2` main workflow:
   - Trigger on push and pull_request
   - Python 3.10+ setup
   - Install dependencies
   - Run `lattice-lock validate`
   - Run `lattice-lock sheriff src/`
   - Run `lattice-lock gauntlet`
   - Run pytest

3. Create `validate-only.yml.j2` lightweight workflow:
   - Trigger on pull_request only
   - Quick validation without full test suite
   - Suitable for draft PRs

4. Create `full-pipeline.yml.j2` comprehensive workflow:
   - All validation steps
   - Code coverage reporting
   - Artifact upload for test results
   - Slack/Discord notification (optional)

5. Add workflow generation to init command:
   - Copy appropriate workflow based on template type
   - Set correct permissions in generated files

6. Write unit tests in `tests/test_github_actions_templates.py`:
   - Test workflows are valid YAML
   - Test all required steps present
   - Test variable substitution works

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Generated workflows are valid GitHub Actions YAML
- Workflows run successfully on GitHub
- All validation steps included
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Follow GitHub Actions best practices
- Use caching for pip dependencies
