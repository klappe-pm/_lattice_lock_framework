# API Reference

Welcome to the Lattice Lock Framework API Reference. This documentation provides detailed information about the Python modules, classes, and functions available in the framework.

## Modules

The framework is divided into several key modules:

- **[Validator](validator.md)**: Schema validation and integrity checks.
- **[Sheriff](sheriff.md)**: AST-based static analysis and code governance.
- **[Gauntlet](gauntlet.md)**: Test generation and contract verification.
- **[Orchestrator](orchestrator.md)**: Intelligent LLM routing and task orchestration.
- **[Admin](admin.md)**: Backend API for project management and monitoring.
- **[Compiler](compiler.md)**: (Future) Schema compilation and code generation.

## Design Principles

The Lattice Lock API is designed with the following principles in mind:

1.  **Type Safety**: Extensive use of Python type hints for better developer experience and static analysis.
2.  **Modularity**: Components are loosely coupled and can be used independently.
3.  **Extensibility**: Interfaces are designed to be extended (e.g., custom Sheriff rules, new Orchestrator models).
4.  **Documentation**: All public APIs are documented with Google-style docstrings.

## Import Patterns

We recommend importing modules explicitly to keep the namespace clean:

```python
from lattice_lock_validator import validate_lattice_schema
from lattice_lock_sheriff import validate_file
from lattice_lock_orchestrator import ModelOrchestrator
```

## Versioning

The framework follows [Semantic Versioning](https://semver.org/).
- **Major**: Breaking changes.
- **Minor**: New features (backwards compatible).
- **Patch**: Bug fixes.

## Getting Started

If you are new to the framework, we recommend starting with the [Validator](validator.md) module to understand how to define and validate your project schemas.
