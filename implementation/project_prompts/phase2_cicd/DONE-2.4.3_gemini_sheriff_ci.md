# Prompt 2.4.3 - Sheriff CI Integration

**Tool:** Gemini CLI
**Epic:** 2.4 - Sheriff CLI Wrapper
**Phase:** 2 - CI/CD Integration

## Context

Sheriff needs to integrate seamlessly with CI/CD pipelines, providing machine-readable output, proper exit codes, and integration with GitHub PR checks for inline annotations.

## Goal

Implement CI-specific features for Sheriff integration.

## Steps

1. Add CI output formats to Sheriff CLI:
   - `--format json` for machine-readable output
   - `--format github` for GitHub Actions annotations
   - `--format junit` for JUnit XML reports

2. Implement GitHub Actions annotation format:
   ```
   ::error file={file},line={line}::{message}
   ::warning file={file},line={line}::{message}
   ```

3. Implement JUnit XML output:
   - Test suite per file
   - Test case per rule check
   - Failure details with line numbers

4. Add caching support:
   - Cache AST parse results
   - Skip unchanged files (based on hash)
   - `--no-cache` flag to force full scan

5. Create GitHub Action for Sheriff:
   ```yaml
   # action.yml
   name: 'Lattice Lock Sheriff'
   description: 'Run Sheriff AST validation'
   inputs:
     path:
       description: 'Path to validate'
       default: 'src/'
   ```

6. Write integration tests in `tests/test_sheriff_ci.py`:
   - Test each output format
   - Test GitHub annotations format
   - Test caching behavior

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- All output formats work correctly
- GitHub annotations appear on PRs
- Caching improves performance
- Integration tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Follow GitHub Actions annotation format exactly
- JUnit format should be compatible with common CI tools
