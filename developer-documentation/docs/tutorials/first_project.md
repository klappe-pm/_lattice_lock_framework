# Creating Your First Project

This tutorial walks you through creating, exploring, and validating your first Lattice Lock project. By the end, you'll have a working project with validation passing.

**Prerequisites:** Complete [Getting Started](getting_started.md) first.

## Step 1: Create a New Project

Use the `init` command to scaffold a new project:

```bash
lattice-lock init my_first_project --template service
```

**Expected output:**
```
Creating service project 'my_first_project'...

Project created successfully!

Created 9 files in ./my_first_project

Next steps:
  cd my_first_project
  python -m venv venv
  source venv/bin/activate
  pip install lattice-lock
  lattice-lock validate
```

### Template Options

| Template | Use Case |
|----------|----------|
| `service` | REST APIs, microservices, backend services (default) |
| `agent` | AI agents with tool definitions |
| `library` | Reusable Python packages |

**Example with different templates:**
```bash
# Create an agent project
lattice-lock init my_agent --template agent

# Create a library project
lattice-lock init my_library --template library
```

### CI Provider Options

You can also specify a CI provider:

```bash
# Default: GitHub Actions
lattice-lock init my_project

# AWS CodeBuild
lattice-lock init my_project --ci aws
```

## Step 2: Navigate to Your Project

```bash
cd my_first_project
```

## Step 3: Explore the Project Structure

Your new project has this structure:

```
my_first_project/
├── .github/
│   └── workflows/
│       └── lattice-lock.yml    # CI/CD workflow
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── lattice.yaml                # Lattice Lock configuration
├── src/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── my_first_project.py # Service scaffold
│   └── shared/
│       └── __init__.py
└── tests/
    └── test_contracts.py       # Contract tests
```

### Key Files Explained

#### `lattice.yaml` - The Configuration File

This is the heart of your Lattice Lock project. Open it to see:

```yaml
# Lattice Lock Configuration
# Generated for: my_first_project
# Documentation: https://github.com/klappe-pm/lattice-lock-framework

version: "1.0"

# Project metadata
project:
  name: my_first_project
  description: "A service project managed by Lattice Lock Framework"

# Module definitions
modules:
  - name: my_first_project
    path: src/my_first_project
    type: service

# Entity definitions (contracts, services, etc.)
entities:
  # Example entity - customize as needed
  - name: example_service
    type: service
    module: my_first_project
    description: "Example service entity"

# Governance rules
config:
  # Imports that should never be used
  forbidden_imports:
    - os.system
    - subprocess.call
    - eval
    - exec

  # Required patterns for code quality
  required_patterns:
    - type_hints
    - docstrings

  # Validation settings
  validation:
    strict_mode: false
    fail_on_warning: false
```

#### Understanding `lattice.yaml` Sections

| Section | Purpose |
|---------|---------|
| `version` | Schema version for compatibility |
| `project` | Basic project metadata |
| `modules` | Source code module definitions |
| `entities` | Domain entities and services |
| `config` | Governance rules and validation settings |

#### `tests/test_contracts.py` - Contract Tests

Placeholder tests that validate your project follows conventions:

```python
"""
Contract tests for my_first_project.

These tests validate that the project adheres to Lattice Lock contracts.
"""

import pytest


def test_placeholder() -> None:
    """Placeholder test - replace with actual contract tests."""
    assert True


def test_project_name_valid() -> None:
    """Verify project name follows conventions."""
    project_name = "my_first_project"
    assert project_name.islower()
    assert " " not in project_name
```

#### `.github/workflows/lattice-lock.yml` - CI Workflow

Automated validation in GitHub Actions:

```yaml
name: Lattice Lock Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install lattice-lock
      - run: lattice-lock validate
      - run: lattice-lock sheriff src/
      - run: lattice-lock gauntlet
```

## Step 4: Run Initial Validation

Now let's validate the project to make sure everything is set up correctly:

```bash
lattice-lock validate
```

**Expected output:**
```
Validating project at: .

Schema Validation:
  ✓ lattice.yaml: passed

Environment Validation:
  ⚠ No .env file found

Agent Manifest Validation:
  ⚠ No agent definitions found

Structure Validation:
  ✓ Repository structure: passed

==================================================
✓ All validations passed!
```

### Understanding Validation Results

| Status | Meaning |
|--------|---------|
| ✓ passed | Validation succeeded |
| ⚠ warning | Non-critical issue (validation still passes) |
| ✗ failed | Critical issue (validation fails) |

The warnings about `.env` and agent definitions are normal for a new service project.

## Step 5: Add Your First Entity

Let's enhance the `lattice.yaml` with a real entity. Open `lattice.yaml` and modify the `entities` section:

