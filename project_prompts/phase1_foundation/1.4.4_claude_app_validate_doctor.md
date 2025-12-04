# Prompt 1.4.4 - Validate and Doctor Commands

**Tool:** Claude Code App
**Epic:** 1.4 - Scaffolding CLI
**Phase:** 1 - Foundation

## Context

The CLI needs `validate` and `doctor` commands. The `validate` command runs all validators (schema, env, agent, structure) on a project. The `doctor` command checks environment health (Python version, dependencies, configuration).

## Goal

Implement the `lattice-lock validate` and `lattice-lock doctor` CLI commands.

## Steps

1. Create `src/lattice_lock_cli/commands/validate.py` implementing:
   - `@click.command()` decorator
   - `--path` option (default: current directory)
   - `--fix` flag for auto-correction where possible
   - `--schema-only`, `--env-only`, `--agents-only`, `--structure-only` flags
   - Call validators from `lattice_lock_validator` module
   - Aggregate and display results

2. Create `src/lattice_lock_cli/commands/doctor.py` implementing:
   - `@click.command()` decorator
   - Check Python version (>=3.10)
   - Check required dependencies installed
   - Check environment variables configured
   - Check Ollama availability (optional)
   - Display health report with pass/fail indicators

3. Implement `--fix` functionality in validate:
   - Auto-fix trailing whitespace
   - Auto-fix missing newlines at EOF
   - Suggest fixes for other issues (don't auto-apply)

4. Register commands in `__main__.py`:
   ```python
   from .commands.validate import validate_command
   from .commands.doctor import doctor_command
   cli.add_command(validate_command, name="validate")
   cli.add_command(doctor_command, name="doctor")
   ```

5. Write unit tests in `tests/test_cli_validate.py` and `tests/test_cli_doctor.py`

6. Ensure proper exit codes (0=success, 1=failure)

## Do NOT Touch

- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/commands/init.py` (owned by Claude Code CLI)
- `src/lattice_lock_cli/templates/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` internals (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `lattice-lock validate` runs all validators
- `lattice-lock validate --fix` auto-corrects fixable issues
- `lattice-lock doctor` shows environment health
- Proper exit codes returned
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Import validators, don't modify them
- Use colorful output for pass/fail indicators
