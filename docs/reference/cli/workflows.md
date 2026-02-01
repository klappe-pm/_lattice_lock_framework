---
title: workflows
type: reference
status: stable
categories: [reference, cli]
sub_categories: [workflows]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-workflows-001]
tags: [cli, workflows, use_cases, examples]
---

# Lattice Lock Workflows

This document provides detailed workflows showing how Lattice Lock commands work together in various development scenarios.

## Use Case 1: New Agent Project Setup

Complete workflow for initializing an AI agent project.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Init as lattice init
    participant Doctor as lattice doctor
    participant Validate as lattice validate
    participant Compile as lattice compile
    
    Dev->>Init: init my_agent --type agent --with-agents
    Init->>Init: Create directory structure
    Init->>Init: Generate lattice.yaml
    Init-->>Dev: Project created
    Dev->>Doctor: doctor
    Doctor->>Doctor: Check Python version
    Doctor->>Doctor: Check dependencies
    Doctor->>Doctor: Check env vars
    Doctor-->>Dev: Environment healthy
    Dev->>Validate: validate
    Validate->>Validate: Check schema
    Validate->>Validate: Check structure
    Validate-->>Dev: Project valid
    Dev->>Compile: compile
    Compile->>Compile: Generate Pydantic models
    Compile->>Compile: Generate test contracts
    Compile-->>Dev: Artifacts ready
```

## Use Case 2: Schema-Driven Development

Workflow showing how schema changes propagate through the system.

```mermaid
flowchart TD
    A[Define Entity in Schema] --> B[lattice validate --schema-only]
    B --> C{Valid?}
    C -->|No| A
    C -->|Yes| D[lattice compile --pydantic]
    D --> E[Models Generated]
    E --> F[Write Business Logic]
    F --> G[lattice test --generate]
    G --> H[Contract Tests Created]
    H --> I[lattice test --run]
    I --> J{Tests Pass?}
    J -->|No| F
    J -->|Yes| K[lattice sheriff]
    K --> L{Sheriff Pass?}
    L -->|No| F
    L -->|Yes| M[Complete]
```

## Use Case 3: AI Query Workflow

How AI operations integrate with the framework.

```mermaid
graph TD
    A[Development Question] --> B{Query Type?}
    B -->|Simple| C[lattice ask]
    B -->|Complex Multi-Step| D[lattice chain run]
    C --> E[Model Selection]
    E --> F[Execute Query]
    F --> G[Return Answer]
    D --> H[Load Pipeline YAML]
    H --> I[Execute Step 1]
    I --> J[Execute Step 2]
    J --> K[Execute Step 3]
    K --> L{Success?}
    L -->|No| M[lattice chain resume]
    L -->|Yes| N[Aggregate Results]
    M --> J
```

## Use Case 4: CI/CD Pipeline Integration

Complete CI/CD workflow using Lattice Lock commands.

```mermaid
flowchart LR
    A[Git Push] --> B[CI Triggered]
    B --> C[lattice doctor --json]
    C --> D{Env OK?}
    D -->|No| E[Fail Build]
    D -->|Yes| F[lattice validate]
    F --> G{Valid?}
    G -->|No| E
    G -->|Yes| H[lattice compile]
    H --> I[lattice sheriff --format github]
    I --> J{Sheriff Pass?}
    J -->|No| E
    J -->|Yes| K[lattice test --format junit]
    K --> L{Tests Pass?}
    L -->|No| E
    L -->|Yes| M[Deploy]
```

## Use Case 5: MCP Server Integration

How the MCP server enables external tool integration.

```mermaid
sequenceDiagram
    participant IDE as IDE/Editor
    participant MCP as lattice mcp
    participant Schema as lattice.yaml
    participant Validate as Validator
    
    IDE->>MCP: Start MCP server
    MCP->>MCP: Initialize transport
    MCP-->>IDE: Server ready
    IDE->>MCP: List resources
    MCP->>Schema: Read schemas
    Schema-->>MCP: Schema content
    MCP-->>IDE: Available resources
    IDE->>MCP: Call validate tool
    MCP->>Validate: Execute validation
    Validate-->>MCP: Results
    MCP-->>IDE: Validation output
    IDE->>IDE: Display results to user
