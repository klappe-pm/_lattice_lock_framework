# Core Architecture - Comprehensive Diagram Documentation

Detailed Mermaid.js diagrams documenting the core system architecture including C4 diagrams, package structure, deployment topology, database schema, and state management.

---

## Table of Contents

1. [System Context (C4 Level 1)](#1-system-context-c4-level-1)
2. [Container Architecture (C4 Level 2)](#2-container-architecture-c4-level-2)
3. [Package Structure](#3-package-structure)
4. [Deployment Topology](#4-deployment-topology)
5. [Database Entity Relationship](#5-database-entity-relationship)
6. [Rollback State Machine](#6-rollback-state-machine)
7. [Migration Strategy Flow](#7-migration-strategy-flow)

---

## 1. System Context (C4 Level 1)

**Purpose**: High-level view showing the Lattice Lock Framework boundary, its users, and external systems it interacts with.

**Diagram Type**: C4 Context Diagram

```mermaid
C4Context
    title System Context Diagram for Lattice Lock Framework

    Person(user, "Developer", "Software engineer building AI-powered applications")
    Person(admin, "Platform Admin", "Manages governance policies and rules")

    System_Boundary(llf_boundary, "Lattice Lock Framework") {
        System(llf, "Lattice Lock Framework", "Governance-first AI development framework with intelligent model orchestration")
    }

    System_Ext(ide, "IDE / Editor", "VS Code, Cursor, JetBrains IDEs")
    System_Ext(ci, "CI/CD Pipeline", "GitHub Actions, GitLab CI, Jenkins")
    System_Ext(llm_providers, "LLM Providers", "OpenAI, Anthropic, Google, Azure, xAI, Ollama")
    System_Ext(db, "Persistence Layer", "PostgreSQL, SQLite, Vector DB")

    Rel(user, llf, "Uses CLI, configures projects")
    Rel(user, ide, "Writes code")
    Rel(ide, llf, "Validates via LSP/Extension")
    Rel(admin, llf, "Defines governance rules")

    Rel(ci, llf, "Runs Sheriff & Gauntlet checks")

    Rel(llf, llm_providers, "Routes prompts & orchestrates models")
    Rel(llf, db, "Stores state, logs, cost metrics")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Element Descriptions

| Element | Type | Description |
|---------|------|-------------|
| **Developer** | Person | Primary user who builds AI applications using the framework |
| **Platform Admin** | Person | Configures governance policies and monitors compliance |
| **Lattice Lock Framework** | System | Core framework providing AI orchestration and governance |
| **IDE / Editor** | External System | Development environment with LSP integration |
| **CI/CD Pipeline** | External System | Automated validation in deployment pipelines |
| **LLM Providers** | External System | AI model providers (8 supported) |
| **Persistence Layer** | External System | Data storage for state, costs, and vectors |

### Key Relationships

| From | To | Interaction |
|------|-----|-------------|
| Developer | Framework | CLI commands, configuration files |
| IDE | Framework | Real-time validation via Language Server Protocol |
| Framework | LLM Providers | API calls for model inference |
| Framework | Database | Persist usage metrics and project state |

### Related Source Files

- [`src/cli/`](../../src/cli/) - CLI entry point
- [`src/orchestrator/`](../../src/orchestrator/) - Model orchestration
- [`src/admin/`](../../src/admin/) - Admin API and dashboard

---

## 2. Container Architecture (C4 Level 2)

**Purpose**: Shows the internal containers (deployable units) within the Lattice Lock Framework.

**Diagram Type**: C4 Container Diagram

```mermaid
C4Container
    title Container Diagram for Lattice Lock Framework

    Person(dev, "Developer", "Uses CLI to interact with framework")

    System_Boundary(llf, "Lattice Lock Framework") {
        Container(cli, "CLI", "Python/Click", "Primary entry point for all operations")

        Container(orchestrator, "Orchestrator", "Python Service", "Routes requests, manages context, handles failover")
        Container(sheriff, "Sheriff", "Python/AST", "Static analysis and governance enforcement")
        Container(gauntlet, "Gauntlet", "Python/Pytest", "Runtime validation and test generation")
        Container(admin_api, "Admin API", "FastAPI", "Backend for dashboard and management")
        Container(dashboard, "Dashboard", "React/Vite", "Web UI for monitoring and configuration")

        ContainerDb(db_sql, "Relational DB", "PostgreSQL/SQLite", "Users, projects, costs, errors")
        ContainerDb(db_vec, "Vector DB", "Chroma/PGVector", "Semantic index for RAG retrieval")
    }

    System_Ext(llm, "External Models", "OpenAI, Anthropic, Google, etc.")

    Rel(dev, cli, "Run commands")
    Rel(dev, dashboard, "View metrics")

    Rel(cli, orchestrator, "AI tasks")
    Rel(cli, sheriff, "Static analysis")
    Rel(cli, gauntlet, "Testing")

    Rel(orchestrator, llm, "API calls")
    Rel(orchestrator, db_sql, "Cost logging")

    Rel(admin_api, db_sql, "CRUD operations")
    Rel(dashboard, admin_api, "REST/WebSocket")

    Rel(gauntlet, orchestrator, "AI validation")
```

### Container Descriptions

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| **CLI** | Python/Click | Command parsing, user interaction |
| **Orchestrator** | Python | Model routing, failover, cost tracking |
| **Sheriff** | Python/AST | Static code analysis, governance checks |
| **Gauntlet** | Python/Pytest | Test generation and execution |
| **Admin API** | FastAPI | REST API, WebSocket, authentication |
| **Dashboard** | React/Vite | Real-time monitoring UI |
| **Relational DB** | PostgreSQL/SQLite | Structured data storage |
| **Vector DB** | Chroma/PGVector | Semantic search and retrieval |

### Related Source Files

- [`src/cli/`](../../src/cli/) - CLI container
- [`src/orchestrator/`](../../src/orchestrator/) - Orchestrator container
- [`src/sheriff/`](../../src/sheriff/) - Sheriff container
- [`src/gauntlet/`](../../src/gauntlet/) - Gauntlet container
- [`src/admin/`](../../src/admin/) - Admin API container
- [`frontend/`](../../frontend/) - Dashboard container
- [`src/database/`](../../src/database/) - Database abstraction

---

## 3. Package Structure

**Purpose**: Shows the Python package hierarchy and inter-module dependencies.

**Diagram Type**: UML Class Diagram (Package View)

```mermaid
classDiagram
    namespace src_lattice_lock {
        class CLI {
            +commands/
            +main.py
        }
        class Orchestrator {
            +core.py
            +providers/
            +routing/
            +scoring/
            +consensus/
        }
        class Sheriff {
            +sheriff.py
            +ast_visitor.py
            +rules.py
            +reports/
        }
        class Gauntlet {
            +generator.py
            +validator.py
            +runner.py
        }
        class Admin {
            +api.py
            +auth/
            +routes.py
        }
        class Config {
            +app_config.py
            +feature_flags.py
            +inheritance.py
        }
        class Database {
            +connection.py
            +repository.py
            +models/
        }
        class Utils {
            +async_compat.py
            +safe_path.py
        }
    }

    CLI ..> Orchestrator : delegates AI tasks
    CLI ..> Sheriff : triggers analysis
    CLI ..> Gauntlet : runs tests
    CLI ..> Admin : server commands

    Orchestrator ..> Config : reads settings
    Sheriff ..> Config : reads rules
    Gauntlet ..> Config : reads policies

    Admin ..> Database : persistence
    Orchestrator ..> Database : cost logging
```

### Package Descriptions

| Package | Purpose | Key Modules |
|---------|---------|-------------|
| **CLI** | User interface | `main.py`, command handlers |
| **Orchestrator** | AI routing | `core.py`, providers, scoring |
| **Sheriff** | Static analysis | `sheriff.py`, ast_visitor, rules |
| **Gauntlet** | Testing | generator, validator, runner |
| **Admin** | API layer | `api.py`, auth, routes |
| **Config** | Settings | app_config, feature_flags |
| **Database** | Persistence | connection, repository, models |
| **Utils** | Helpers | async_compat, safe_path |

### Dependency Flow

```
CLI (entry)
 ├── Orchestrator → LLM Providers
 ├── Sheriff → AST Analysis
 ├── Gauntlet → Test Execution
 └── Admin → Database → Storage
```

### Related Source Files

- [`src/lattice_lock/__init__.py`](../../src/lattice_lock/__init__.py) - Package root
- [`pyproject.toml`](../../pyproject.toml) - Package configuration

---

## 4. Deployment Topology

**Purpose**: Shows deployment environments from local development through CI/CD to production.

**Diagram Type**: Flowchart with Subgraphs

```mermaid
flowchart TD
    subgraph Local["Local Development"]
        DevMachine[Developer<br/>Workstation]
        CLI[Lattice CLI]
        LocalModels[Local LLM<br/>Ollama]

        DevMachine --> CLI
        CLI --> LocalModels
    end

    subgraph CICD["CI/CD Pipeline"]
        Runner[GitHub Actions<br/>Runner]
        SheriffCI[Sheriff<br/>Lint Check]
        GauntletCI[Gauntlet<br/>Test Check]

        Runner --> SheriffCI
        Runner --> GauntletCI
    end

    subgraph Production["Production Cloud"]
        CloudRun[Cloud Run<br/>or K8s]
        AdminAPI[Admin API]
        OrchService[Orchestrator<br/>Service]
        CloudDB[(Cloud SQL)]

        CloudRun --> AdminAPI
        CloudRun --> OrchService
        AdminAPI --> CloudDB
        OrchService --> CloudDB
    end

    Local -.->|Push Code| CICD
    CICD -.->|Deploy| Production

    style Local fill:#e8f5e9
    style CICD fill:#fff3e0
    style Production fill:#e3f2fd
```

### Environment Descriptions

| Environment | Components | Purpose |
|-------------|------------|---------|
| **Local Development** | CLI, Ollama | Developer workstation setup |
| **CI/CD Pipeline** | Sheriff, Gauntlet | Automated validation gates |
| **Production Cloud** | Admin API, Orchestrator, Cloud SQL | Deployed services |

### Deployment Configurations

| Component | Local | CI/CD | Production |
|-----------|-------|-------|------------|
| Database | SQLite | SQLite | Cloud SQL |
| LLM Provider | Ollama | Mock/OpenAI | Multi-provider |
| Auth | Disabled | Disabled | JWT |
| Scaling | Single | Parallel | Auto-scale |

### Related Source Files

- [`Dockerfile`](../../Dockerfile) - Container definition
- [`docker-compose.yml`](../../docker-compose.yml) - Local multi-container
- [`.github/workflows/`](../../.github/workflows/) - CI/CD workflows
- [`infrastructure/`](../../infrastructure/) - Cloud deployment configs

---

## 5. Database Entity Relationship

**Purpose**: Shows the core database schema with entities and relationships.

**Diagram Type**: Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Project : owns
    User {
        uuid id PK
        string email UK
        string password_hash
        string role
        timestamp created_at
        timestamp updated_at
    }

    Project ||--o{ CostRecord : generates
    Project ||--o{ ProjectError : has
    Project ||--o{ Checkpoint : has
    Project {
        string id PK
        uuid user_id FK
        string name
        string status
        json config
        int health_score
        timestamp created_at
    }

    CostRecord {
        uuid id PK
        string project_id FK
        string model_id
        int prompt_tokens
        int completion_tokens
        float cost_usd
        string task_type
        timestamp timestamp
    }

    ProjectError {
        uuid id PK
        string project_id FK
        string severity
        string error_code
        string message
        json stack_trace
        timestamp created_at
    }

    Checkpoint {
        uuid id PK
        string project_id FK
        json files
        json config
        string schema_version
        string description
        timestamp created_at
    }
```

### Entity Descriptions

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **User** | Platform users | email, role, password_hash |
| **Project** | Registered projects | name, status, health_score |
| **CostRecord** | Usage tracking | model_id, tokens, cost_usd |
| **ProjectError** | Error history | severity, error_code, message |
| **Checkpoint** | Rollback state | files, config, schema_version |

### Relationships

| Relationship | Cardinality | Description |
|--------------|-------------|-------------|
| User → Project | 1:N | Users own multiple projects |
| Project → CostRecord | 1:N | Projects generate many cost records |
| Project → ProjectError | 1:N | Projects track error history |
| Project → Checkpoint | 1:N | Projects have rollback checkpoints |

### Related Source Files

- [`src/database/models/`](../../src/database/models/) - SQLAlchemy models
- [`src/database/repository.py`](../../src/database/repository.py) - Repository pattern
- [`src/admin/db.py`](../../src/admin/db.py) - Database session management

---

## 6. Rollback State Machine

**Purpose**: Shows system states and transitions for error handling and rollback.

**Diagram Type**: State Diagram

```mermaid
stateDiagram-v2
    [*] --> Healthy: System Start

    Healthy --> Warning: Minor Error < Threshold
    Healthy --> Error: Critical Failure

    Warning --> Healthy: Auto-Recovery
    Warning --> Error: Errors Escalate

    state Error {
        [*] --> AssessDamage
        AssessDamage --> TriggerRollback: Damage > Limit
        AssessDamage --> ManualIntervention: Damage < Limit

        TriggerRollback --> Restoring: Load Checkpoint
        Restoring --> VerifyRestore: Apply State

        VerifyRestore --> Healthy: Validation Pass
        VerifyRestore --> Broken: Validation Fail
    }

    ManualIntervention --> Healthy: Admin Fix
    Broken --> [*]: Terminal State
```

### State Descriptions

| State | Description | Triggers |
|-------|-------------|----------|
| **Healthy** | Normal operation | Successful operations |
| **Warning** | Minor issues detected | Error rate below threshold |
| **Error** | Significant failure | Critical errors, cascading failures |
| **AssessDamage** | Evaluate impact | Entry to Error state |
| **TriggerRollback** | Initiate recovery | Damage exceeds limit |
| **Restoring** | Apply checkpoint | Rollback in progress |
| **VerifyRestore** | Validate recovery | Post-restore checks |
| **Broken** | Unrecoverable | Failed validation |
| **ManualIntervention** | Human required | Damage below auto-fix threshold |

### Transition Thresholds

| Transition | Threshold | Action |
|------------|-----------|--------|
| Healthy → Warning | Error rate > 1% | Log warning, monitor |
| Warning → Error | Error rate > 10% | Initiate damage assessment |
| AssessDamage → Rollback | Affected files > 5 | Auto-rollback |
| AssessDamage → Manual | Affected files ≤ 5 | Alert admin |

### Related Source Files

- [`src/rollback/checkpoint.py`](../../src/rollback/checkpoint.py) - CheckpointManager
- [`src/rollback/state.py`](../../src/rollback/state.py) - RollbackState
- [`src/rollback/storage.py`](../../src/rollback/storage.py) - CheckpointStorage
- [`src/rollback/trigger.py`](../../src/rollback/trigger.py) - Rollback triggers

---

## 7. Migration Strategy Flow

**Purpose**: Documents the database migration process with backup and rollback.

**Diagram Type**: Flowchart

```mermaid
flowchart TD
    Start([Start Migration]) --> CheckVer{Check DB<br/>Version}

    CheckVer --> |Current == Target| Done([Already<br/>Up to Date])
    CheckVer --> |Current < Target| Plan[Identify<br/>Migration Path]

    Plan --> Backup[Create Backup<br/>Checkpoint]

    Backup --> Apply[Apply Next<br/>Migration]

    Apply --> Success{Migration<br/>Success?}

    Success -- Yes --> UpdateVer[Update Version<br/>Record]
    UpdateVer --> MoreMigrations{More<br/>Migrations?}

    MoreMigrations -- Yes --> Apply
    MoreMigrations -- No --> Complete([Migration<br/>Complete])

    Success -- No --> Rollback[Restore<br/>from Backup]
    Rollback --> Fail([Migration<br/>Failed])

    style Start fill:#e8f5e9
    style Done fill:#e8f5e9
    style Complete fill:#e8f5e9
    style Fail fill:#ffebee
```

### Node Descriptions

| Node | Description | Action |
|------|-------------|--------|
| **Check DB Version** | Compare current vs target | Query version table |
| **Identify Migration Path** | List required migrations | Parse migration files |
| **Create Backup** | Save current state | Checkpoint creation |
| **Apply Migration** | Execute migration script | Run SQL/Alembic |
| **Update Version** | Record new version | Insert version record |
| **Restore Backup** | Revert on failure | Apply checkpoint |

### Migration Best Practices

1. **Always backup** before applying migrations
2. **Test in staging** before production
3. **Use transactions** for atomicity
4. **Version everything** in migration files
5. **Plan rollback** for every migration

### Related Source Files

- [`src/database/migrations/`](../../src/database/migrations/) - Alembic migrations
- [`src/rollback/checkpoint.py`](../../src/rollback/checkpoint.py) - Backup mechanism

---

## Summary

| Diagram | Type | Purpose | C4 Level |
|---------|------|---------|----------|
| System Context | C4 Context | External boundaries | Level 1 |
| Container Architecture | C4 Container | Internal components | Level 2 |
| Package Structure | Class | Code organization | N/A |
| Deployment Topology | Flowchart | Environment mapping | N/A |
| Database ERD | ER Diagram | Data model | N/A |
| Rollback State Machine | State | Error recovery | N/A |
| Migration Flow | Flowchart | DB updates | N/A |

---

## Usage

These diagrams render in GitHub, GitLab, VS Code (Mermaid extension), Obsidian, and [mermaid.live](https://mermaid.live).

Note: C4 diagrams require Mermaid v9.2+ for full C4 syntax support.
