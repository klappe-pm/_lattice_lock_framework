# Prompt 2.5.2 - Gauntlet CLI Wrapper

**Tool:** Codex CLI
**Epic:** 2.5 - Gauntlet Test Runner
**Phase:** 2 - CI/CD Integration

## Context

The Gauntlet needs a CLI wrapper that generates and runs semantic tests from lattice.yaml. It should integrate with the lattice-lock CLI and provide options for test generation and execution.

## Goal

Create a CLI wrapper for Gauntlet that integrates with the lattice-lock CLI.

## Steps

1. Create `src/lattice_lock_cli/commands/gauntlet.py` implementing:
   - `@click.command()` decorator
   - `--generate` flag to generate tests without running
   - `--run` flag to run existing tests (default)
   - `--output` option for generated test location
   - `--lattice` option for lattice.yaml path

2. Implement generate mode:
   - Parse lattice.yaml
   - Generate pytest contracts
   - Write to tests/test_contracts_vX.py

3. Implement run mode:
   - Locate generated test files
   - Run pytest with appropriate options
   - Capture and format output

4. Add coverage integration:
   - `--coverage` flag to enable coverage
   - Generate coverage report
   - Fail if coverage below threshold

5. Register command in CLI:
   ```python
   from .commands.gauntlet import gauntlet_command
   cli.add_command(gauntlet_command, name="gauntlet")
   ```

6. Write unit tests in `tests/test_gauntlet_cli.py`:
   - Test generate mode creates files
   - Test run mode executes tests
   - Test coverage reporting works

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `lattice-lock gauntlet --generate` creates test files
- `lattice-lock gauntlet --run` executes tests
- Coverage reporting works
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use pytest programmatically for test execution
- Support pytest plugins (coverage, etc.)
