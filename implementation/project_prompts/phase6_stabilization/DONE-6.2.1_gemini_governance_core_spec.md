# Governance Core & lattice.yaml Specification

**Task ID:** 6.2.1
**Phase:** 6.2 (Governance Core Loop)
**Author:** Gemini Antimatter
**Status:** Approved Design

## 1. Overview
The Governance Core is the heart of Lattice Lock. It allows developers to define rigorous schemas and behavioral contracts in a simple YAML format (`lattice.yaml`), which the framework compiles into runtime validation artifacts (Pydantic models, SQL tables, Pytest contracts).

## 2. Canonical lattice.yaml Format

The `lattice.yaml` file defines the data models and their associated rules.

### 2.1 Complete Example

```yaml
version: "2.1"
generated_module: "my_project_types"  # Name of python module to create

entities:
  User:
    fields:
      id: "uuid"
      username: "str"
      email: "str"
      age: "int"
      role: "enum(admin, user, guest)"
    constraints:
      username:
        min_length: 3
        max_length: 20
        pattern: "^[a-z0-9_]+$"
      age:
        gte: 18
        lt: 120
      email:
        format: "email"
    ensures:
      - "role == 'admin' implies email.endswith('@company.com')"
      - "username != id"

  Project:
    fields:
      id: "uuid"
      owner_id: "uuid"
      name: "str"
      budget: "decimal"
    constraints:
      budget:
        gte: 0.0
    ensures:
      - "budget > 1000.0 implies name.startswith('Enterprise ')"
```

### 2.2 Field Types
| Type | Python Equivalent | Notes |
| :--- | :--- | :--- |
| `str` | `str` | |
| `int` | `int` | |
| `float` | `float` | |
| `decimal` | `decimal.Decimal` | For currency/precision. |
| `bool` | `bool` | |
| `uuid` | `uuid.UUID` | |
| `datetime` | `datetime.datetime` | |
| `enum(val1, val2)` | `Enum` | Generates Python Enum class. |
| `list[type]` | `List[type]` | Generic list. |
| `optional[type]` | `Optional[type]` | Nullable field. |

### 2.3 Constraint Types
| Constraint | Description |
| :--- | :--- |
| `gt`, `lt`, `gte`, `lte` | Numeric bounds. |
| `min_length`, `max_length` | String/List length bounds. |
| `pattern` | Regex pattern (strings only). |
| `format` | Pre-defined formats: `email`, `url`, `ipv4`. |
| `unique` | Database uniqueness constraint. |

### 2.4 Semantic Contracts (`ensures`)
These are logical assertions checked by **Gauntlet** (via property-based testing) and optionally at runtime.
*   **Syntax:** Python-like expression strings.
*   **Scope:** Access to all fields of the entity instance.
*   **Logic:** Support for `implies`, `and`, `or`, `not`.

## 3. Compilation Pipeline

The `compile_lattice` process transforms `lattice.yaml` into usable code.

**Steps:**
1.  **Loader**: Read `lattice.yaml`.
2.  **Meta-Validation**: Validate structure against strict internal schema.
3.  **Generator (Artifacts)**:
    *   **Pydantic Models**: `src/generated/models.py`. Includes strict types and validators.
    *   **SQLModel**: (Optional) For database ORM.
    *   **Gauntlet Tests**: `tests/contracts/test_{entity}.py`. Generates Hypothesis strategies to rigorously fuzz the constraints and `ensures` clauses.

## 4. API Surface

### 4.1 Python API
The compiler should be importable to allow integration into larger build systems.

```python
# src/lattice_lock/compiler.py

def compile_lattice(
    source_path: str = "lattice.yaml",
    output_dir: str = "src/generated",
    generate_pydantic: bool = True,
    generate_sqlmodel: bool = False,
    generate_gauntlet: bool = True
) -> None:
    """
    Compiles lattice schema into artifacts.
    Raises SchemaValidationError on invalid input.
    """
    pass
```

### 4.2 CLI Command
Exposed via `lattice-lock compile`.

```bash
lattice-lock compile --output src/my_types --sqlmodel
```

## 5. File Locations

*   **Compiler Core**: `src/lattice_lock/compiler.py`
*   **Schema Definition**: `src/lattice_lock_validator/schema.py` (Existing, needs updates).
*   **Generated Output**: By default `src/generated/` (should be gitignored or checked in depending on workflow).

## 6. Implementation Tasks (Devin AI)

1.  **Create `src/lattice_lock/compiler.py`**:
    *   Implement file reading and parsing.
    *   Implement Pydantic generation logic (using jinja2 templates or AST generation).
2.  **Update `src/lattice_lock_validator/schema.py`**:
    *   Ensure it fully supports the new V2.1 spec (enums, complex constraints).
3.  **Create Example**:
    *   Add `examples/lattice.yaml` with the canonical example content.
4.  **Tests**:
    *   `tests/test_compiler.py`: End-to-end test (YAML -> Python file -> Import check).
    *   `tests/test_examples.py`: Verify example file is valid.
