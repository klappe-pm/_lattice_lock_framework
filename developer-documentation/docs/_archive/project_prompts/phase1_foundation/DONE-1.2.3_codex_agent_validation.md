# Prompt 1.2.3 - Agent Manifest Validation

**Tool:** Codex CLI
**Epic:** 1.2 - Configuration Validator
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework uses agent definition files that must comply with the v2.1 specification at `agent_specifications/agent_instructions_file_format_v2_1.md`. Agent manifests are YAML files in `agent_definitions/` that define agent identity, directives, responsibilities, and scope.

## Goal

Implement agent manifest validation against the v2.1 specification.

## Steps

1. Create `src/lattice_lock_validator/agents.py` implementing:
   - `validate_agent_manifest(file_path: str) -> ValidationResult`
   - Check required sections per v2.1 spec
   - Validate section structure and required fields
   - Return structured errors with line numbers

2. Validate required top-level sections:
   - `agent.identity` (name, version, description, role)
   - `directive` (primary_goal)
   - `responsibilities` (list of tasks)
   - `scope` (can_access, cannot_access)

3. Validate agent.identity fields:
   - `name`: non-empty string
   - `version`: semantic version format
   - `description`: non-empty string
   - `role`: non-empty string

4. Validate directive fields:
   - `primary_goal`: non-empty string
   - `constraints`: optional list

5. Validate responsibilities:
   - Each must have `name`, `description`
   - Optional: `inputs`, `outputs`, `criticality`

6. Write unit tests in `tests/test_agent_validator.py`:
   - Test valid agent manifest passes
   - Test missing required section fails
   - Test invalid version format fails
   - Test empty required field fails
   - Test with real agent files from `agent_definitions/`

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Valid agent manifests pass validation
- Invalid manifests return specific error messages
- Line numbers included where possible
- Tests pass with real agent files from repo
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Reference `agent_specifications/agent_instructions_file_format_v2_1.md` for full spec
- Use PyYAML for parsing
