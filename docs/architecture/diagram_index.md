# Lattice Lock Framework - Diagram Documentation Index

Comprehensive index of all Mermaid.js architecture diagrams organized by domain. Each diagram includes detailed node descriptions, related source file links, and integration context.

---

## Quick Navigation

| Domain | Document | Diagrams | Focus Area |
|--------|----------|----------|------------|
| [Core Architecture](#core-architecture) | [CORE_ARCHITECTURE_DIAGRAMS.md](core_architecture_diagrams.md) | 7 | System structure, deployment, data |
| [Orchestrator](#orchestrator) | [ORCHESTRATOR_DIAGRAMS.md](model_orchestrator_diagrams.md) | 9 | Model routing, consensus, chains |
| [Governance](#governance) | [GOVERNANCE_DIAGRAMS.md](governance_system_diagrams.md) | 5 | Sheriff, Gauntlet, Compiler |
| [Admin](#admin) | [ADMIN_DIAGRAMS.md](admin_system_diagrams.md) | 3 | Authentication, telemetry, dashboard |
| [Agents](#agents) | [AGENT_DIAGRAMS.md](agent_system_diagrams.md) | 6 | Lifecycle, communication, memory |
| [Workflows](#workflows) | [WORKFLOW_DIAGRAMS.md](workflow_diagrams.md) | 6 | CLI, IDE, validation flows |
| [Sequences](#sequences) | [SEQUENCE_DIAGRAMS.md](docs/architecture/sequence_diagrams.md) | 10 | Detailed interaction sequences |

**Total: 46 documented diagrams**

---

## Core Architecture

📄 **Document**: [CORE_ARCHITECTURE_DIAGRAMS.md](core_architecture_diagrams.md)

High-level system architecture using C4 model, package structure, deployment topology, and data models.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | System Context (C4 Level 1) | C4 Context | External actors and system boundaries |
| 2 | Container Architecture (C4 Level 2) | C4 Container | Major containers and their relationships |
| 3 | Package Structure | Flowchart | Python package organization |
| 4 | Deployment Topology | Flowchart | Infrastructure and deployment targets |
| 5 | Database Entity Relationship | ERD | Data model relationships |
| 6 | Rollback State Machine | State | Checkpoint and rollback states |
| 7 | Migration Strategy Flow | Flowchart | Database migration process |

### Key Source Files
- `src/` - Core package structure
- `src/rollback/checkpoint.py` - Checkpoint management
- `src/database/` - Database models and migrations

---

## Orchestrator

📄 **Document**: [ORCHESTRATOR_DIAGRAMS.md](model_orchestrator_diagrams.md)

Model orchestration, routing, consensus, and chain execution flows.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | Request Routing Sequence | Sequence | End-to-end request flow |
| 2 | Class Architecture | Class | Core class relationships |
| 3 | Model Selection Logic | Flowchart | Provider selection algorithm |
| 4 | Provider Fallback Strategy | Flowchart | Fallback chain execution |
| 5 | Consensus Engine Voting | Sequence | Multi-model agreement |
| 6 | Request Routing Pipeline | Flowchart | Pipeline stages |
| 7 | Chain Execution Flow | Flowchart | Sequential chain processing |
| 8 | Context Window Management | Flowchart | Token tracking and limits |
| 9 | Cost Tracking Data Flow | Flowchart | Usage and billing flow |

### Key Source Files
- `src/orchestrator/core.py` - ModelOrchestrator class
- `src/orchestrator/router.py` - Request routing
- `src/consensus/engine.py` - Consensus voting
- `src/orchestrator/chains.py` - Chain execution

---

## Governance

📄 **Document**: [GOVERNANCE_DIAGRAMS.md](governance_system_diagrams.md)

Static analysis (Sheriff), runtime testing (Gauntlet), and configuration compilation.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | Sheriff AST Analysis Pipeline | Flowchart | Code parsing and analysis |
| 2 | Sheriff Rule Evaluation Flow | Sequence | Dynamic rule checking |
| 3 | Gauntlet Test Generation | Flowchart | Test code generation |
| 4 | Gauntlet Execution Loop | State | Test lifecycle and retry |
| 5 | Compiler Processing Pipeline | Flowchart | YAML to JSON compilation |

### Key Source Files
- `src/sheriff/sheriff.py` - Static analysis engine
- `src/sheriff/ast_visitor.py` - AST traversal
- `src/gauntlet/generator.py` - Test generation
- `src/gauntlet/runner.py` - Test execution
- `src/compiler/core.py` - Configuration compiler

---

## Admin

📄 **Document**: [ADMIN_DIAGRAMS.md](admin_system_diagrams.md)

Administration system including authentication, observability, and dashboard architecture.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | Authentication Flow | Sequence | JWT login and validation |
| 2 | Telemetry Pipeline | Flowchart | OTEL metrics/traces/logs |
| 3 | Admin Dashboard Architecture | C4 Container | Frontend/backend structure |

### Key Source Files
- `src/admin/api.py` - FastAPI application
- `src/admin/auth/service.py` - JWT authentication
- `src/admin/telemetry/` - Observability
- `src/dashboard/` - Dashboard components

---

## Agents

📄 **Document**: [AGENT_DIAGRAMS.md](agent_system_diagrams.md)

AI agent system including lifecycle, communication, memory, and specialized workflows.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | Agent Lifecycle | State | Execution states and transitions |
| 2 | Inter-Agent Communication | Sequence | Multi-agent collaboration |
| 3 | Handoff Protocol | Sequence | Task transfer with checkpoints |
| 4 | Memory Retrieval Flow | Flowchart | RAG pipeline for context |
| 5 | Product Agent Workflow | Flowchart | PRD creation process |
| 6 | Engineering Agent Workflow | Flowchart | Development with quality gates |

### Key Source Files
- `src/agents/base.py` - Base agent class
- `src/agents/memory/` - Memory subsystem
- `src/agents/handoff/` - Handoff protocol
- `src/agents/product/` - Product agent
- `src/agents/engineering/` - Engineering agent

---

## Workflows

📄 **Document**: [WORKFLOW_DIAGRAMS.md](workflow_diagrams.md)

User-facing workflows including CLI, IDE integration, and validation processes.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | CLI Command Hierarchy | Mind Map | Complete command structure |
| 2 | IDE Integration Flow | Sequence | LSP communication |
| 3 | Project Initialization Flow | Flowchart | `lattice init` process |
| 4 | High-Level User Flow | Flowchart | End-to-end development journey |
| 5 | Governance Validation Flow | Sequence | Three-step validation |
| 6 | Configuration Inheritance Flow | Graph | Config merging priority |

### Key Source Files
- `src/cli/` - CLI commands
- `src/lsp/` - Language server
- `src/config/` - Configuration loading
- `src/validator/` - Schema validation

---

## Sequences

📄 **Document**: [SEQUENCE_DIAGRAMS.md](docs/architecture/sequence_diagrams.md)

Detailed interaction sequences for complex system behaviors.

| # | Diagram | Type | Purpose |
|---|---------|------|---------|
| 1 | Model Orchestrator - Request Routing | Sequence | Provider routing flow |
| 2 | Model Orchestrator - Fallback Chain | Sequence | Error recovery cascade |
| 3 | Admin API - JWT Authentication | Sequence | Token lifecycle |
| 4 | Admin API - Token Refresh | Sequence | Token renewal |
| 5 | Sheriff - File Validation | Sequence | AST analysis pipeline |
| 6 | Dashboard - WebSocket Lifecycle | Sequence | Real-time connection |
| 7 | Prompt Architect - 4-Stage Pipeline | Sequence | Agent orchestration |
| 8 | Checkpoint - State Management | Sequence | Checkpoint operations |
| 9 | Rollback - Recovery Flow | Sequence | State restoration |
| 10 | Error Handling - Retry with Backoff | Sequence | Error recovery |

### Key Source Files
- `src/orchestrator/core.py` - Request routing
- `src/admin/auth/service.py` - Authentication
- `src/sheriff/sheriff.py` - Static analysis
- `src/dashboard/websocket.py` - WebSocket manager
- `src/agents/prompt_architect/orchestrator.py` - Pipeline
- `src/rollback/checkpoint.py` - Checkpoints
- `src/errors/middleware.py` - Error handling

---

## Diagram Types Reference

| Type | Mermaid Syntax | Use Case |
|------|----------------|----------|
| **Sequence** | `sequenceDiagram` | Temporal interactions between components |
| **Flowchart** | `flowchart TD/LR` | Process flows and decision trees |
| **State** | `stateDiagram-v2` | State machines and transitions |
| **Class** | `classDiagram` | Object relationships and hierarchies |
| **C4 Context** | `C4Context` | System boundaries and external actors |
| **C4 Container** | `C4Container` | Major deployable units |
| **ERD** | `erDiagram` | Database entity relationships |
| **Mind Map** | `mindmap` | Hierarchical concept organization |
| **Graph** | `graph TD/LR` | General node relationships |

---

## Source Diagram Files

All original diagram files are located in `docs/assets/diagrams/`:

```
docs/assets/diagrams/
├── admin/
│   ├── admin_dashboard_architecture.md
│   ├── authentication_flow.md
│   └── telemetry_pipeline.md
├── agents/
│   ├── agent_lifecycle.md
│   ├── engineering_agent_workflow.md
│   ├── handoff_protocol.md
│   ├── inter_agent_communication.md
│   ├── memory_retrieval_flow.md
│   └── product_agent_workflow.md
├── core/
│   ├── container_architecture.md
│   ├── database_erd.md
│   ├── deployment_topology.md
│   ├── migration_strategy_flow.md
│   ├── package_structure.md
│   ├── rollback_state_machine.md
│   └── system_context.md
├── governance/
│   ├── compiler_logic.md
│   ├── gauntlet_execution_loop.md
│   ├── gauntlet_test_generation.md
│   ├── sheriff_ast_analysis.md
│   └── sheriff_rule_evaluation.md
├── orchestrator/
│   ├── chain_execution_flow.md
│   ├── consensus_engine_voting.md
│   ├── context_window_management.md
│   ├── cost_tracking_data_flow.md
│   ├── model_selection_logic.md
│   ├── orchestrator_classes.md
│   ├── orchestrator_sequence.md
│   ├── provider_fallback_strategy.md
│   └── request_routing_pipeline.md
└── workflows/
    ├── cli_command_hierarchy.md
    ├── configuration_inheritance_flow.md
    ├── governance_validation_flow.md
    ├── high_level_user_flow.md
    ├── ide_integration_flow.md
    └── project_initialization_flow.md
```

---

## Rendering

These diagrams render in:
- **GitHub** - Native Mermaid support in markdown
- **GitLab** - Native Mermaid support
- **VS Code** - With Mermaid extension
- **Obsidian** - Native Mermaid support
- **mermaid.live** - Online editor and viewer

---

## Contributing

When adding new diagrams:

1. Create the diagram in the appropriate `docs/assets/diagrams/` subdirectory
2. Update the corresponding `*_DIAGRAMS.md` documentation file with:
   - Diagram purpose and type
   - Node descriptions table
   - Related source files with line references
3. Update this index with the new diagram entry
4. Ensure the diagram renders correctly in mermaid.live before committing
