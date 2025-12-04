# Prompt 1.4.2 - Init Command Implementation

**Tool:** Claude Code CLI
**Epic:** 1.4 - Scaffolding CLI
**Phase:** 1 - Foundation

## Context

The `lattice-lock init` command scaffolds new projects with compliant directory structures. It should create a project with `lattice.yaml`, `src/`, `tests/`, `.github/workflows/`, and `README.md` as defined in `specifications/lattice_lock_framework_specifications.md` Section 3.3.1.

## Goal

Implement the `lattice-lock init <project-name>` command that creates a new project structure.

## Steps

1. Create `src/lattice_lock_cli/commands/init.py` implementing:
   - `@click.command()` decorator
   - `project_name` argument (required)
   - `--template` option (choices: agent, service, library; default: service)
   - `--output-dir` option (default: current directory)

2. Implement project creation logic:
   - Validate project name (snake_case, no special chars)
   - Check target directory doesn't exist
   - Create directory structure from templates
   - Render Jinja2 templates with project name

3. Create directory structure:
   ```
   project-name/
   ├── lattice.yaml
   ├── src/
   │   ├── shared/
   │   └── services/
   ├── tests/
   │   └── test_contracts.py
   ├── .github/
   │   └── workflows/
   │       └── lattice-lock.yml
   └── README.md
   ```

4. Register command in `__main__.py`:
   ```python
   from .commands.init import init_command
   cli.add_command(init_command, name="init")
   ```

5. Write unit tests in `tests/test_cli_init.py`:
   - Test successful project creation
   - Test invalid project name rejected
   - Test existing directory rejected
   - Test different templates create correct structures

6. Add helpful output messages showing created files

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `lattice-lock init my_project` creates correct structure
- Templates render correctly with project name
- Invalid inputs rejected with helpful messages
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Jinja2 for template rendering
- Follow Click best practices
