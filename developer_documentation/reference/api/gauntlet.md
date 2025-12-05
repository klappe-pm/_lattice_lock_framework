# Gauntlet Module

The `lattice_lock_gauntlet` module provides automated test generation and execution capabilities based on the `lattice.yaml` schema.

## Overview

Gauntlet translates the constraints and "ensures" clauses defined in your Lattice schema into executable pytest contracts. It also includes a pytest plugin for reporting results.

## Classes

### GauntletGenerator

Responsible for generating Python test files from the Lattice schema.

```python
class GauntletGenerator:
    def __init__(self, lattice_file: str, output_dir: str):
        ...
    
    def generate(self):
        ...
```

**Methods:**

-   `__init__(lattice_file: str, output_dir: str)`: Initializes the generator.
    -   `lattice_file`: Path to the `lattice.yaml` file.
    -   `output_dir`: Directory where generated tests will be saved.
-   `generate()`: Parses the schema and writes test files to the output directory.

### LatticeParser

Parses `lattice.yaml` into internal entity definitions.

```python
class LatticeParser:
    def __init__(self, lattice_file: str):
        ...

    def parse(self) -> List[EntityDefinition]:
        ...
```

**Methods:**

-   `parse() -> List[EntityDefinition]`: Returns a list of parsed entities with their fields and constraints.

### EntityDefinition

Data class representing a parsed entity.

```python
@dataclass
class EntityDefinition:
    name: str
    fields: Dict[str, Any]
    ensures: List[EnsuresClause]
```

### EnsuresClause

Data class representing a validation rule or constraint.

```python
@dataclass
class EnsuresClause:
    name: str
    field: str
    constraint: str
    value: Any
    description: str
```

### GauntletPlugin

A pytest plugin for enhanced reporting (JSON, GitHub Actions).

```python
class GauntletPlugin:
    def __init__(self, json_report: bool = False, github_report: bool = False):
        ...
```

**Configuration:**

-   `json_report` (bool): Enable JSON report generation (default: `False`, or via `GAUNTLET_JSON_REPORT` env var).
-   `github_report` (bool): Enable GitHub Actions summary and annotations (default: `False`, or via `GAUNTLET_GITHUB_REPORT` env var).

## Usage Example

### Generating Tests

```python
from lattice_lock_gauntlet import GauntletGenerator

generator = GauntletGenerator(
    lattice_file="lattice.yaml",
    output_dir="tests/gauntlet"
)
generator.generate()
```

### Running Tests

Gauntlet tests are standard pytest files. You can run them using the CLI or programmatically.

```bash
pytest tests/gauntlet
```
