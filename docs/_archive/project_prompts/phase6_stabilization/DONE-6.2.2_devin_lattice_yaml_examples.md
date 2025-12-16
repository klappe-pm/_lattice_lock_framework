# Task 6.2.2 - lattice.yaml Examples and Test Fixtures

**Tool:** Devin AI
**Phase:** 6.2 - Governance Core Loop
**Dependencies:** 6.2.1 (Governance Core & lattice.yaml Specification)
**Owner:** Devin AI

---

## Prompt for Devin

Task ID: 6.2.2 - lattice.yaml Examples and Test Fixtures

### Context

- Design doc from 6.2.1 specifies the canonical lattice.yaml format (refer to that output)
- Files to create:
  - `examples/basic/lattice.yaml` - Simple example
  - `examples/advanced/lattice.yaml` - Complex example with all features
  - `tests/fixtures/valid_lattice.yaml` - Valid test fixture
  - `tests/fixtures/invalid_lattice.yaml` - Invalid test fixture for error testing

### Goals

1. Create canonical example files based on 6.2.1 specification:
   - Basic example: 2 entities, simple constraints
   - Advanced example: Multiple entities, relationships, all constraint types, ensures clauses

2. Create test fixtures:
   - Valid fixture that exercises all supported features
   - Invalid fixture(s) that test error handling:
     - Missing required fields
     - Invalid constraint syntax
     - Unknown field types
     - Circular references (if applicable)

3. Validate examples work with existing validator:
   - Run `src/lattice_lock_validator/schema.py` against examples
   - Fix any issues in examples OR report validator bugs

4. Add tests for example validation:
   - Test that valid examples pass validation
   - Test that invalid examples produce appropriate errors

### Constraints

- Examples must follow the format specified in 6.2.1 design doc
- Examples should be realistic and useful for documentation
- Invalid examples should cover common user mistakes
- Tests must pass before PR

### Output

- Created example files in `examples/` directory
- Created test fixtures in `tests/fixtures/`
- New test file: `tests/test_lattice_examples.py`
- Summary of changes ready for PR description

### Acceptance Criteria

- [ ] `examples/basic/lattice.yaml` exists and is valid
- [ ] `examples/advanced/lattice.yaml` exists and is valid
- [ ] Test fixtures exist for valid and invalid cases
- [ ] All examples validate successfully with schema validator
- [ ] Tests cover example validation
- [ ] Examples are documented with comments explaining each section
