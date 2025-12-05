# API Reference

The Lattice Lock Framework exposes a comprehensive Python API for programmatic interaction with its core components. This reference documentation details the public interfaces, classes, and functions available to developers.

## Design Principles

The API is designed with the following principles in mind:

-   **Modularity**: Each component (Validator, Sheriff, Gauntlet, Orchestrator) is a standalone package that can be used independently or as part of the unified framework.
-   **Type Safety**: Extensive use of Python type hints to ensure code quality and developer productivity.
-   **Async-First**: Core operations, especially those involving I/O or model interaction, are asynchronous.
-   **Governance-First**: All APIs are built to enforce and respect the governance policies defined in `lattice.yaml`.

## Module Hierarchy

The framework is organized into the following top-level modules:

-   [Validator](validator.md): Core validation logic for schemas, environments, and agent manifests.
-   [Sheriff](sheriff.md): AST-based policy enforcement and code governance.
-   [Gauntlet](gauntlet.md): Automated test generation and execution.
-   [Orchestrator](orchestrator.md): Intelligent model routing and orchestration.
-   [Compiler](compiler.md): Polyglot compilation and build tools.
-   [Admin](admin.md): Administrative interfaces and dashboard backend.

## Import Patterns

The recommended way to import components is from their respective top-level packages:

```python
from lattice_lock_validator import validate_lattice_schema
from lattice_lock_sheriff import Sheriff
from lattice_lock_gauntlet import Gauntlet
from lattice_lock_orchestrator import Orchestrator
```

## Versioning

The API follows [Semantic Versioning](https://semver.org/).
-   **Major**: Breaking changes to public APIs.
-   **Minor**: New features and non-breaking changes.
-   **Patch**: Bug fixes and internal improvements.

Stability is guaranteed for public APIs documented here. Internal modules (prefixed with `_` or not documented) may change without notice.
