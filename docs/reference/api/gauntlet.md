# Gauntlet API

The `lattice_lock.gauntlet` module generates semantic test contracts from Lattice Lock schemas.

## Overview

Gauntlet reads `ensures` clauses from your schema and generates `pytest` test files to verify that your data models adhere to these constraints.

## Classes

### `GauntletGenerator`

Generates pytest test contracts from Lattice Lock definitions.

```python
class GauntletGenerator:
    def __init__(self, lattice_file: str, output_dir: str): ...
```

**Attributes:**
- `parser` (LatticeParser): The parser for reading lattice definitions.
- `output_dir` (Path): Directory where generated tests will be saved.
- `env` (Environment): Jinja2 environment for template loading.

**Methods:**

#### `generate`

```python
def generate(self):
```

Generates test files for all parsed entities.

## Usage Example

```python
from lattice_lock.gauntlet import GauntletGenerator

generator = GauntletGenerator(
    lattice_file="lattice.yaml",
    output_dir="tests/contracts"
)

generator.generate()
```
