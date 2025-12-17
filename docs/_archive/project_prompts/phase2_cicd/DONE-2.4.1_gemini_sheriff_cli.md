# Prompt 2.4.1 - Sheriff CLI Implementation

**Tool:** Gemini CLI
**Epic:** 2.4 - Sheriff CLI Wrapper
**Phase:** 2 - CI/CD Integration

## Context

Sheriff is the AST-based validator that enforces import discipline and type hint compliance. It needs a CLI wrapper that can be called from CI pipelines and integrates with the existing `sheriff.py` in the repo root.

## Goal

Create a CLI wrapper for Sheriff that integrates with the lattice-lock CLI.

## Steps

1. Create `src/lattice_lock_cli/commands/sheriff.py` implementing:
   - `@click.command()` decorator
   - `path` argument (file or directory to validate)
   - `--lattice` option (path to lattice.yaml, auto-detected if not provided)
   - `--fix` flag for auto-correction where possible
   - `--ignore` option for patterns to skip

2. Implement Sheriff invocation:
   - Import existing `sheriff.py` functionality
   - Walk directory tree for Python files
   - Run AST validation on each file
   - Collect and aggregate results

3. Implement output formatting:
   - JSON output with `--json` flag
   - Human-readable output by default
   - Summary statistics at end
   - Exit code 0 for pass, 1 for fail

4. Add escape hatch support:
   - Detect `# lattice:ignore` comments
   - Log ignored violations for audit

5. Register command in CLI:
   ```python
   from .commands.sheriff import sheriff_command
   cli.add_command(sheriff_command, name="sheriff")
   ```

6. Write unit tests in `tests/test_sheriff_cli.py`

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `lattice-lock sheriff src/` validates all Python files
- Violations reported with file, line, and description
- Exit codes correct for CI integration
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Build on existing sheriff.py, don't rewrite
- Keep validation fast (<5 seconds for typical project)
