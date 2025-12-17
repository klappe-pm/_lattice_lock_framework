# Prompt 2.3.1 - GCP Cloud Build Template

**Tool:** Devin AI
**Epic:** 2.3 - GCP Cloud Build Integration
**Phase:** 2 - CI/CD Integration

## Context

The Lattice Lock Framework needs GCP Cloud Build integration for teams using Google Cloud infrastructure. The build configuration should run validation, Sheriff, and Gauntlet checks.

## Goal

Create GCP Cloud Build templates for Lattice Lock validation.

## Steps

1. Create `src/lattice_lock_cli/templates/ci/gcp/` directory:
   ```
   gcp/
   ├── cloudbuild.yaml.j2
   ├── cloudbuild-pr.yaml.j2
   └── trigger-config.yaml.j2
   ```

2. Create `cloudbuild.yaml.j2` main build config:
   - Step 1: Install Python dependencies
   - Step 2: Run lattice-lock validate
   - Step 3: Run lattice-lock sheriff
   - Step 4: Run lattice-lock gauntlet
   - Step 5: Run pytest with coverage
   - Artifacts: test results to Cloud Storage

3. Create `cloudbuild-pr.yaml.j2` for PR validation:
   - Lightweight validation for PRs
   - Skip full test suite
   - Fast feedback loop

4. Create `trigger-config.yaml.j2`:
   - GitHub/Cloud Source Repository trigger
   - Branch filter configuration
   - Substitution variables

5. Add GCP template option to init command:
   - `--ci gcp` flag generates GCP templates
   - Place in `ci/gcp/` directory in scaffolded project

6. Write unit tests in `tests/test_gcp_templates.py`:
   - Test cloudbuild.yaml is valid
   - Test all steps are present
   - Test variable substitution works

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- Generated templates are valid Cloud Build YAML
- All validation steps included
- Templates work with GCP Cloud Build
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Follow GCP Cloud Build best practices
- Use cloud-builders images where possible
