# Prompt 2.2.1 - AWS CodePipeline Template

**Tool:** Devin AI
**Epic:** 2.2 - AWS CodePipeline Integration
**Phase:** 2 - CI/CD Integration

## Context

The Lattice Lock Framework needs AWS CodePipeline integration for teams using AWS infrastructure. The pipeline should run validation, Sheriff, and Gauntlet checks as part of the CI/CD process.

## Goal

Create AWS CodePipeline and CodeBuild templates for Lattice Lock validation.

## Steps

1. Create `src/lattice_lock_cli/templates/ci/aws/` directory:
   ```
   aws/
   ├── buildspec.yml.j2
   ├── pipeline.yml.j2
   └── codebuild-project.yml.j2
   ```

2. Create `buildspec.yml.j2` for CodeBuild:
   - Install phase: Python 3.10+, pip dependencies
   - Pre-build phase: lattice-lock validate
   - Build phase: lattice-lock sheriff, lattice-lock gauntlet
   - Post-build phase: pytest, coverage report
   - Artifacts: test results, coverage reports

3. Create `pipeline.yml.j2` CloudFormation template:
   - Source stage: CodeCommit or GitHub connection
   - Build stage: CodeBuild project
   - Optional deploy stage placeholder

4. Create `codebuild-project.yml.j2`:
   - Environment: Python 3.10 runtime
   - Service role with necessary permissions
   - Cache configuration for pip

5. Add AWS template option to init command:
   - `--ci aws` flag generates AWS templates
   - Place in `ci/aws/` directory in scaffolded project

6. Write unit tests in `tests/test_aws_templates.py`:
   - Test buildspec is valid YAML
   - Test CloudFormation templates are valid
   - Test variable substitution works

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- Generated templates are valid AWS CloudFormation
- Buildspec runs all validation steps
- Templates work with AWS CodePipeline
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Follow AWS best practices for CodePipeline
- Include IAM role templates with least privilege
