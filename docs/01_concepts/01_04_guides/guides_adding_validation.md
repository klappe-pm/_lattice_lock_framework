---
title: "Adding Validation Rules"
type: tutorial
status: stable
categories: [Guides, Tutorials]
sub_categories: [Validation]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [tut-validation-001]
tags: [tutorial, validation, rules]
author: Education Agent
---

# Adding Validation Rules

This tutorial teaches you how to add constraints, ensures clauses, and custom validation rules to your Lattice Lock project. You'll learn to use Sheriff for AST validation and Gauntlet for semantic testing.

**Prerequisites:** Complete [Creating Your First Project](first_project.md) first.

## Overview of Validation Layers

Lattice Lock provides three validation layers:

| Layer | Tool | What It Checks |
|-------|------|----------------|
| Schema | `validate` | lattice.yaml structure, file existence, project structure |
| Static | `sheriff` | AST-based code analysis: imports, type hints, patterns |
| Semantic | `gauntlet` | Generated tests from entity definitions |

## Step 1: Add Constraints to Entities

First, upgrade your `lattice.yaml` to use v2.1 format with full entity schema support.

### Basic v2.1 Entity Definition

Replace the contents of `lattice.yaml` with:

```yaml
version: v2.1
generated_module: my_first_project_types

# Entity definitions with validation
entities:
  User:
    description: "User account entity"
    fields:
      id: int
      email: str
      name: str
      age: int
      status: str
      created_at: datetime
    constraints:
      id: {primary_key: true, auto_increment: true}
      email: {unique: true, max_length: 255}
      name: {min_length: 1, max_length: 100}
      age: {gte: 0, lte: 150}
      status: {enum: [pending, active, suspended, deleted]}
    ensures:
      - "email contains '@'"
      - "age >= 0"
      - "len(name) >= 1"
    indexes:
      - {fields: [email], unique: true}
      - {fields: [status]}

# Keep governance rules
config:
  forbidden_imports:
    - os.system
    - subprocess.call
    - eval
    - exec
  required_patterns:
    - type_hints
    - docstrings
  validation:
    strict_mode: false
    fail_on_warning: false
```

### Understanding Constraints

| Constraint | Type | Example | Description |
|------------|------|---------|-------------|
| `primary_key` | bool | `{primary_key: true}` | Mark as primary key |
| `auto_increment` | bool | `{auto_increment: true}` | Auto-increment integer |
| `unique` | bool | `{unique: true}` | Enforce uniqueness |
| `foreign_key` | string | `{foreign_key: User.id}` | Foreign key reference |
| `max_length` | int | `{max_length: 255}` | Maximum string length |
| `min_length` | int | `{min_length: 1}` | Minimum string length |
| `gt` | number | `{gt: 0}` | Greater than |
| `gte` | number | `{gte: 0}` | Greater than or equal |
| `lt` | number | `{lt: 100}` | Less than |
| `lte` | number | `{lte: 100}` | Less than or equal |
| `enum` | array | `{enum: [a, b, c]}` | Allowed values |

## Step 2: Add Ensures Clauses

Ensures clauses define business logic that must always be true. Add more complex rules:

```yaml
entities:
  Order:
    description: "E-commerce order"
    fields:
      id: int
      user_id: int
      total_cents: int
      item_count: int
      status: str
      shipping_address: str
      created_at: datetime
    constraints:
      id: {primary_key: true, auto_increment: true}
      user_id: {foreign_key: User.id}
      total_cents: {gte: 0}
      item_count: {gt: 0}
      status: {enum: [pending, confirmed, shipped, delivered, cancelled]}
    ensures:
      # Business rules as constraints
      - "total_cents >= 0"
      - "item_count > 0"
      - "status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']"
      - "len(shipping_address) >= 10"
    indexes:
      - {fields: [user_id]}
      - {fields: [status]}
      - {fields: [created_at]}
```

### Supported Ensures Expressions

| Expression Type | Syntax | Example |
|-----------------|--------|---------|
| Comparison | `field op value` | `"age >= 18"` |
| Membership | `field in [...]` | `"status in ['a', 'b']"` |
| Contains | `field contains 'x'` | `"email contains '@'"` |
| Length | `len(field) op value` | `"len(name) >= 1"` |
| Equality | `field == value` | `"is_verified == true"` |

