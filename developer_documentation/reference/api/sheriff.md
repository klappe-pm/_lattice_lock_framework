# Sheriff Module

The `lattice_lock_sheriff` module implements AST-based static analysis to enforce code governance policies, such as import discipline and type hint usage.

## Overview

Sheriff acts as a linter that is aware of the Lattice Lock governance rules. It ensures that code written by agents or developers adheres to the project's architectural constraints.

## Classes

### SheriffConfig

Configuration object for Sheriff validation rules.

```python
@dataclass
class SheriffConfig:
    forbidden_imports: List[str] = field(default_factory=list)
    enforce_type_hints: bool = True
    target_version: str = "3.10"
```

**Attributes:**

-   `forbidden_imports` (List[str]): List of module names that are not allowed to be imported.
-   `enforce_type_hints` (bool): If `True`, enforces the presence of type hints in function signatures.
-   `target_version` (str): The target Python version for compatibility checks.

### Violation

Represents a single rule violation found during analysis.

```python
@dataclass
class Violation:
    rule_id: str
    message: str
    line_number: int
    filename: str
```

**Attributes:**

-   `rule_id` (str): Unique identifier for the violated rule (e.g., "SHERIFF_001").
-   `message` (str): Human-readable description of the violation.
-   `line_number` (int): Line number where the violation occurred.
-   `filename` (str): Path to the file containing the violation.

## Functions

### validate_file

Validates a single Python file against the configuration.

```python
def validate_file(file_path: Path, config: SheriffConfig) -> List[Violation]:
    ...
```

**Arguments:**

-   `file_path` (Path): Path to the Python file.
-   `config` (SheriffConfig): Configuration object.

**Returns:**

-   `List[Violation]`: A list of violations found.

### validate_path

Validates a file or directory recursively.

```python
def validate_path(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: Optional[List[str]] = None,
) -> List[Violation]:
    ...
```

**Arguments:**

-   `path` (Path): Path to the file or directory.
-   `config` (SheriffConfig): Configuration object.
-   `ignore_patterns` (Optional[List[str]]): Glob patterns of files/directories to ignore.

**Returns:**

-   `List[Violation]`: A list of violations found (excluding ignored ones).

### validate_path_with_audit

Validates a path and returns both active and ignored violations for auditing purposes.

```python
def validate_path_with_audit(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: Optional[List[str]] = None,
) -> Tuple[List[Violation], List[Violation]]:
    ...
```

**Returns:**

-   `Tuple[List[Violation], List[Violation]]`: A tuple containing `(active_violations, ignored_violations)`.

## Rules

-   **SHERIFF_001 (Import Discipline)**: Checks for forbidden imports defined in `config.forbidden_imports`.
-   **SHERIFF_002 (Type Hints)**: Enforces return type hints on functions if `config.enforce_type_hints` is True.
-   **SHERIFF_003 (Version Compliance)**: Checks for Python version compatibility (placeholder).

## Usage Example

```python
from pathlib import Path
from lattice_lock_sheriff import SheriffConfig, validate_file

config = SheriffConfig(
    forbidden_imports=["os", "sys"],
    enforce_type_hints=True
)

violations = validate_file(Path("my_script.py"), config)

for v in violations:
    print(f"{v.filename}:{v.line_number} - {v.message} ({v.rule_id})")
```
