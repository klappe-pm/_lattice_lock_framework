---
title: integration_patterns
type: reference
status: stable
categories: [reference, cli]
sub_categories: [integration]
date_created: 2026-01-31
date_revised: 2026-01-31
file_ids: [cli-integration-001]
tags: [cli, integration, patterns, ci_cd, best_practices]
---

# Lattice Lock Integration Patterns

This document covers how Lattice Lock commands integrate with external systems, best practices by project phase, and the complete command ecosystem.

## Integration Points

### External System Connections

How Lattice Lock commands integrate with external systems.

```mermaid
graph TD
    subgraph "Lattice Lock"
        A[lattice init --ci-provider github]
        B[lattice mcp --transport sse]
        C[lattice feedback --storage github]
        D[lattice sheriff --format github]
    end

    subgraph "External Systems"
        E[GitHub Actions]
        F[GitHub Issues]
        G[IDE Extensions]
        H[Web Dashboards]
    end

    A --> E
    C --> F
    B --> G
    B --> H
    D --> E
```

## Best Practices by Phase

### Project Phase Recommendations

Which commands to emphasize at different project stages.

```mermaid
graph TD
    subgraph "Phase 1: Setup"
        P1A[lattice init]
        P1B[lattice doctor]
        P1C[lattice validate]
    end

    subgraph "Phase 2: Development"
        P2A[lattice compile]
        P2B[lattice test]
        P2C[lattice sheriff]
        P2D[lattice validate]
    end

    subgraph "Phase 3: Integration"
        P3A[lattice mcp]
        P3B[lattice chain]
        P3C[lattice ask]
    end

    subgraph "Phase 4: Production"
        P4A[lattice validate --schema-only]
        P4B[lattice test --format junit]
        P4C[lattice sheriff --format github]
        P4D[lattice feedback]
    end

    P1A --> P1B --> P1C
    P1C --> P2A --> P2B --> P2C
    P2C -.iterate.-> P2D -.iterate.-> P2A
    P2C --> P3A
    P3A --> P3B --> P3C
    P3C --> P4A --> P4B --> P4C --> P4D
```

## Command Cheat Sheet

### Quick Reference by Goal

```mermaid
mindmap
    root((Lattice Lock))
        Start Project
            lattice init
            lattice doctor
        Validate
            lattice validate
            lattice validate --fix
            lattice validate --schema-only
        Build
            lattice compile
            lattice compile --pydantic
            lattice compile --sqlmodel
        Test
            lattice test
            lattice test --generate
            lattice test --coverage
        Enforce
            lattice sheriff
            lattice sheriff --fix
            lattice sheriff --format json
        AI Tools
            lattice ask
            lattice chain run
            lattice chain resume
        Integrate
            lattice mcp
            lattice feedback
```

## Unified Command Ecosystem Diagram

### Complete Lattice Lock Command Integration

This comprehensive diagram shows all Lattice Lock commands, their subcommands, data flows, integrations, and how they connect throughout the entire development lifecycle.

