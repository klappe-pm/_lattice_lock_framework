# API Reference

The Lattice Lock Python API allows you to integrate the framework's capabilities directly into your Python applications and tools.

## Overview

Lattice Lock is designed as a modular framework. Each component can be used independently or as part of the cohesive system.

### Design Principles

- **Type Safety**: The API makes heavy use of Python type hints.
- **Modularity**: Components are loosely coupled.
- **Extensibility**: Interfaces are designed to be extended (e.g., custom validators, rules).

## Module Hierarchy

- [`lattice_lock.validator`](./validator.md): Core validation engine.
- [`lattice_lock.compiler`](./compiler.md): Polyglot schema compiler.
- [`lattice_lock.sheriff`](./sheriff.md): AST-based static analysis.
- [`lattice_lock.gauntlet`](./gauntlet.md): Semantic test generation.
- [`lattice_lock.orchestrator`](./orchestrator.md): LLM orchestration and routing.
- [`lattice_lock.admin`](./admin.md): Administrative and dashboard APIs.

## Import Patterns

We recommend importing the top-level package or specific submodules.

```python
import lattice_lock
from lattice_lock import validator
from lattice_lock.orchestrator import Orchestrator
```

## Versioning

Lattice Lock follows [Semantic Versioning](https://semver.org/).

- **Major (X.y.z)**: Breaking changes to the public API.
- **Minor (x.Y.z)**: New features, backwards compatible.
- **Patch (x.y.Z)**: Bug fixes, backwards compatible.

## Stability Guarantees

APIs documented here are considered public and stable. Internal modules (prefixed with `_` or not listed here) may change without notice.
