# Validator Module

The `lattice_lock_validator` module provides core validation logic for the Lattice Lock Framework. It ensures that schemas, environment configurations, agent manifests, and repository structures adhere to the defined governance policies.

## Overview

This module is the first line of defense in the governance pipeline. It is used by the CLI, CI/CD workflows, and the pre-commit hooks to enforce standards.

## Classes

### ValidationResult

A data class representing the outcome of a validation operation.

```python
@dataclass
class ValidationResult:
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
```

**Attributes:**

-   `valid` (bool): `True` if no errors were found, `False` otherwise.
-   `errors` (List[ValidationError]): A list of critical errors that caused validation to fail.
-   `warnings` (List[ValidationWarning]): A list of non-critical warnings.

**Methods:**

-   `add_error(message: str, line_number: Optional[int] = None, field_path: Optional[str] = None)`: Adds an error to the result.
-   `add_warning(message: str, line_number: Optional[int] = None, field_path: Optional[str] = None)`: Adds a warning to the result.

### ValidationError

```python
@dataclass
class ValidationError:
    message: str
    line_number: Optional[int] = None
    field_path: Optional[str] = None
```

### ValidationWarning

```python
@dataclass
class ValidationWarning:
    message: str
    line_number: Optional[int] = None
    field_path: Optional[str] = None
```

## Functions

### validate_lattice_schema

Validates the `lattice.yaml` schema definition file.

```python
def validate_lattice_schema(file_path: str) -> ValidationResult:
    ...
```

**Arguments:**

-   `file_path` (str): Path to the `lattice.yaml` file.

**Returns:**

-   `ValidationResult`: The result of the validation.

**Checks:**

-   Valid YAML syntax.
-   Required sections: `version`, `generated_module`, `entities`.
-   Version format (Semantic Versioning).
-   Entity definitions, field types, and constraints.
-   Interface definitions and entity references.

### validate_env_file

Validates `.env` files for security and configuration standards.

```python
def validate_env_file(file_path: str, required_vars: Optional[List[str]] = None) -> ValidationResult:
    ...
```

**Arguments:**

-   `file_path` (str): Path to the `.env` file.
-   `required_vars` (Optional[List[str]]): List of environment variables that must be present. Defaults to `['ORCHESTRATOR_STRATEGY', 'LOG_LEVEL']`.

**Returns:**

-   `ValidationResult`: The result of the validation.

**Checks:**

-   Variable naming convention (`UPPER_SNAKE_CASE`).
-   Potential plaintext secrets (keys ending in `_KEY`, `_SECRET`, etc. with non-placeholder values).
-   Presence of required variables.

### validate_agent_manifest

Validates agent definition files (e.g., `coding_agent_definition.yaml`).

```python
def validate_agent_manifest(file_path: str) -> ValidationResult:
    ...
```

**Arguments:**

-   `file_path` (str): Path to the agent definition file.

**Returns:**

-   `ValidationResult`: The result of the validation.

**Checks:**

-   Valid YAML syntax.
-   Required top-level sections: `agent`, `directive`, `responsibilities`, `scope`.
-   `agent.identity` fields: `name`, `version`, `description`, `role`.
-   `directive` fields: `primary_goal`.
-   `responsibilities` list structure.
-   `scope` fields: `can_access`, `cannot_access`.

### validate_repository_structure

Validates the project's directory structure and file naming conventions.

```python
def validate_repository_structure(repo_path: str) -> ValidationResult:
    ...
```

**Arguments:**

-   `repo_path` (str): Path to the root of the repository.

**Returns:**

-   `ValidationResult`: The result of the validation.

**Checks:**

-   Required root directories: `agent_definitions/`, `src/`, `scripts/`.
-   Required root files: `.gitignore`, `README.md`.
-   Agent definition file placement and naming (`{category}_{name}_definition.yaml`).
-   File naming convention (`snake_case` for most files).
-   Prohibited file types/names.

## Usage Example

```python
from lattice_lock_validator import validate_lattice_schema

result = validate_lattice_schema("lattice.yaml")

if result.valid:
    print("Schema is valid!")
    for warning in result.warnings:
        print(f"Warning: {warning.message}")
else:
    print("Schema validation failed:")
    for error in result.errors:
        print(f"Error: {error.message} at line {error.line_number}")
```
