# Prompt 1.2.1 - Schema Validation Core

**Tool:** Gemini CLI
**Epic:** 1.2 - Configuration Validator
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework uses `lattice.yaml` files as the single source of truth for type definitions, interfaces, and constraints. These files must be validated against policy rules before compilation. The schema format is defined in `specifications/lattice_lock_framework_specifications.md` Section 3.1.1.

## Goal

Implement the core schema validation logic for `lattice.yaml` files.

## Steps

1. Create `src/lattice_lock_validator/__init__.py` with module exports

2. Create `src/lattice_lock_validator/schema.py` implementing:
   - `validate_lattice_schema(file_path: str) -> ValidationResult`
   - Check required sections: `version`, `generated_module`, `entities`
   - Validate version format (semantic versioning: vX.Y or vX.Y.Z)
   - Validate entity references (entities must be defined before referenced)
   - Validate field types (supported: uuid, str, int, decimal, bool, enum)
   - Validate constraints (gt, lt, gte, lte, unique, primary_key)
   - Return structured errors with line numbers

3. Create `ValidationResult` dataclass with:
   - `valid: bool`
   - `errors: list[ValidationError]`
   - `warnings: list[ValidationWarning]`

4. Create `ValidationError` dataclass with:
   - `message: str`
   - `line_number: int | None`
   - `field_path: str | None`

5. Write unit tests in `tests/test_schema_validator.py`:
   - Test valid schema passes
   - Test missing required sections fails
   - Test invalid version format fails
   - Test undefined entity reference fails
   - Test invalid field type fails

6. Ensure validators use pydantic for internal validation

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Valid `lattice.yaml` files pass validation
- Invalid files return specific, actionable error messages
- Line numbers included in error messages where possible
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use PyYAML for parsing YAML files
- Consider using jsonschema for structural validation
