# Governance Core & lattice.yaml Specification

## Overview

The Governance Core is the central nervous system of the Lattice Lock Framework. It enforces a "schema-first" approach where the `lattice.yaml` file serves as the single source of truth for:
1.  **Data Structure**: Entity definitions and types.
2.  **Data Integrity**: Field-level constraints (e.g., `gt`, `unique`).
3.  **Semantic Contracts**: Business logic invariants (`ensures` clauses).

This specification defines the canonical format of `lattice.yaml`, the compilation pipeline that transforms it into enforcement artifacts, and the API surface for interacting with the core.

## 1. Canonical lattice.yaml Format

The `lattice.yaml` file defines the data model and governance rules for a project. It must adhere to the following structure.

### Minimal Example

```yaml
version: v2.1
generated_module: types_v2

entities:
  Order:
    fields:
      id:
        type: uuid
        primary_key: true
      amount:
        type: decimal
        gt: 0
        scale: 2
      status:
        type: enum
        enum: [pending, filled, cancelled]
        default: pending
    ensures:
      - name: limit_check
        field: amount
        constraint: lte
        value: 10000
        description: "Orders cannot exceed $10,000 without manual review"

  Customer:
    fields:
      id:
        type: uuid
        primary_key: true
      email:
        type: str
        unique: true
      rating:
        type: int
        gte: 1
        lte: 5
```

### Field Types

Supported types for `fields`:

| Type | Description | Python Equivalent | SQL Equivalent |
| :--- | :--- | :--- | :--- |
| `uuid` | Universally Unique Identifier | `uuid.UUID` | `UUID` |
| `str` | Text string | `str` | `VARCHAR` / `TEXT` |
| `int` | Integer | `int` | `INTEGER` |
| `decimal` | Fixed-precision number | `decimal.Decimal` | `DECIMAL` / `NUMERIC` |
| `bool` | Boolean value | `bool` | `BOOLEAN` |
| `enum` | Enumerated set of strings | `enum.Enum` | `VARCHAR` (constrained) |

### Constraints

Constraints apply to individual fields.

| Constraint | Type | Description |
| :--- | :--- | :--- |
| `primary_key` | `bool` | Marks the field as the unique identifier for the entity. |
| `unique` | `bool` | Enforces global uniqueness for the field. |
| `gt` | `number` | Greater than. |
| `lt` | `number` | Less than. |
| `gte` | `number` | Greater than or equal to. |
| `lte` | `number` | Less than or equal to. |
| `scale` | `int` | Number of decimal places (only for `decimal`). |
| `default` | `any` | Default value if not provided. |
| `nullable` | `bool` | Whether the field can be null (default: `false`). |

### Ensures Clauses

`ensures` clauses define higher-level semantic contracts that may involve multiple fields or complex logic. These are compiled into **Gauntlet** test contracts.

```yaml
ensures:
  - name: <string>        # Unique identifier for the rule
    field: <string>       # Primary field this rule targets (for error reporting)
    constraint: <type>    # The type of check (gt, lt, custom, etc.)
    value: <any>          # The threshold or reference value
    description: <string> # Human-readable explanation of the rule
```

## 2. Compilation Pipeline

The `compile_lattice` process transforms the raw YAML into usable code and tests.

1.  **Parsing & Validation**:
    *   Load `lattice.yaml`.
    *   Validate structure against the meta-schema (schema-of-schemas).
    *   Validate type consistency (e.g., `gt` not applied to `bool`).
    *   *Tool:* `src/lattice_lock_validator/schema.py`

2.  **Code Generation (Types)**:
    *   Generate a Python module (e.g., `types_v2.py`) containing Pydantic models for each entity.
    *   Field constraints are mapped to Pydantic `Field()` validators.
    *   *Destination:* `src/<project_name>/generated/` (or user-configured path).

3.  **Test Generation (Contracts)**:
    *   Generate **Gauntlet** test files (pytest).
    *   Each `ensures` clause becomes a property-based test case.
    *   Boundary tests are automatically generated for numeric constraints.
    *   *Destination:* `tests/gauntlet/`

## 3. compile_lattice API Surface

The core logic should be encapsulated in a new module: `src/lattice_lock/core/compiler.py`.

### Python API

```python
@dataclass
class CompilationResult:
    success: bool
    generated_files: List[Path]
    errors: List[str]

def compile_lattice(
    source_path: Path,
    output_dir: Path,
    test_dir: Path,
    options: Dict[str, Any] = None
) -> CompilationResult:
    """
    Orchestrates the full compilation pipeline.

    Args:
        source_path: Path to lattice.yaml
        output_dir: Where to write generated type definitions
        test_dir: Where to write generated Gauntlet tests
        options: Optional flags (e.g., dry_run, strict_mode)
    """
```

### CLI Command

The `lattice-lock` CLI will expose this via:

```bash
lattice-lock compile --file ./lattice.yaml --out ./src/generated --tests ./tests/gauntlet
```

## 4. Integration Points

### Sheriff (Architecture Validator)
*   **Role**: Static analysis.
*   **Integration**: Sheriff reads `lattice.yaml` to understand the valid entities. It then scans the codebase to ensure no unauthorized imports or direct database access bypass the generated types/DAO (if applicable).
*   **Hook**: `lattice-lock check` runs Sheriff validation which now includes a "Schema Compliance" check.

### Gauntlet (Semantic Tester)
*   **Role**: Runtime verification.
*   **Integration**: Gauntlet *is* the test runner for the generated tests. It doesn't just run them; it provides the *fixtures* and *generators* to create data that satisfies the schema constraints, allowing it to fuzz-test the `ensures` clauses.
*   **Hook**: `lattice-lock test` executes the generated tests in `tests/gauntlet/`.

## 5. File Locations

*   **Compiler Logic**: `src/lattice_lock/core/compiler.py` (New Module)
*   **Command Entry**: `src/lattice_lock_cli/commands/compile.py`
*   **Existing Validators**: Keep `src/lattice_lock_validator/schema.py` but potentially refactor to be called by the compiler.
*   **Existing Generators**: Refactor `src/lattice_lock_gauntlet/generator.py` to be invoked by the compiler.

## 6. Implementation Tasks (Devin AI)

The following tasks are assigned to the implementation engineer (Devin AI) to realize this specification:

### 1. Refactor Validator
*   [ ] Enhance `src/lattice_lock_validator/schema.py` to support the full `lattice.yaml` spec defined above (enums, all constraints).
*   [ ] Add meta-schema validation for the `ensures` format.

### 2. Implement Compiler Core
*   [ ] Create `src/lattice_lock/core/` package.
*   [ ] Implement `compiler.py` with the `compile_lattice` function.
*   [ ] Implement Pydantic model generation logic (string template or Jinja2).

### 3. CLI Integration
*   [ ] Create `src/lattice_lock_cli/commands/compile.py`.
*   [ ] Register the `compile` command in the main CLI entry point.

### 4. Gauntlet Integration
*   [ ] Update `src/lattice_lock_gauntlet/generator.py` to accept the parsed entity objects from the compiler rather than parsing the file again itself (or ensure they share the parser).
*   [ ] Ensure generated tests import the *generated types* locally.

### 5. Verification
*   [ ] Create a sample `lattice.yaml` in `examples/`.
*   [ ] Write a test that runs the full compilation pipeline and asserts the output files exist and are valid Python.