```mermaid
graph TB
    %% Entry Points
    DEV[Developer/User]
    CI[CI/CD System]
    IDE[IDE/Editor]

    %% Core Artifacts
    SCHEMA[(lattice.yaml<br/>Schema)]
    MODELS[(Generated<br/>Models)]
    TESTS[(Test<br/>Contracts)]
    CODE[(Application<br/>Code)]

    %% Commands - Initialization
    subgraph INIT_GROUP["Project Initialization"]
        INIT[lattice init]
        DOCTOR[lattice doctor]
    end

    %% Commands - Validation
    subgraph VALID_GROUP["Validation and Quality"]
        VALIDATE[lattice validate]
        SHERIFF[lattice sheriff]
    end

    %% Commands - Build
    subgraph BUILD_GROUP["Code Generation"]
        COMPILE[lattice compile]
    end

    %% Commands - Testing
    subgraph TEST_GROUP["Testing"]
        TEST[lattice test]
    end

    %% Commands - AI Operations
    subgraph AI_GROUP["AI Operations"]
        ASK[lattice ask]
        CHAIN_RUN[chain run]
        CHAIN_RESUME[chain resume]
        CHAIN_HISTORY[chain history]
    end

    %% Commands - Integration
    subgraph INTEG_GROUP["Integration"]
        MCP[lattice mcp]
        FEEDBACK[lattice feedback]
    end

    %% External Systems
    GITHUB[GitHub]
    AGENTS[AI Agents]
    DB[(Database)]

    %% Developer Workflow
    DEV -->|1. Create| INIT
    INIT -->|generates| SCHEMA
    INIT --> DOCTOR
    DOCTOR -->|validates| DEV

    DEV -->|2. Edit| SCHEMA
    SCHEMA --> VALIDATE
    VALIDATE -->|valid| COMPILE
    VALIDATE -->|issues| DEV

    %% Compilation Flow
    COMPILE -->|generates| MODELS
    COMPILE -->|generates| TESTS
    SCHEMA -.source.-> COMPILE

    %% Development Flow
    MODELS -->|use| CODE
    DEV -->|3. Write| CODE
    CODE --> SHERIFF
    SHERIFF -.validates.-> SCHEMA
    SHERIFF -->|violations| CODE
    SHERIFF -->|pass| TEST

    %% Testing Flow
    TESTS -->|against| CODE
    TEST -.reads.-> TESTS
    TEST -->|validates| CODE
    TEST -->|fail| CODE
    TEST -->|pass| DEV

    %% AI Integration Flow
    DEV -->|4. Query| ASK
    ASK -.via.-> MCP
    MCP -->|exposes| SCHEMA
    MCP --> IDE
    MCP --> AGENTS

    DEV -->|5. Workflow| CHAIN_RUN
    CHAIN_RUN -.uses.-> ASK
    CHAIN_RUN -->|fails| CHAIN_RESUME
    CHAIN_RUN --> CHAIN_HISTORY
    CHAIN_RESUME --> CHAIN_HISTORY
    CHAIN_RESUME -.continues.-> CHAIN_RUN

    %% CI/CD Flow
    CI --> DOCTOR
    CI --> VALIDATE
    CI --> SHERIFF
    CI --> TEST
    CI --> GITHUB
    SHERIFF -.format.-> GITHUB
    TEST -.format.-> GITHUB

    %% Database Integration
    MODELS -.SQLModel.-> DB
    CODE --> DB

    %% Feedback Loop
    DEV -->|6. Feedback| FEEDBACK
    FEEDBACK -.github.-> GITHUB
    FEEDBACK -.improves.-> INIT
    FEEDBACK -.improves.-> VALIDATE
    FEEDBACK -.improves.-> TEST

    %% Continuous Validation
    SCHEMA -.continuous.-> VALIDATE
    SCHEMA -.continuous.-> SHERIFF
    SCHEMA -.continuous.-> TEST
    SCHEMA -.continuous.-> MCP

    %% Style Definitions
    classDef entryPoint fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    classDef artifact fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    classDef command fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef external fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000

    class DEV,CI,IDE entryPoint
    class SCHEMA,MODELS,TESTS,CODE,DB artifact
    class INIT,DOCTOR,VALIDATE,SHERIFF,COMPILE,TEST,ASK,CHAIN_RUN,CHAIN_RESUME,CHAIN_HISTORY,MCP,FEEDBACK command
    class GITHUB,AGENTS external
```

### Diagram Legend

**Node Colors:**
- Blue: Entry points (Developer, CI/CD, IDE)
- Yellow: Core artifacts (schemas, models, code, databases)
- Green: Lattice Lock commands
- Orange: External systems

**Connection Types:**
- Solid arrows: Direct flow or execution
- Dotted arrows: Optional or continuous operations
- Numbered paths: Developer workflow sequence

