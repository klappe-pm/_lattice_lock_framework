# Prompt 1.4.3 - Project Templates

**Tool:** Claude Code CLI
**Epic:** 1.4 - Scaffolding CLI
**Phase:** 1 - Foundation

## Context

The `lattice-lock init` command needs Jinja2 templates for generating project files. Templates should support three project types: agent, service, and library. Each template type generates appropriate scaffolding for its use case.

## Goal

Create Jinja2 templates for all project types that generate compliant project structures.

## Steps

1. Create `src/lattice_lock_cli/templates/` directory structure:
   ```
   templates/
   ├── base/
   │   ├── lattice.yaml.j2
   │   ├── readme.md.j2
   │   └── gitignore.j2
   ├── agent/
   │   └── agent_definition.yaml.j2
   ├── service/
   │   └── service_scaffold.py.j2
   ├── library/
   │   └── lib_init.py.j2
   └── ci/
       └── github_workflow.yml.j2
   ```

2. Create `templates/base/lattice.yaml.j2`:
   - Version placeholder
   - Generated module name from project name
   - Example entity definition
   - Config section with forbidden imports

3. Create `templates/base/readme.md.j2`:
   - Project name as title
   - Description placeholder
   - Installation instructions
   - Usage examples
   - Reference to Lattice Lock docs

4. Create `templates/ci/github_workflow.yml.j2`:
   - Trigger on push/PR
   - Python setup
   - Install dependencies
   - Run lattice-lock validate
   - Run tests

5. Create template loader utility in `src/lattice_lock_cli/templates/__init__.py`:
   - `get_template(name: str) -> Template`
   - `render_template(name: str, context: dict) -> str`
   - `get_templates_for_type(project_type: str) -> list[str]`

6. Write unit tests in `tests/test_templates.py`:
   - Test each template renders without error
   - Test template variables are substituted
   - Test output is valid YAML/Markdown/Python

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- All templates render correctly
- Generated files are syntactically valid
- Templates support all three project types
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Jinja2 for templating
- Include helpful comments in generated files
