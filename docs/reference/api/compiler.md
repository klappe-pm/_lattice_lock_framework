---
title: compiler
type: reference
status: stable
categories: [reference, api]
sub_categories: [compiler]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [api-compiler-001]
tags: [compiler, api, core]
---

# Compiler API

The `lattice_lock.compiler` module handles the polyglot compilation of Lattice Lock schemas into target language artifacts.

> [!NOTE]
> This module is currently under active development. The API described below is subject to change.

## Overview

The compiler takes a validated `ValidationResult` or a raw schema file and generates code (e.g., Pydantic models, TypeScript interfaces, SQL DDL) based on the defined entities.

## Future API

We anticipate the API will look similar to the following:

### `Compiler`

```python
class Compiler:
    def __init__(self, config: CompilerConfig): ...

    def compile(self, schema_path: str, output_dir: str, target: str): ...
```

**Arguments:**
- `schema_path` (str): Path to the `lattice.yaml` file.
- `output_dir` (str): Directory to output generated code.
- `target` (str): Target language (e.g., 'python', 'typescript').

## Usage Example (Preview)

```python
# Preview of expected usage
from lattice_lock.compiler import Compiler, CompilerConfig

compiler = Compiler(CompilerConfig())
compiler.compile("lattice.yaml", "./src/models", target="python")
```
