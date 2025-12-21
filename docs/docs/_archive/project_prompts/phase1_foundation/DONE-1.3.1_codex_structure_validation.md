# Prompt 1.3.1 - Structure Validation Module

**Tool:** Codex CLI
**Epic:** 1.3 - Repository Structure Enforcement
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework has mandatory repository structure standards defined in `directory/repository_structure_standards.md`. All files must follow snake_case naming, be in correct directories, and follow specific patterns for agent definitions, documentation, and code.

## Goal

Implement repository structure validation that enforces naming conventions and directory organization.

## Steps

1. Create `src/lattice_lock_validator/structure.py` implementing:
   - `validate_repository_structure(repo_path: str) -> ValidationResult`
   - `validate_file_naming(file_path: str) -> ValidationResult`
   - `validate_directory_structure(repo_path: str) -> ValidationResult`

2. Implement file naming validation:
   - All files must use snake_case (no spaces, hyphens in names)
   - Agent definitions: `{category}_{name}_definition.yaml`
   - Documentation: `*.md` files only in doc directories
   - Python files: `*.py` with snake_case names
   - Exception: standard files like `README.md`, `LICENSE.md`

3. Implement directory structure validation:
   - Required root directories: `agent_definitions/`, `src/`, `scripts/`
   - Required root files: `.gitignore`, `README.md`
   - Agent definitions must be in category subdirectories
   - No files at wrong nesting levels

4. Implement prohibited pattern detection:
   - No spaces in file/directory names
   - No special characters except underscore
   - No camelCase or PascalCase in file names
   - No temporary files (*.tmp, *.bak, .DS_Store)

5. Write unit tests in `tests/test_structure_validator.py`:
   - Test valid structure passes
   - Test snake_case violation detected
   - Test missing required directory detected
   - Test prohibited file detected
   - Test with actual repo structure

6. Return actionable error messages with file paths

## Do NOT Touch

- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Valid repository structure passes
- Naming violations detected with specific file paths
- Missing directories reported
- Prohibited patterns caught
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Reference `directory/repository_structure_standards.md` for full rules
- Use pathlib for file system operations
