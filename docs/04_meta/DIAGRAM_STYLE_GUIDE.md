# Diagram Style Guide

This guide defines the standard styling and best practices for Mermaid diagrams within the Lattice Lock Framework documentation.

## Standard Color Palette

We use a standard set of `classDef` styles to ensure consistency across all diagrams.

### Class Definitions

Copy and paste these definitions into the top of your mermaid diagrams:

```mermaid
%% Standard Class Definitions
classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
classDef agent fill:#e0f2f1,stroke:#004d40,stroke-width:2px;
classDef cli fill:#fff3e0,stroke:#e65100,stroke-width:2px;
classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5;
classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px;
```

### Usage

Apply these classes to nodes using the `:::classname` syntax.

- **Core** (`:::core`): Core infrastructure components (Orchestrator, Sheriff, Gauntlet, Database).
- **Agent** (`:::agent`): AI Agents and sub-agents.
- **CLI** (`:::cli`): User interfaces, CLI commands, and meaningful user interactions.
- **External** (`:::external`): 3rd party APIs, cloud providers, and external systems.
- **Error** (`:::error`): Failure paths, error states, and exception handling.

## Directionality

- **Flowcharts**: Use `TD` (Top-Down) for process flows and decision trees. Use `LR` (Left-Right) for system architecture and data pipelines.
- **Sequence**: Standard top-down time flow.
- **Class**: Standard top-down hierarchy.

## Node Naming

Nodes should be linked to metadata where possible using the `file_id` format if applicable (Phase 2).