## Step 3: Run Sheriff Validation

Sheriff performs AST-based static analysis on your Python code.

### Basic Sheriff Usage

```bash
lattice-lock sheriff src/
```

**Expected output (no violations):**
```
✓ No violations found in src/
```

**Expected output (with violations):**
```
src/services/user.py:5:1 - IMPORT001 - Forbidden import: os.system
src/services/user.py:15:5 - TYPE001 - Missing type hint for parameter 'data'
src/services/user.py:15:5 - DOC001 - Missing docstring for function 'process'

✗ Found 3 violation(s) in src/
```

### Sheriff Output Formats

Sheriff supports multiple output formats for CI integration:

```bash
# Human-readable (default)
lattice-lock sheriff src/ --format text

# JSON for scripting
lattice-lock sheriff src/ --format json

# GitHub Actions annotations
lattice-lock sheriff src/ --format github

# JUnit XML for CI tools
lattice-lock sheriff src/ --format junit
```

#### JSON Output Example

```bash
lattice-lock sheriff src/ --format json
```

```json
{
  "violations": [
    {
      "rule_id": "IMPORT001",
      "message": "Forbidden import: os.system",
      "line_number": 5,
      "filename": "src/services/user.py"
    }
  ],
  "ignored_violations": [],
  "count": 1,
  "ignored_count": 0,
  "target": "src/",
  "success": false
}
```

### Sheriff Caching

Sheriff caches results to speed up repeated runs:

```bash
# Run with caching (default)
lattice-lock sheriff src/

# Disable caching for fresh scan
lattice-lock sheriff src/ --no-cache

# Clear cache before running
lattice-lock sheriff src/ --clear-cache

# Use custom cache directory
lattice-lock sheriff src/ --cache-dir .my_cache
```

### Ignoring Files

Exclude files from Sheriff validation:

```bash
# Ignore specific patterns
lattice-lock sheriff src/ --ignore "**/test_*.py" --ignore "**/migrations/*"
```

## Step 4: Run Gauntlet Tests

Gauntlet generates and runs semantic tests based on your entity definitions.

### Generate Tests

```bash
lattice-lock gauntlet --generate
```

**Expected output:**
```
Generating tests from lattice.yaml into tests/gauntlet...
Generation complete.
```

This creates test files in `tests/gauntlet/`:

```
tests/gauntlet/
├── test_user_contracts.py
└── test_order_contracts.py
```

### Run Generated Tests

```bash
lattice-lock gauntlet --run
```

**Expected output:**
```
Running tests in tests/gauntlet...
================================ test session starts ================================
collected 8 items

tests/gauntlet/test_user_contracts.py::test_user_email_unique PASSED         [ 12%]
tests/gauntlet/test_user_contracts.py::test_user_email_max_length PASSED     [ 25%]
tests/gauntlet/test_user_contracts.py::test_user_age_bounds PASSED           [ 37%]
tests/gauntlet/test_user_contracts.py::test_user_status_enum PASSED          [ 50%]
tests/gauntlet/test_order_contracts.py::test_order_total_non_negative PASSED [ 62%]
tests/gauntlet/test_order_contracts.py::test_order_item_count_positive PASSED[ 75%]
tests/gauntlet/test_order_contracts.py::test_order_status_enum PASSED        [ 87%]
tests/gauntlet/test_order_contracts.py::test_order_address_length PASSED     [100%]

================================= 8 passed in 0.45s =================================
```

### Generate and Run Together

```bash
lattice-lock gauntlet --generate --run
```

### Gauntlet Output Formats

```bash
# JUnit XML report
lattice-lock gauntlet --format junit

# JSON report
lattice-lock gauntlet --format json

# GitHub Actions annotations
lattice-lock gauntlet --format github

# Multiple formats
lattice-lock gauntlet --format junit --format json
```

### Enable Coverage

```bash
lattice-lock gauntlet --coverage
```

