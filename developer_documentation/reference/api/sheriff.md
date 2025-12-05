# Sheriff Module

The `lattice_lock_sheriff` module provides AST-based validation for Python code, enforcing import discipline, type hints, and other code quality rules.

## Overview

Sheriff is designed to be a lightweight, fast, and extensible static analysis tool that integrates with the Lattice Lock Framework.

## Modules

### Core Validation (`sheriff.py`)

The main entry point for validation.

#### Functions

- `validate_file(file_path: Path, config: SheriffConfig) -> List[Violation]`: Validates a single file.
- `validate_path(path: Path, config: SheriffConfig, ignore_patterns: Optional[List[str]] = None) -> List[Violation]`: Validates a file or directory recursively.
- `validate_file_with_audit(...) -> Tuple[List[Violation], List[Violation]]`: Validates a file and returns both active and ignored violations.
- `validate_path_with_audit(...) -> Tuple[List[Violation], List[Violation]]`: Validates a path and returns both active and ignored violations.

### AST Visitor (`ast_visitor.py`)

#### Classes

- `SheriffVisitor(ast.NodeVisitor)`: Visits AST nodes and applies rules.
    - `visit(node: ast.AST)`: Visits a node.
    - `get_violations() -> List[Violation]`: Returns found violations.

### Rules (`rules.py`)

Defines the validation rules.

#### Classes

- `Rule(ABC)`: Abstract base class for rules.
- `ImportDisciplineRule(Rule)`: Checks for forbidden imports.
- `TypeHintRule(Rule)`: Checks for missing type hints.
- `VersionComplianceRule(Rule)`: Checks for version compliance (placeholder).
- `Violation`: Dataclass representing a rule violation.
    - `rule_id`: ID of the rule (e.g., SHERIFF_001).
    - `message`: Description of the violation.
    - `line_number`: Line number where it occurred.
    - `filename`: File where it occurred.

### Configuration (`config.py`)

#### Classes

- `SheriffConfig`: Configuration object for Sheriff.
    - `forbidden_imports`: List of forbidden module names.
    - `enforce_type_hints`: Boolean to enable type hint checks.

## Usage Examples

```python
from pathlib import Path
from lattice_lock_sheriff.sheriff import validate_path
from lattice_lock_sheriff.config import SheriffConfig

# Configure Sheriff
config = SheriffConfig(
    forbidden_imports=["os.system", "subprocess"],
    enforce_type_hints=True
)

# Validate a directory
violations = validate_path(Path("./src"), config)

if violations:
    print(f"Found {len(violations)} violations:")
    for v in violations:
        print(f"{v.filename}:{v.line_number} - {v.rule_id}: {v.message}")
else:
    print("No violations found.")
```