```

## Development Workflow

The typical daily development cycle with Lattice Lock commands.

```mermaid
flowchart TD
    A[Start Development] --> B[Edit lattice.yaml]
    B --> C[lattice validate]
    C --> D{Schema Valid?}
    D -->|No| B
    D -->|Yes| E[lattice compile]
    E --> F[Generated Models]
    F --> G[Write Application Code]
    G --> H[lattice sheriff]
    H --> I{Code Valid?}
    I -->|No| G
    I -->|Yes| J[lattice test]
    J --> K{Tests Pass?}
    K -->|No| G
    K -->|Yes| L[Commit Changes]
    L --> M[lattice feedback]
```

## Multi-Environment Deployment

Using Lattice Lock across development, staging, and production.

```mermaid
flowchart TD
    A[Development] --> B[lattice validate]
    B --> C[lattice test]
    C --> D{Pass?}
    D -->|No| A
    D -->|Yes| E[Commit to Git]
    E --> F[CI: lattice doctor]
    F --> G[CI: lattice validate]
    G --> H[CI: lattice sheriff]
    H --> I[CI: lattice test --coverage]
    I --> J{All Pass?}
    J -->|No| K[Reject PR]
    J -->|Yes| L[Merge to Main]
    L --> M[Deploy to Staging]
    M --> N[Staging Tests]
    N --> O{Pass?}
    O -->|No| P[Rollback]
    O -->|Yes| Q[Deploy to Production]
    Q --> R[Production Monitoring]
    R --> S[lattice feedback]
```

## Agent Development Lifecycle

Specialized workflow for AI agent development.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Init as lattice init
    participant Ask as lattice ask
    participant Chain as lattice chain
    participant Test as lattice test
    participant MCP as lattice mcp
    
    Dev->>Init: init agent --type agent --with-agents
    Init-->>Dev: Agent project created
    Dev->>Ask: ask "Design agent architecture"
    Ask-->>Dev: Architecture suggestions
    Dev->>Dev: Define agent in lattice.yaml
    Dev->>Chain: chain run agent_pipeline.yaml
    Chain->>Chain: Generate → Refine → Test
    Chain-->>Dev: Agent code generated
    Dev->>Test: test --generate
    Test-->>Dev: Contract tests created
    Dev->>Test: test --run
    Test-->>Dev: Tests pass
    Dev->>MCP: mcp --transport stdio
    MCP-->>Dev: Agent accessible via MCP
```

## Schema Evolution Workflow

Managing schema changes over time.

```mermaid
flowchart TD
    A[Existing Schema] --> B[Propose Changes]
    B --> C[lattice validate]
    C --> D{Breaking Changes?}
    D -->|Yes| E[Review Impact]
    D -->|No| F[lattice compile]
    E --> G{Acceptable?}
    G -->|No| B
    G -->|Yes| F
    F --> H[Update Models]
    H --> I[lattice test --generate]
    I --> J[Update Tests]
    J --> K[lattice test]
    K --> L{Tests Pass?}
    L -->|No| M[Fix Code]
    M --> K
    L -->|Yes| N[lattice sheriff]
    N --> O{Sheriff Pass?}
    O -->|No| M
    O -->|Yes| P[Migration Script]
    P --> Q[Deploy]
```

## Data Flow Through Commands

### Schema to Production Flow

Complete data transformation from schema definition to running code.

```mermaid
graph LR
    A[lattice.yaml] --> B[lattice validate]
    B --> C{Valid Schema}
    C --> D[lattice compile]
    D --> E[models.py]
    D --> F[orm.py]
    D --> G[test_contracts.py]
    E --> H[Application Code]
    F --> I[Database Layer]
    G --> J[lattice test]
    J --> K{Tests Pass?}
    K -->|Yes| L[Production]
    K -->|No| M[Fix Code]
    M --> H
    M --> I
```

### Feedback Loop

How validation, testing, and enforcement create a quality feedback loop.

```mermaid
graph TD
    A[Write Code] --> B[lattice validate]
    B --> C{Schema Compliant?}
    C -->|No| D[Show Schema Errors]
    C -->|Yes| E[lattice sheriff]
    E --> F{Code Quality?}
    F -->|No| G[Show Quality Errors]
    F -->|Yes| H[lattice test]
    H --> I{Tests Pass?}
    I -->|No| J[Show Test Failures]
    I -->|Yes| K[Success]
    D --> A
    G --> A
    J --> A
```

## Error Handling Patterns

### Common Error Recovery Flows

How to recover from errors in different commands.