**Output includes coverage report:**
```
----------- coverage: platform darwin, python 3.11.4 -----------
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
src/services/user.py             45      3    93%   67-69
src/services/order.py            38      2    95%   45-46
-----------------------------------------------------------
TOTAL                            83      5    94%
```

### Parallel Test Execution

Speed up tests with parallel execution (requires `pytest-xdist`):

```bash
# Auto-detect workers
lattice-lock gauntlet --parallel

# Specify number of workers
lattice-lock gauntlet --parallel 4
```

## Step 5: Fix Validation Errors

Let's walk through fixing common validation errors.

### Example: Fixing a Type Hint Violation

**Sheriff reports:**
```
src/services/user.py:20:5 - TYPE001 - Missing type hint for parameter 'user_data'
```

**Before (violation):**
```python
def create_user(self, user_data):
    return self._save(user_data)
```

**After (fixed):**
```python
def create_user(self, user_data: dict) -> dict:
    return self._save(user_data)
```

### Example: Fixing a Forbidden Import

**Sheriff reports:**
```
src/services/user.py:3:1 - IMPORT001 - Forbidden import: eval
```

**Before (violation):**
```python
result = eval(expression)  # Dangerous!
```

**After (fixed):**
```python
import ast
result = ast.literal_eval(expression)  # Safe alternative
```

### Example: Fixing a Constraint Violation

**Gauntlet test fails:**
```
FAILED test_user_contracts.py::test_user_email_contains_at
    AssertionError: Email validation failed: 'invalid-email'
```

**Fix:** Update your service to validate emails:

```python
def create_user(self, email: str, name: str) -> dict:
    """Create a new user with validation.

    Args:
        email: User's email address.
        name: User's display name.

    Returns:
        The created user dictionary.

    Raises:
        ValueError: If email is invalid.
    """
    if "@" not in email:
        raise ValueError(f"Invalid email: {email}")

    # ... rest of implementation
```

## Step 6: Run Full Validation Suite

Run all validation layers together:

```bash
# Schema validation
lattice-lock validate

# AST validation
lattice-lock sheriff src/

# Semantic tests
lattice-lock gauntlet --generate --run
```

Or create a validation script:

```bash
#!/bin/bash
# validate.sh - Run all validation

set -e  # Exit on first error

echo "=== Schema Validation ==="
lattice-lock validate

echo ""
echo "=== Sheriff AST Validation ==="
lattice-lock sheriff src/

echo ""
echo "=== Gauntlet Semantic Tests ==="
lattice-lock gauntlet --generate --run

echo ""
echo "✓ All validations passed!"
```

Make it executable and run:

```bash
chmod +x validate.sh
./validate.sh
```

## Step 7: Verbose Output for Debugging

When troubleshooting, use verbose mode:

```bash
# Verbose validation
lattice-lock -v validate

# Verbose Sheriff
lattice-lock -v sheriff src/
```

## Summary: Complete Validation Workflow

```bash
# 1. Validate configuration
lattice-lock validate

# 2. Run AST checks
lattice-lock sheriff src/

# 3. Generate and run semantic tests
lattice-lock gauntlet --generate --run

# 4. Run project tests
pytest tests/ -v
```

## What's Next?

Now that you understand validation, learn how to integrate it into your CI/CD pipeline.

**Continue to:** [CI/CD Integration](ci_integration.md)

## Quick Reference

| Command | Description |
|---------|-------------|
| `lattice-lock validate` | Run schema validation |
| `lattice-lock validate --schema-only` | Validate only lattice.yaml |
| `lattice-lock sheriff src/` | Run AST validation |
| `lattice-lock sheriff src/ --format json` | JSON output |
| `lattice-lock sheriff src/ --no-cache` | Skip caching |
| `lattice-lock gauntlet --generate` | Generate tests |
| `lattice-lock gauntlet --run` | Run tests |
| `lattice-lock gauntlet --coverage` | With coverage |

## See Also

- [CI/CD Integration](ci_integration.md) - Next tutorial
- [Configuration Reference](docs/reference/configuration.md) - Entity schema details
- [Sheriff Reference](docs/reference/cli/sheriff.md) - Complete Sheriff docs
- [Gauntlet Reference](docs/reference/cli/gauntlet.md) - Complete Gauntlet docs
