# Task 6.4.2 - Core CLI Wrapper Implementation

**Tool:** Devin AI
**Phase:** 6.4 - Engineering Framework & Tooling
**Dependencies:** 6.4.1 (CLI UX Design), 6.2.3 (compile_lattice)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.4.2 - Core CLI Wrapper Implementation

### Context

- Design doc from 6.4.1 specifies the CLI structure (refer to that output)
- Files to create/modify:
  - `src/lattice_lock_cli/commands/validate.py` - Validate command
  - `src/lattice_lock_cli/commands/compile.py` - Compile command
  - `src/lattice_lock_cli/__main__.py` - Entry point updates
  - Integration with existing orchestrator commands

### Tool Ownership Note

Per `work_breakdown_structure.md`, Devin AI owns:
- `scripts/orchestrator_cli.py`
- `src/lattice_lock_validator/*`
- `src/lattice_lock_sheriff/*`
- `src/lattice_lock_gauntlet/*`

Devin should NOT touch:
- `src/lattice_lock_cli/commands/init.py` (Claude Code CLI)
- `src/lattice_lock_cli/templates/` (Claude Code CLI)

### Goals

1. Implement `validate` command wrapper:
   - Orchestrate schema validation + Sheriff + Gauntlet
   - Support `--schema-only`, `--sheriff-only`, `--gauntlet-only` flags
   - Proper exit codes per design doc
   - Rich output formatting

2. Implement `compile` command wrapper:
   - Wrap `compile_lattice` function from 6.2.3
   - Support all options from design doc
   - Progress indicators for long operations

3. Ensure orchestrator commands accessible:
   - Either integrate into unified CLI
   - Or document how to access via `orchestrator_cli.py`

4. Add tests:
   - Test validate command with valid/invalid inputs
   - Test compile command
   - Test exit codes
   - Test output formatting

### Constraints

- Respect tool ownership boundaries
- Must not break existing CLI functionality
- Use `rich` for output (already a dependency)
- Tests must pass before PR

### Output

- New/modified files in `src/lattice_lock_cli/commands/`
- Updated `src/lattice_lock_cli/__main__.py`
- New tests: `tests/test_cli_commands.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `lattice-lock validate` runs all validations
- [ ] `lattice-lock compile` compiles schemas
- [ ] Exit codes match design doc specification
- [ ] Rich output formatting works
- [ ] All existing tests still pass
- [ ] New tests cover CLI commands
