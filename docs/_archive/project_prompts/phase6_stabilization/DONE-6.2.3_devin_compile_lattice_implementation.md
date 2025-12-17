# Task 6.2.3 - compile_lattice Python API & CLI Entry

**Tool:** Devin AI
**Phase:** 6.2 - Governance Core Loop
**Dependencies:** 6.2.1 (Governance Core Spec), 6.2.2 (lattice.yaml Examples)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.2.3 - compile_lattice Python API & CLI Entry

### Context

- Design doc from 6.2.1 specifies the compile_lattice API (refer to that output)
- Example files from 6.2.2 provide test cases
- Files to create/modify:
  - `src/lattice_lock/compile.py` - Core compilation logic
  - `src/lattice_lock/__init__.py` - Export compile function
  - `scripts/compile_lattice.py` - CLI entrypoint (or integrate into existing CLI)

### Goals

1. Implement `compile_lattice` function:
   ```python
   def compile_lattice(
       schema_path: str | Path,
       output_dir: str | Path | None = None,
       generate_pydantic: bool = True,
       generate_sqlmodel: bool = False,
       generate_gauntlet: bool = True,
   ) -> CompilationResult:
       """
       Compile a lattice.yaml schema into enforcement artifacts.

       Args:
           schema_path: Path to lattice.yaml file
           output_dir: Directory for generated files (default: same as schema)
           generate_pydantic: Generate Pydantic models
           generate_sqlmodel: Generate SQLModel ORM classes
           generate_gauntlet: Generate Gauntlet test contracts

       Returns:
           CompilationResult with paths to generated files and any warnings
       """
   ```

2. Implementation steps:
   - Load and parse YAML schema
   - Validate using existing `src/lattice_lock_validator/schema.py`
   - Generate Gauntlet tests using `src/lattice_lock_gauntlet/generator.py`
   - Optionally generate Pydantic models
   - Optionally generate SQLModel classes
   - Return result with generated file paths

3. Create CLI entrypoint:
   ```bash
   # Option A: Standalone script
   python scripts/compile_lattice.py examples/basic/lattice.yaml --output-dir ./generated

   # Option B: Integrated into lattice-lock CLI
   lattice-lock compile examples/basic/lattice.yaml --output-dir ./generated
   ```

4. Add comprehensive tests:
   - Test compilation of valid schemas
   - Test error handling for invalid schemas
   - Test each generation option (pydantic, sqlmodel, gauntlet)
   - Test output file creation

### Constraints

- Must integrate with existing validator and gauntlet modules
- Must not break existing functionality
- Clear error messages for compilation failures
- Tests must pass before PR

### Output

- New file: `src/lattice_lock/compile.py`
- Updated: `src/lattice_lock/__init__.py`
- New file: `scripts/compile_lattice.py` (or CLI integration)
- New test file: `tests/test_compile_lattice.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `compile_lattice()` function works with example schemas
- [ ] CLI entrypoint works: `python scripts/compile_lattice.py examples/basic/lattice.yaml`
- [ ] Gauntlet tests are generated correctly
- [ ] Invalid schemas produce clear error messages
- [ ] All existing tests still pass
- [ ] New tests cover compilation scenarios
