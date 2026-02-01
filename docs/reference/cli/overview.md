---
title: overview
type: reference
status: stable
categories: [reference, cli]
sub_categories: [overview]
date_created: 2026-01-31
date_revised: 2026-01-31
file_ids: [cli-overview-001]
tags: [cli, commands, overview, architecture]
---

# Lattice Lock Commands Overview

This document provides a high-level overview of all Lattice Lock CLI commands, their relationships, and how they connect to the core framework.

For detailed workflows and use cases, see [workflows.md](./workflows.md).
For integration patterns and external system connections, see [integration_patterns.md](./integration_patterns.md).

## Command Ecosystem Architecture

This diagram shows how all Lattice Lock commands relate to each other and the core framework components.

```mermaid
graph TD
    subgraph "Project Lifecycle"
        INIT[lattice init]
        DOCTOR[lattice doctor]
        VALIDATE[lattice validate]
    end

    subgraph "Development Workflow"
        COMPILE[lattice compile]
        TEST[lattice test]
        SHERIFF[lattice sheriff]
    end

    subgraph "AI Operations"
        ASK[lattice ask]
        CHAIN[lattice chain]
    end

    subgraph "Integration & Services"
        MCP[lattice mcp]
        FEEDBACK[lattice feedback]
    end

    subgraph "Core Framework"
        SCHEMA[lattice.yaml]
        MODELS[Pydantic Models]
        CONTRACTS[Test Contracts]
    end

    INIT --> SCHEMA
    INIT --> DOCTOR
    DOCTOR --> VALIDATE
    VALIDATE --> COMPILE
    COMPILE --> MODELS
    COMPILE --> CONTRACTS
    CONTRACTS --> TEST
    SHERIFF --> SCHEMA
    TEST --> SCHEMA
    ASK -.query.-> MCP
    CHAIN -.multi-step.-> ASK
    MCP --> SCHEMA
    FEEDBACK -.improvement.-> INIT
    VALIDATE -.verify.-> SHERIFF
```

## Command Relationships by Category

### Project Initialization Flow

```mermaid
flowchart LR
    A[New Project Need] --> B[lattice init]
    B --> C[Project Structure Created]
    C --> D[lattice doctor]
    D --> E{Environment OK?}
    E -->|No| F[Fix Dependencies]
    F --> D
    E -->|Yes| G[lattice validate]
    G --> H{Valid?}
    H -->|No| I[Fix Issues]
    I --> G
    H -->|Yes| J[Ready for Development]
```

### Subcommand Relationships

```mermaid
graph TB
    subgraph "lattice chain"
        CHAIN_RUN[chain run]
        CHAIN_RESUME[chain resume]
        CHAIN_HISTORY[chain history]
    end

    CHAIN_RUN --> CHAIN_HISTORY
    CHAIN_RUN -.fails.-> CHAIN_RESUME
    CHAIN_RESUME --> CHAIN_HISTORY
```

## Command Dependencies

### Direct Dependencies

This diagram shows which commands depend on outputs from other commands.

```mermaid
graph LR
    A[lattice init] --> B[lattice.yaml]
    B --> C[lattice validate]
    B --> D[lattice compile]
    B --> E[lattice sheriff]
    B --> F[lattice test]
    B --> G[lattice mcp]
    D --> H[Pydantic Models]
    D --> I[SQLModel Classes]
    D --> J[Test Contracts]
    J --> F
    C -.validates.-> B
    E -.enforces.-> B
    F -.verifies.-> B
```

### Optional Dependencies

Commands that can enhance or extend other commands.

```mermaid
graph TD
    A[lattice ask] -.can use.-> B[lattice mcp]
    C[lattice chain] -.orchestrates.-> A
    D[lattice validate --fix] -.improves.-> E[lattice sheriff]
    F[lattice test --coverage] -.extends.-> G[lattice test]
    H[lattice feedback] -.informs.-> I[All Commands]
```

## Command Flag Patterns

### Common Flag Combinations

Frequently used flag patterns across commands.

```mermaid
graph TD
    subgraph "Output Control"
        A[--verbose/-v]
        B[--json]
        C[--format]
    end

    subgraph "Path Control"
        D[--path/-p]
        E[--output/-o]
        F[--lattice]
    end

    subgraph "Mode Control"
        G[--fix]
        H[--generate]
        I[--run/--no-run]
    end

    subgraph "Filter Control"
        J[--schema-only]
        K[--env-only]
        L[--agents-only]
    end

    A --> M[lattice validate --verbose]
    B --> N[lattice doctor --json]
    C --> O[lattice sheriff --format github]
    D --> P[lattice validate --path .]
    E --> Q[lattice compile --output ./gen]
    F --> R[lattice sheriff --lattice custom.yaml]
    G --> S[lattice validate --fix]
    H --> T[lattice test --generate]
    J --> U[lattice validate --schema-only]
```

## Command Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **Project Lifecycle** | `init`, `doctor`, `validate` | Setup and verification |
| **Development** | `compile`, `test`, `sheriff` | Build and quality |
| **AI Operations** | `ask`, `chain` | AI-powered assistance |
| **Integration** | `mcp`, `feedback` | External tool support |

## Related Documentation

- **[CLI Reference](./README.md)** - Complete command reference with all options
- **[Workflows](./workflows.md)** - Detailed use case workflows and sequences
- **[Integration Patterns](./integration_patterns.md)** - External system integration
- **Individual Commands** - See specific command files for detailed documentation:
  - [init](./init.md), [doctor](./doctor.md), [validate](./validate.md)
  - [compile](./compile.md), [test](./test.md), [sheriff](./sheriff.md)
  - [ask](./ask.md), [chain](./chain.md)
  - [mcp](./mcp.md), [feedback](./feedback.md), [admin](./admin.md)
