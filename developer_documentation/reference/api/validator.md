# Validator Module

The `lattice_lock_validator` module provides core validation logic for the Lattice Lock Framework. It ensures that agent definitions, schemas, environment variables, and repository structures adhere to the framework's specifications.

## Overview

The validator is used by the `lattice-lock validate` CLI command and can also be used programmatically to verify compliance.

## Modules

### Schema Validation (`schema.py`)

Validates Lattice Lock schema definition files (YAML).

#### Classes

- `ValidationResult`: Container for validation results (valid status, errors, warnings).
- `ValidationError`: Represents a single validation error.
- `ValidationWarning`: Represents a single validation warning.

#### Functions

- `validate_lattice_schema(file_path: str) -> ValidationResult`: Validates a schema file.

### Agent Validation (`agents.py`)

Validates agent manifest files against the Lattice Lock agent specification.

#### Functions

- `validate_agent_manifest(file_path: str) -> ValidationResult`: Validates an agent manifest file.

### Environment Validation (`env.py`)

Validates environment variable files (`.env`) for required variables, naming conventions, and potential secrets.

#### Functions

- `validate_env_file(file_path: str, required_vars: Optional[List[str]] = None) -> ValidationResult`: Validates an env file.

### Structure Validation (`structure.py`)

Validates the repository directory structure and file naming conventions (snake_case).

#### Functions

- `validate_repository_structure(repo_path: str) -> ValidationResult`: Validates the entire repository structure.
- `validate_directory_structure(repo_path: str) -> ValidationResult`: Validates directory existence and nesting.
- `validate_file_naming(file_path: str, repo_root: str = "") -> ValidationResult`: Validates a single file's name.

## Usage Examples

```python
from lattice_lock_validator.schema import validate_lattice_schema
from lattice_lock_validator.agents import validate_agent_manifest

# Validate a schema
result = validate_lattice_schema("path/to/schema.yaml")
if not result.valid:
    for error in result.errors:
        print(f"Error: {error.message}")

# Validate an agent manifest
agent_result = validate_agent_manifest("agent_definitions/coder/coder_agent_definition.yaml")
if agent_result.valid:
    print("Agent manifest is valid!")
```
