# Gauntlet Module

The `lattice_lock_gauntlet` module provides test generation and execution capabilities for the Lattice Lock Framework. It translates Lattice Lock definitions into executable pytest contracts.

## Overview

Gauntlet ensures that the implementation matches the constraints defined in the Lattice Lock schema.

## Modules

### Test Generator (`generator.py`)

Generates pytest files from parsed Lattice definitions.

#### Classes

- `GauntletGenerator`: Main generator class.
    - `__init__(lattice_file: str, output_dir: str)`: Initializes the generator.
    - `generate()`: Generates test files for all entities in the lattice file.

### Parser (`parser.py`)

Parses Lattice Lock YAML definitions into internal data structures.

#### Classes

- `LatticeParser`: Parses the YAML file.
    - `parse() -> List[EntityDefinition]`: Returns a list of parsed entities.
- `EntityDefinition`: Data class for an entity.
- `EnsuresClause`: Data class for a validation rule.

### Pytest Plugin (`plugin.py`)

A pytest plugin to collect results and generate reports (JSON, GitHub Summary).

#### Classes

- `GauntletPlugin`: The pytest plugin.
    - `pytest_sessionstart(session)`: Records start time.
    - `pytest_runtest_logreport(report)`: Collects test results.
    - `pytest_sessionfinish(session, exitstatus)`: Generates reports.

## Usage Examples

### Generating Tests

```python
from lattice_lock_gauntlet.generator import GauntletGenerator

# Generate tests from lattice.yaml to tests/generated
generator = GauntletGenerator("lattice.yaml", "tests/generated")
generator.generate()
```

### Running Tests with Plugin

```python
import pytest
from lattice_lock_gauntlet.plugin import GauntletPlugin

# Run pytest with the Gauntlet plugin
plugin = GauntletPlugin(json_report=True)
pytest.main(["tests/generated"], plugins=[plugin])
```
