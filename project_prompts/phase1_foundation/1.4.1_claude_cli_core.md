# Prompt 1.4.1 - CLI Core and Entry Point

**Tool:** Claude Code CLI
**Epic:** 1.4 - Scaffolding CLI
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework needs a CLI tool (`lattice-lock`) for scaffolding projects, running validation, and managing the development workflow. The CLI should use the Click framework and follow the structure defined in `specifications/lattice_lock_framework_specifications.md` Section 3.3.1.

## Goal

Create the CLI package structure and main entry point using Click.

## Steps

1. Create `src/lattice_lock_cli/__init__.py` with:
   - Package version import from `lattice_lock`
   - Module docstring describing the CLI

2. Create `src/lattice_lock_cli/__main__.py` implementing:
   - Main Click group with `@click.group()`
   - Version option (`--version`)
   - Verbose option (`--verbose`)
   - Help text and description
   - Entry point function `main()`

3. Set up CLI group structure:
   ```python
   @click.group()
   @click.version_option()
   @click.option('--verbose', '-v', is_flag=True)
   @click.pass_context
   def cli(ctx, verbose):
       """Lattice Lock Framework CLI"""
       ctx.ensure_object(dict)
       ctx.obj['verbose'] = verbose
   ```

4. Create `src/lattice_lock_cli/commands/__init__.py` for command imports

5. Add placeholder imports for commands (to be implemented):
   - `from .init import init_command`
   - Commands will be added by other prompts

6. Write unit tests in `tests/test_cli_core.py`:
   - Test CLI loads without error
   - Test `--version` shows correct version
   - Test `--help` shows help text
   - Test verbose flag is passed to context

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `python -m lattice_lock_cli --help` works
- `python -m lattice_lock_cli --version` shows version
- CLI group structure ready for commands
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Click framework (https://click.palletsprojects.com/)
- Follow Click best practices for context passing
