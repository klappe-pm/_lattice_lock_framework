---
title: validate
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-validate-001]
tags: [cli, validate, validation, governance]
---

# cmd_validate

## lattice validate

Runs comprehensive validators on a Lattice Lock project to ensure compliance with governance rules and best practices. Performs schema validation, environment file checks, agent manifest validation, and repository structure verification. Can automatically fix common issues like trailing whitespace and missing EOF newlines.

```bash
lattice validate [OPTIONS]
```

**Basic Examples:**

```bash
# Validate entire project
lattice validate
```

```bash
# Validate specific path
lattice validate --path /path/to/project
```

```bash
# Validate current directory explicitly
lattice validate --path .
```

#### --path, -p

Path to project directory (default: current directory).

```bash
# Validate specific project
lattice validate --path /path/to/project
```

```bash
# Validate parent directory
lattice validate --path ../other_project
```

```bash
# Validate with absolute path
lattice validate -p /Users/me/projects/my_app
```

#### --fix

Auto-fix issues where possible (trailing whitespace, missing EOF newline).

```bash
# Apply auto-fixes
lattice validate --fix
```

```bash
# Fix and validate
lattice validate --path /path/to/project --fix
```

```bash
# Fix with verbose output
lattice validate --fix --verbose
```

#### --schema-only

Run only schema validation (lattice.yaml).

```bash
# Validate only schema
lattice validate --schema-only
```

```bash
# Schema validation for specific path
lattice validate --path /path/to/project --schema-only
```

```bash
# Quick schema check
lattice validate --schema-only --path .
```

#### --env-only

Run only environment file validation (.env).

```bash
# Validate only environment files
lattice validate --env-only
```

```bash
# Check env in specific project
lattice validate --path /path/to/project --env-only
```

```bash
# Env validation with fixes
lattice validate --env-only --fix
```

#### --agents-only

Run only agent manifest validation.

```bash
# Validate only agent manifests
lattice validate --agents-only
```

```bash
# Agent validation for specific path
lattice validate --path /path/to/agents --agents-only
```

```bash
# Quick agent check
lattice validate --agents-only --verbose
```

#### --structure-only

Run only repository structure validation.

```bash
# Validate only repository structure
lattice validate --structure-only
```

```bash
# Structure check for project
lattice validate --path /path/to/project --structure-only
```

```bash
# Verify folder organization
lattice validate --structure-only --verbose
```

#### --verbose

Verbose output with detailed warnings.

```bash
# Show detailed validation output
lattice validate --verbose
```

```bash
# Verbose with specific path
lattice validate --path . --verbose
```

```bash
# Detailed fix output
lattice validate --fix --verbose
```

**Use Cases:**
- Pre-commit validation before version control
- CI/CD pipeline integration
- Schema compliance verification
- Code quality checks
- Automated formatting fixes

### Process Flow Diagrams: lattice validate

#### Decision Flow: Validation Pipeline
This diagram shows the validation workflow including optional auto-fix mode and selective validator execution. Use this to understand how validation runs are configured and results are collected.

```mermaid
graph TD
    A[Start Validation] --> B{Fix Mode?}
    B -->|Yes| C[Apply Auto-Fixes]
    B -->|No| D[Determine Validators]
    C --> D
    D --> E{Run All?}
    E -->|Yes| F[Schema Validation]
    E -->|No| G[Selective Validation]
    F --> H[Environment Validation]
    H --> I[Agent Validation]
    I --> J[Structure Validation]
    G --> K[Run Selected]
    J --> L[Collect Results]
    K --> L
    L --> M{Any Errors?}
    M -->|Yes| N[Display Errors]
    M -->|No| O[Display Success]
    N --> P[Exit Code 1]
    O --> Q[Exit Code 0]
```

#### Sequence Flow: Validator Execution Order
This sequence diagram shows how validators are executed in order after optional auto-fixing. Follow this to see the interaction between different validation components.

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as Validate Command
    participant Fixer as Auto-Fixer
    participant SV as Schema Validator
    participant EV as Env Validator
    participant AV as Agent Validator
    participant RV as Structure Validator

    U->>CLI: lattice validate --fix
    CLI->>Fixer: Apply fixes
    Fixer->>Fixer: Fix whitespace
    Fixer->>Fixer: Fix EOF newlines
    Fixer-->>CLI: Fixes applied
    CLI->>SV: Validate schema
    SV-->>CLI: Results
    CLI->>EV: Validate .env
    EV-->>CLI: Results
    CLI->>AV: Validate agents
    AV-->>CLI: Results
    CLI->>RV: Validate structure
    RV-->>CLI: Results
    CLI->>CLI: Aggregate results
    CLI-->>U: Display summary
```

#### Data Flow: Multi-Validator Processing
This data flow diagram illustrates how validation results from multiple validators are aggregated. Use this to understand the parallel nature of different validation checks.

```mermaid
graph LR
    A[Project Path] --> B[Auto-Fix Phase]
    B --> C[Schema Check]
    B --> D[Env Check]
    B --> E[Agent Check]
    B --> F[Structure Check]
    C --> G[Results]
    D --> G
    E --> G
    F --> G
    G --> H{All Pass?}
    H -->|Yes| I[Success]
    H -->|No| J[Show Errors]
```

#### Detailed Flowchart: Selective Validation Logic
This flowchart details the logic for selecting which validators to run based on command flags. Reference this when using specific validation modes (schema-only, env-only, etc.).

```mermaid
flowchart TD
    Start([lattice validate]) --> ParsePath[Parse Path]
    ParsePath --> CheckFix{Fix Flag?}
    CheckFix -->|Yes| ApplyFixes[Apply Fixes]
    CheckFix -->|No| SelectValidators
    ApplyFixes --> SelectValidators[Select Validators]
    SelectValidators --> SchemaCheck{Schema Only?}
    SchemaCheck -->|Yes| RunSchema[Run Schema]
    SchemaCheck -->|No| EnvCheck{Env Only?}
    EnvCheck -->|Yes| RunEnv[Run Env]
    EnvCheck -->|No| AgentCheck{Agent Only?}
    AgentCheck -->|Yes| RunAgent[Run Agent]
    AgentCheck -->|No| StructCheck{Structure Only?}
    StructCheck -->|Yes| RunStruct[Run Structure]
    StructCheck -->|No| RunAll[Run All Validators]
    RunSchema --> Collect[Collect Results]
    RunEnv --> Collect
    RunAgent --> Collect
    RunStruct --> Collect
    RunAll --> Collect
    Collect --> Display[Display Results]
    Display --> ExitCode{Has Errors?}
    ExitCode -->|Yes| Fail([Exit 1])
    ExitCode -->|No| Success([Exit 0])
```

#### State Diagram: Validation Lifecycle
This state diagram shows the progression through validation states from initialization to completion. Use this to identify at which stage validation errors or warnings occur.

```mermaid
stateDiagram-v2
    [*] --> Initialized: Start
    Initialized --> Fixing: Fix Mode
    Initialized --> Validating: No Fix
    Fixing --> Validating: Fixes Applied
    Validating --> SchemaCheck: Validating
    SchemaCheck --> EnvCheck
    EnvCheck --> AgentCheck
    AgentCheck --> StructureCheck
    StructureCheck --> Aggregating: Complete
    Aggregating --> Passed: No Errors
    Aggregating --> Failed: Has Errors
    Passed --> [*]
    Failed --> [*]
```