```yaml
# Entity definitions (contracts, services, etc.)
entities:
  # Your first entity
  - name: user_service
    type: service
    module: my_first_project
    description: "User management service"

  # A data entity with schema (v2.1 format preview)
  # Uncomment when ready to use v2.1 features:
  # User:
  #   description: "User account"
  #   fields:
  #     id: int
  #     email: str
  #     created_at: datetime
  #   constraints:
  #     id: {primary_key: true}
  #     email: {unique: true, max_length: 255}
  #   ensures:
  #     - "email contains '@'"
```

Run validation again:

```bash
lattice-lock validate
```

**Expected output:**
```
Validating project at: .

Schema Validation:
  ✓ lattice.yaml: passed

Environment Validation:
  ⚠ No .env file found

Agent Manifest Validation:
  ⚠ No agent definitions found

Structure Validation:
  ✓ Repository structure: passed

==================================================
✓ All validations passed!
```

## Step 6: Create a Service Implementation

Create a simple service in `src/services/my_first_project.py`:

```python
"""
User service implementation for my_first_project.

This service handles user management operations.
"""

from typing import Optional


class UserService:
    """Service for managing user operations."""

    def __init__(self) -> None:
        """Initialize the user service."""
        self._users: dict[int, dict] = {}
        self._next_id: int = 1

    def create_user(self, email: str, name: str) -> dict:
        """Create a new user.

        Args:
            email: User's email address.
            name: User's display name.

        Returns:
            The created user dictionary.
        """
        user_id = self._next_id
        self._next_id += 1

        user = {
            "id": user_id,
            "email": email,
            "name": name,
        }
        self._users[user_id] = user
        return user

    def get_user(self, user_id: int) -> Optional[dict]:
        """Get a user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The user dictionary if found, None otherwise.
        """
        return self._users.get(user_id)

    def list_users(self) -> list[dict]:
        """List all users.

        Returns:
            List of all user dictionaries.
        """
        return list(self._users.values())
```

## Step 7: Run Full Validation

Now run the complete validation suite:

```bash
# Basic validation
lattice-lock validate

# AST-based validation (Sheriff)
lattice-lock sheriff src/

# Run tests
pytest tests/ -v
```

### Sheriff Validation

```bash
lattice-lock sheriff src/
```

**Expected output (if no violations):**
```
✓ No violations found in src/
```

If Sheriff finds issues, you'll see:
```
src/services/my_first_project.py:15:1 - IMPORT001 - Forbidden import: os.system
src/services/my_first_project.py:23:5 - TYPE001 - Missing type hint for parameter 'data'

✗ Found 2 violation(s) in src/
```

### Running Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
================================ test session starts ================================
collected 2 items

tests/test_contracts.py::test_placeholder PASSED                              [ 50%]
tests/test_contracts.py::test_project_name_valid PASSED                       [100%]

================================= 2 passed in 0.12s =================================
```

## Common Mistakes and How to Fix Them

### Invalid Project Name

```
Error: Invalid project name 'My Project'. Name must be snake_case...
```

**Fix:** Use lowercase letters, numbers, and underscores only:
```bash
lattice-lock init my_project    # ✓ Correct
lattice-lock init MyProject     # ✗ Wrong
lattice-lock init my-project    # ✗ Wrong
```

### Missing Type Hints

Sheriff may complain about missing type hints:

```
TYPE001 - Missing type hint for parameter 'data'
```

**Fix:** Add type hints to all function parameters and return values:

```python
# Wrong
def process(data):
    return data

# Correct
def process(data: dict) -> dict:
    return data
```

### Missing Docstrings

Sheriff may flag missing docstrings:

```
DOC001 - Missing docstring for function 'process'
```

**Fix:** Add docstrings to all public functions and classes:

```python
def process(data: dict) -> dict:
    """Process the input data.

    Args:
        data: Input dictionary to process.

    Returns:
        Processed dictionary.
    """
    return data
```

### Forbidden Imports

```
IMPORT001 - Forbidden import: os.system
```

**Fix:** Use safer alternatives:

```python
# Wrong - forbidden
import os
os.system("ls")

# Correct - use subprocess with proper handling
import subprocess
subprocess.run(["ls"], check=True, capture_output=True)
```

## What's Next?

Your first project is now set up and validated! Next, learn how to add more sophisticated validation rules.

**Continue to:** [Adding Validation Rules](adding_validation.md)

## Quick Reference

| Command | Description |
|---------|-------------|
| `lattice-lock init NAME` | Create new project |
| `lattice-lock init NAME --template TYPE` | Create with specific template |
| `lattice-lock validate` | Run all validators |
| `lattice-lock validate --schema-only` | Validate only lattice.yaml |
| `lattice-lock sheriff src/` | Run AST validation |
| `pytest tests/ -v` | Run tests |

## See Also

- [Adding Validation Rules](adding_validation.md) - Next tutorial
- [Configuration Reference](../reference/configuration.md) - Complete lattice.yaml docs
- [CLI Reference](../reference/cli/init.md) - init command details