```mermaid
flowchart TD
    A[Command Error] --> B{Error Type?}
    
    B -->|Schema Invalid| C[lattice validate --verbose]
    C --> D[Fix lattice.yaml]
    D --> E[Retry Command]
    
    B -->|Env Issue| F[lattice doctor]
    F --> G[Install Dependencies]
    G --> H[Set Env Vars]
    H --> E
    
    B -->|Code Quality| I[lattice sheriff --fix]
    I --> J{Auto-Fixed?}
    J -->|No| K[Manual Fixes]
    J -->|Yes| E
    K --> E
    
    B -->|Test Failure| L[lattice test --verbose]
    L --> M[Debug Tests]
    M --> N[Fix Code]
    N --> E
    
    B -->|Pipeline Failed| O[lattice chain resume]
    O --> P{Resumed?}
    P -->|Yes| Q[Complete]
    P -->|No| R[Check Logs]
    R --> S[Fix Issues]
    S --> O
```

## End-to-End: From Idea to Production

Comprehensive example showing all commands in a complete workflow.

```mermaid
flowchart TD
    START([Idea: Build User Service]) --> A[lattice init user_service --type service]
    A --> B[lattice doctor]
    B --> C{Env OK?}
    C -->|No| D[Fix Environment]
    D --> B
    C -->|Yes| E[Edit lattice.yaml]
    E --> F[Define User entity]
    F --> G[lattice validate]
    G --> H{Valid?}
    H -->|No| E
    H -->|Yes| I[lattice compile --pydantic --sqlmodel]
    I --> J[Models generated]
    J --> K[lattice ask 'Implement user auth']
    K --> L[Write application code]
    L --> M[lattice sheriff]
    M --> N{Quality OK?}
    N -->|No| L
    N -->|Yes| O[lattice test --generate]
    O --> P[lattice test --coverage]
    P --> Q{Tests pass?}
    Q -->|No| L
    Q -->|Yes| R[Git commit]
    R --> S[CI: lattice validate]
    S --> T[CI: lattice sheriff --format github]
    T --> U[CI: lattice test --format junit]
    U --> V{CI pass?}
    V -->|No| W[Fix issues]
    W --> L
    V -->|Yes| X[lattice mcp --transport sse]
    X --> Y[Deploy to staging]
    Y --> Z[Deploy to production]
    Z --> AA[lattice feedback]
    AA --> END([Production Running])
```

## Developer Journey: Command Flow

The typical decision flow a developer follows when using Lattice Lock commands.

```mermaid
flowchart TD
    START([Start New Project]) --> INIT[lattice init]
    INIT --> DOCTOR{lattice doctor<br/>Environment OK?}
    DOCTOR -->|No| FIX_ENV[Fix Environment]
    FIX_ENV --> DOCTOR
    DOCTOR -->|Yes| EDIT_SCHEMA[Edit lattice.yaml]
    
    EDIT_SCHEMA --> VALIDATE{lattice validate<br/>Schema Valid?}
    VALIDATE -->|No| EDIT_SCHEMA
    VALIDATE -->|Yes| COMPILE[lattice compile]
    
    COMPILE --> WRITE_CODE[Write Application Code]
    WRITE_CODE --> SHERIFF{lattice sheriff<br/>Quality OK?}
    SHERIFF -->|No| WRITE_CODE
    SHERIFF -->|Yes| TEST_GEN[lattice test --generate]
    
    TEST_GEN --> TEST_RUN{lattice test<br/>Tests Pass?}
    TEST_RUN -->|No| WRITE_CODE
    TEST_RUN -->|Yes| COMMIT[Git Commit]
    
    COMMIT --> CI_START[CI Pipeline Triggered]
    CI_START --> CI_DOCTOR[CI: lattice doctor]
    CI_DOCTOR --> CI_VALIDATE[CI: lattice validate]
    CI_VALIDATE --> CI_SHERIFF[CI: lattice sheriff]
    CI_SHERIFF --> CI_TEST[CI: lattice test]
    
    CI_TEST --> CI_PASS{All Checks Pass?}
    CI_PASS -->|No| WRITE_CODE
    CI_PASS -->|Yes| DEPLOY[Deploy to Production]
    
    DEPLOY --> MONITOR[Monitor & Feedback]
    MONITOR --> FEEDBACK[lattice feedback]
    FEEDBACK --> CONTINUE{Continue Development?}
    CONTINUE -->|Yes| EDIT_SCHEMA
    CONTINUE -->|No| END([Project Complete])
    
    style START fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
    style END fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
    style DEPLOY fill:#ff9800,stroke:#e65100,stroke-width:2px,color:#fff
    style DOCTOR fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    style VALIDATE fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    style SHERIFF fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    style TEST_RUN fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    style CI_PASS fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
```
