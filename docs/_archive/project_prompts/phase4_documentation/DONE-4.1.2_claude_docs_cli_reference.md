# Prompt 4.1.2 - CLI Reference Documentation

**Tool:** Claude Code Website
**Epic:** 4.1 - Reference Documentation
**Phase:** 4 - Documentation & Pilot

## Context

The Lattice Lock CLI needs comprehensive reference documentation covering all commands, options, and usage patterns. This documentation should be auto-generated where possible and manually enhanced with examples.

## Goal

Create CLI reference documentation for all lattice-lock commands.

## Steps

1. Create `developer_documentation/reference/` directory:
   ```
   reference/
   ├── cli/
   │   ├── index.md
   │   ├── init.md
   │   ├── validate.md
   │   ├── doctor.md
   │   ├── sheriff.md
   │   └── gauntlet.md
   └── configuration.md
   ```

2. Create `cli/index.md`:
   - Overview of CLI structure
   - Global options (--help, --version, --verbose)
   - Command categories
   - Exit codes reference

3. Create command reference pages:
   - `init.md`: Project scaffolding command
   - `validate.md`: Validation command with all options
   - `doctor.md`: Environment health check
   - `sheriff.md`: AST validation command
   - `gauntlet.md`: Semantic test runner

4. For each command page include:
   - Synopsis (command syntax)
   - Description
   - Options table with types and defaults
   - Examples (basic and advanced)
   - Exit codes
   - See also (related commands)

5. Create `configuration.md`:
   - lattice.yaml schema reference
   - All configuration options
   - Default values
   - Environment variable overrides

6. Add man page generation script for Unix systems

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `scripts/` (owned by various tools)

## Success Criteria

- All CLI commands documented
- Options and flags fully described
- Examples are runnable and accurate
- Documentation follows consistent format

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Click's help text as source of truth
- Include real-world usage examples
- Cross-reference related documentation
