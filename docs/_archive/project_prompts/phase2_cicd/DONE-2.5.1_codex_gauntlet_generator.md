# Prompt 2.5.1 - Gauntlet Test Generator

**Tool:** Codex CLI
**Epic:** 2.5 - Gauntlet Test Runner
**Phase:** 2 - CI/CD Integration

## Context

The Gauntlet auto-generates pytest contracts from `ensures` clauses in lattice.yaml. These semantic tests validate that implementations meet their behavioral specifications.

## Goal

Implement the test generator that creates pytest contracts from lattice.yaml ensures clauses.

## Steps

1. Create `src/lattice_lock_gauntlet/` module:
   ```
   lattice_lock_gauntlet/
   ├── __init__.py
   ├── generator.py
   ├── parser.py
   └── templates/
       └── test_contract.py.j2
   ```

2. Create `parser.py`:
   - Parse lattice.yaml entities and interfaces
   - Extract `ensures` clauses
   - Parse constraint expressions (gt, lt, gte, lte, etc.)

3. Create `generator.py`:
   - Generate pytest test functions from ensures clauses
   - Create test fixtures for entity instances
   - Generate boundary condition tests
   - Generate invariant preservation tests

4. Create `templates/test_contract.py.j2`:
   - Test file template with imports
   - Test class per entity/interface
   - Test method per ensures clause

5. Implement constraint-to-test mapping:
   - `gt: 0` → `assert value > 0`
   - `unique: true` → uniqueness test
   - Custom ensures → property-based test

6. Write unit tests in `tests/test_gauntlet_generator.py`:
   - Test parsing ensures clauses
   - Test generated tests are valid Python
   - Test generated tests catch violations

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Generator creates valid pytest files
- Generated tests catch constraint violations
- All ensures clause types supported
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Jinja2 for test templates
- Consider hypothesis for property-based tests
