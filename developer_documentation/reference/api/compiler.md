# Compiler Module (Future API)

> [!NOTE]
> This module is currently under design and development. The API described below is a proposal and subject to change.

The `lattice_lock_compiler` module will be responsible for compiling Lattice Lock definitions into executable code and other artifacts.

## Overview

The compiler transforms high-level Lattice Lock schemas into:
1.  Python data models (Pydantic/Dataclasses)
2.  Database migration scripts (SQLAlchemy/Alembic)
3.  API specifications (OpenAPI)
4.  Frontend client code (TypeScript/React)

## Proposed Modules

### Core Compiler (`compiler.py`)

#### Classes

- `LatticeCompiler`: Main compiler class.
    - `compile(schema_path: str, output_dir: str, targets: List[str])`: Compiles a schema to specified targets.
    - `watch(schema_path: str)`: Watches for changes and recompiles.

### Code Generators (`generators/`)

#### Classes

- `PythonGenerator`: Generates Python code.
- `TypescriptGenerator`: Generates TypeScript code.
- `SqlGenerator`: Generates SQL DDL.

## Usage Examples (Proposed)

```python
from lattice_lock_compiler import LatticeCompiler

compiler = LatticeCompiler()

# Compile schema to Python and TypeScript
compiler.compile(
    schema_path="lattice.yaml",
    output_dir="./generated",
    targets=["python", "typescript"]
)
```