**Command Categories:**
- Project Initialization: Setup and environment verification
- Validation and Quality: Schema and code compliance
- Code Generation: Transform schemas to code
- Testing: Generate and run contract tests
- AI Operations: Query models and run pipelines
- Integration: External tools and feedback

### Key Integration Points

1. **Schema as Central Truth**: lattice.yaml is the single source of truth for all operations

2. **Multi-Stage Quality Gates**: Code flows through validate, compile, sheriff, and test stages

3. **AI-Enhanced Development**: Ask and chain commands integrate with MCP for context-aware assistance

4. **Bidirectional Feedback**: Developer actions inform the system and improve the framework

5. **CI/CD Native**: Commands provide JSON, GitHub, and JUnit output formats

6. **Resumable Workflows**: Chain commands support failure recovery

## Command Performance Characteristics

### Execution Time Categories

Understanding relative performance of different commands.

```mermaid
graph LR
    subgraph "Fast < 1s"
        F1[lattice doctor]
        F2[lattice validate --schema-only]
        F3[lattice mcp]
    end

    subgraph "Medium 1-10s"
        M1[lattice validate]
        M2[lattice compile]
        M3[lattice sheriff]
    end

    subgraph "Slow 10s+"
        S1[lattice test]
        S2[lattice chain run]
        S3[lattice ask --compare]
    end

    subgraph "Variable"
        V1[lattice ask]
        V2[lattice chain resume]
    end
```

## Command Output Types

### Output Format Decision Tree

Choosing the right output format for different scenarios.

```mermaid
flowchart TD
    A[Need Output] --> B{Audience?}

    B -->|Human| C{Detail Level?}
    C -->|Normal| D[Default Text]
    C -->|High| E[--verbose]

    B -->|Machine| F{Platform?}
    F -->|CI/CD| G{Which CI?}
    G -->|GitHub Actions| H[--format github]
    G -->|Jenkins/Generic| I[--format junit]
    F -->|API/Script| J[--format json]

    B -->|Both| K[--json + Parse]
```

## Command Execution States

### State Machine for Command Workflows

This state diagram shows typical states during Lattice Lock workflows.

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    Uninitialized --> Initialized: lattice init
    Initialized --> Validated: lattice validate
    Validated --> Compiled: lattice compile
    Compiled --> Tested: lattice test
    Tested --> Enforced: lattice sheriff
    Enforced --> Production: Deploy

    Validated --> Invalid: Validation Error
    Invalid --> Validated: Fix Schema

    Tested --> Failed: Test Failure
    Failed --> Tested: Fix Code

    Enforced --> Violated: Sheriff Error
    Violated --> Enforced: Fix Violations

    Production --> Maintained: lattice feedback
    Maintained --> Validated: Schema Update
```

## Command Interaction Patterns

### Parallel vs Sequential Execution

Understanding when commands can run in parallel or must be sequential.

```mermaid
graph TD
    subgraph "Parallel Operations"
        P1[lattice ask query1]
        P2[lattice ask query2]
        P3[lattice ask query3]
    end

    subgraph "Sequential Required"
        S1[lattice validate] --> S2[lattice compile]
        S2 --> S3[lattice test]
        S3 --> S4[lattice sheriff]
    end

    subgraph "Conditional Sequences"
        C1[lattice chain run] --> C2{Failed?}
        C2 -->|Yes| C3[lattice chain resume]
        C2 -->|No| C4[Complete]
        C3 --> C4
    end
```

## Summary

This document demonstrates how Lattice Lock commands integrate with external systems to provide:

1. **External System Integration**: Native support for GitHub, IDEs, and CI/CD pipelines
2. **Phase-Based Best Practices**: Clear guidance on which commands to use when
3. **Complete Ecosystem View**: Understanding of how all commands work together
4. **Performance Awareness**: Knowledge of command execution characteristics
5. **Output Flexibility**: Multiple output formats for different consumers
