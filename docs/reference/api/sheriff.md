---
title: sheriff
type: reference
status: stable
categories: [reference, api]
sub_categories: [governance]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [api-sheriff-001]
tags: [sheriff, api, validation]
---

# Sheriff API

The `lattice_lock.sheriff` module performs AST-based static analysis on Python code to enforce architectural and stylistic rules.

## Overview

Sheriff uses Python's `ast` module to inspect code structure without executing it. It checks for rule violations such as forbidden imports, naming conventions, and type hint usage.

## Functions

### `validate_file`

```python
def validate_file(file_path: Path, config: SheriffConfig) -> List[Violation]:
```

Validate a single Python file.

**Arguments:**
- `file_path` (Path): Path to the Python file.
- `config` ([`SheriffConfig`](#sheriffconfig)): Sheriff configuration object.

**Returns:**
- List[[`Violation`](#violation)]: List of violations found.

### `validate_path`

```python
def validate_path(path: Path, config: SheriffConfig, ignore_patterns: Optional[List[str]] = None) -> List[Violation]:
```

Validate a file or directory recursively.

**Arguments:**
- `path` (Path): Path to validate (file or directory).
- `config` ([`SheriffConfig`](#sheriffconfig)): Sheriff configuration.
- `ignore_patterns` (Optional[List[str]]): List of glob patterns to ignore.

**Returns:**
- List[[`Violation`](#violation)]: List of violations found.

## Classes

### `Violation`

Represents a rule violation found by Sheriff.

**Attributes:**
- `rule_id` (str): ID of the violated rule.
- `message` (str): Description of the violation.
- `line_number` (int): Line number where the violation occurred.
- `filename` (str): File where the violation occurred.
- `severity` (str): Severity level (e.g., "error", "warning").

### `SheriffConfig`

Configuration object for Sheriff.

*(See `lattice_lock.sheriff.config` for details)*

## Usage Example

```python
from pathlib import Path
from lattice_lock.sheriff import validate_file, SheriffConfig

config = SheriffConfig()
violations = validate_file(Path("src/main.py"), config)

for v in violations:
    print(f"{v.filename}:{v.line_number} - {v.message}")
```
