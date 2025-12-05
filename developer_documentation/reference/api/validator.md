# Validator API

The `lattice_lock.validator` module provides functions to validate Lattice Lock schemas, environment files, and project structures.

## Overview

This module is the core validation engine. It parses YAML definitions and enforces constraints defined in the Lattice Lock specification.

## Functions

### `validate_lattice_schema`

```python
def validate_lattice_schema(file_path: str) -> ValidationResult:
```

Validates a Lattice Lock schema definition file.

**Arguments:**
- `file_path` (str): Path to the schema file (YAML).

**Returns:**
- [`ValidationResult`](#validationresult): The result of the validation.

### `validate_env_file`

```python
def validate_env_file(file_path: str) -> ValidationResult:
```

Validates an environment configuration file.

### `validate_agent_manifest`

```python
def validate_agent_manifest(file_path: str) -> ValidationResult:
```

Validates an agent manifest file.

### `validate_repository_structure`

```python
def validate_repository_structure(root_path: str) -> ValidationResult:
```

Validates the project repository structure.

## Classes

### `ValidationResult`

Container for validation results.

**Attributes:**
- `valid` (bool): Whether the validation passed.
- `errors` (List[[`ValidationError`](#validationerror)]): List of validation errors.
- `warnings` (List[[`ValidationWarning`](#validationwarning)]): List of validation warnings.

**Methods:**

#### `add_error`

```python
def add_error(self, message: str, line_number: Optional[int] = None, field_path: Optional[str] = None):
```

Adds an error to the result.

#### `add_warning`

```python
def add_warning(self, message: str, line_number: Optional[int] = None, field_path: Optional[str] = None):
```

Adds a warning to the result.

### `ValidationError`

Represents a validation error.

**Attributes:**
- `message` (str): Error message.
- `line_number` (Optional[int]): Line number where the error occurred.
- `field_path` (Optional[str]): Path to the field causing the error.

### `ValidationWarning`

Represents a validation warning.

**Attributes:**
- `message` (str): Warning message.
- `line_number` (Optional[int]): Line number.
- `field_path` (Optional[str]): Field path.

## Usage Example

```python
from lattice_lock.validator import validate_lattice_schema

result = validate_lattice_schema("lattice.yaml")

if result.valid:
    print("Schema is valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message} at line {error.line_number}")
```
