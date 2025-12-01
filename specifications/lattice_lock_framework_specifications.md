# lattice_lock_framework_specifications

**Version:** 1.0.0  
**Last Updated:** 2025-11-30  
**Author:** Kevin Lappe

---

## Overview and Positioning

### What is Lattice-Lock?

Lattice-Lock is a **governance-first framework for AI-assisted software development**. It provides deterministic, policy-enforced code generation and agent orchestration by combining three integrated layers:

1. **Governance Core** - Schema-driven code generation with compile-time enforcement
2. **Model Orchestrator** - Intelligent routing of AI tasks across multiple providers
3. **Engineering Framework** - Standardized tooling for repo scaffolding, CI/CD, and validation

The framework transforms code generation from probabilistic synthesis into **constrained assembly**, guaranteeing structural compliance and semantic correctness through pre-compilation enforcement.

### Document Scope

This specification is the **authoritative reference** for the Lattice-Lock system. It guides all design and implementation decisions across the three layers. Previous documentation (WARP.md, context docs, standalone PRDs) should be considered superseded by this specification for architectural decisions.

### Target Audience

- Internal engineers building AI-powered applications
- DevOps/Platform teams integrating agent workflows into CI/CD
- Orchestration administrators managing multi-agent systems
- LLM agent developers creating new agent definitions

### Implementation Status

| Layer | Status | Location |
|-------|--------|----------|
| Governance Core | Specified | This specification (Section 3.1) |
| Model Orchestrator | **Implemented** | `src/lattice_lock_orchestrator/core.py`, `registry.py`, `scorer.py` |
| Engineering Framework | Planned | This specification (Section 3.3) |

---

## Layered Architecture

### Architecture Diagram
```
┌────────────────────────────────────────────────────────────────────┐
│                    ENGINEERING FRAMEWORK                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Scaffolding │  │   CI/CD     │  │ Validation  │  │   Admin    │ │
│  │    CLI      │  │   Hooks     │  │   Engine    │  │    API     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
          │                │                │               │
          ▼                ▼                ▼               ▼
┌────────────────────────────────────────────────────────────────────┐
│                     MODEL ORCHESTRATOR                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │    Task     │  │   Model     │  │   Cost      │  │  Provider  │ │
│  │  Analyzer   │  │   Scorer    │  │  Tracker    │  │  Clients   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
          │                │                │               │
          ▼                ▼                ▼               ▼
┌────────────────────────────────────────────────────────────────────┐
│                     GOVERNANCE CORE                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Lattice   │  │  Polyglot   │  │   Sheriff   │  │    The     │ │
│  │   Schema    │  │  Compiler   │  │    (AST)    │  │  Gauntlet  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Governance Core
**Purpose:** Eliminate interface drift, style divergence, and semantic drift through schema-first code generation.

- Defines the single source of truth (`lattice.yaml`)
- Compiles schemas into typed artifacts (Pydantic models, ORM, migrations, tests)
- Enforces structural compliance via AST analysis (Sheriff)
- Validates semantic correctness via auto-generated tests (Gauntlet)

**Key Guarantee:** 100% structural compliance, >99% semantic compliance

#### Model Orchestrator
**Purpose:** Intelligently route AI tasks across providers with cost optimization.

- Analyzes task requirements and selects optimal models
- Manages 63 models across 8 providers (Local, OpenAI, Anthropic, Google, xAI, Azure, Bedrock, DIAL)
- Tracks costs and performance metrics
- Provides fallback chains and consensus mechanisms

**Key Guarantee:** Local-first strategy, automatic fallback, cost-aware routing

#### Engineering Framework
**Purpose:** Standardize project setup, CI/CD integration, and operational workflows.

- Scaffolds compliant repository structures
- Integrates validation into AWS/GCP pipelines
- Provides error boundaries and rollback mechanisms
- Offers admin visibility into agent status and health

**Key Guarantee:** <30 minutes to first successful CI validation

### Layer Contracts

| Provider Layer | Consumer Layer | Contract |
|----------------|----------------|----------|
| Governance Core | Model Orchestrator | Generated types module, validation rules, forbidden imports list |
| Governance Core | Engineering Framework | Sheriff CLI, Gauntlet test suite, schema validation |
| Model Orchestrator | Engineering Framework | `ModelOrchestrator` class, CLI interface, cost/performance APIs |
| Engineering Framework | End Users | Scaffolding CLI, CI templates, admin API endpoints |

---

## Component Specifications

### 3.1 Governance Core Specification

#### 3.1.1 Lattice Schema (`lattice.yaml`)

The lattice schema is the **Single Source of Truth** for all type definitions, interfaces, and constraints.

**Required Sections:**

```yaml
version: v2.1                    # Schema version (semantic versioning)
generated_module: types_v2       # Output module name

config:
  forbidden_imports:             # Libraries agents MUST NOT use
    - requests
    - psycopg2
    - sqlite3
    - float                      # Use Decimal for money
  orm_engine: sqlmodel           # ORM backend

entities:                        # Domain model definitions
  EntityName:
    description: "..."
    persistence: table           # Database backing (optional)
    fields:
      field_name: { type: uuid, primary_key: true }
      price: { type: decimal, gt: 0, scale: 8 }
      status: { enum: [pending, filled, cancelled], default: pending }

interfaces:                      # Service contracts
  IServiceName:
    file: src/services/service.py
    scaffold: repository_pattern
    depends_on: []
    methods:
      method_name:
        params:
          param: EntityType
        returns: ResultType
        ensures:                 # Semantic post-conditions
          - "result.value > 0"
```

**Invariants:**
- MUST use semantic versioning for schema versions
- MUST define all entities before referencing in interfaces
- MUST NOT use forbidden imports in generated code
- SHOULD include `ensures` clauses for critical business logic

#### 3.1.2 Polyglot Compiler (`compile_lattice.py`)

**Inputs:** `lattice.yaml`

**Outputs:**
| Artifact | Purpose | Location |
|----------|---------|----------|
| Pydantic Models | API contracts, validation | `src/shared/types_vX.py` |
| SQLModel ORM | Database schema | `src/shared/models_vX.py` |
| Alembic Migrations | Database versioning | `migrations/` |
| Pytest Contracts | Semantic validation | `tests/test_contracts_vX.py` |

**Guarantees:**
- Deterministic output (same input always produces same output)
- Version-aware (generates versioned modules)
- Backward compatible (old versions remain importable)

#### 3.1.3 Sheriff (AST Enforcement)

Sheriff performs instant structural validation via Abstract Syntax Tree analysis.

**Enforced Rules:**

| Rule | Description | Latency |
|------|-------------|---------|
| Import Discipline | MUST import from generated types module | Instant |
| Forbidden Imports | MUST NOT use libraries in forbidden list | Instant |
| Type Hints | MUST have return type hints on all functions | Instant |
| Version Compliance | MUST use current lattice version | Instant |

**Escape Hatch:** `# lattice:ignore` comment bypasses specific rules (audit logged)

**CLI Interface:**
```bash
sheriff.py <file> [lattice.yaml]
# Returns: PASSED or FAILED with specific violations
```

#### 3.1.4 The Gauntlet (Semantic Testing)

The Gauntlet auto-generates pytest contracts from `ensures` clauses in the lattice schema.

**Generated Tests:**
- Post-condition validation for all interface methods
- Boundary condition tests for field constraints
- Invariant preservation tests for entity state transitions

**Execution:**
```bash
pytest tests/test_contracts_vX.py
# Latency: ~8s for full suite
```

**Failure Handling:**
- Detailed error messages with exact violation
- Suggested fixes based on constraint type
- Integration with CI for blocking merges

---

### 3.2 Model Orchestrator Specification

**Status:** Implemented

#### 3.2.1 Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `ModelOrchestrator` | `scripts/core.py` | Main routing engine |
| `TaskAnalyzer` | `scripts/scorer.py` | Classifies task requirements |
| `ModelScorer` | `scripts/scorer.py` | Scores models against requirements |
| `ModelRegistry` | `scripts/registry.py` | Manages model capabilities database |
| `ModelGuideParser` | `scripts/guide.py` | Parses recommendation guides |
| API Clients | `scripts/api_clients.py` | Provider-specific implementations |

#### 3.2.2 Supported Providers

| Provider | Models | Cost | Key Strengths |
|----------|--------|------|---------------|
| Local/Ollama | 20 | Free | Privacy, offline, zero cost |
| OpenAI | 11 | Paid | GPT-4o, O1 reasoning, vision |
| Anthropic | 7 | Paid | Claude 4.1 Opus, advanced reasoning |
| Google | 6 | Paid | Gemini 2.0, 2M context |
| xAI Grok | 5 | Paid | 2M context, vision |
| Azure | 4 | Paid | Enterprise compliance |
| Bedrock | 8 | Paid | AWS managed service |
| DIAL | 2 | Paid | Enterprise gateway |

#### 3.2.3 Task Classification

The orchestrator detects and routes based on task type:

| Task Type | Primary Local | Primary Cloud | Selection Criteria |
|-----------|---------------|---------------|-------------------|
| CODE_GENERATION | codellama:34b | claude-sonnet-4.5 | accuracy > speed |
| CODE_REVIEW | deepseek-r1:70b | claude-opus-4.1 | depth > speed |
| DEBUGGING | deepseek-r1:70b | o1-pro | reasoning depth |
| REASONING | deepseek-r1:70b | o1-pro | chain-of-thought |
| VISION | llama-3.2-90b | gpt-4o | multimodal |
| QUICK_RESPONSE | llama3.1:8b | gpt-4o-mini | speed > accuracy |

#### 3.2.4 Scoring Algorithm

Models are scored using weighted criteria:

```
Score = (Task Affinity × 0.40) + (Performance × 0.30) + 
        (Accuracy × 0.20) + (Cost Efficiency × 0.10)
```

#### 3.2.5 Interaction Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Single Model | Best model for task | Default routing |
| Chain of Thought | Fast draft → quality refine | Complex generation |
| Parallel Consensus | Multiple models vote | Critical decisions |
| Hierarchical | Parent delegates to specialists | Multi-agent workflows |

#### 3.2.6 API Interface

```python
from scripts.core import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Route a request
response = await orchestrator.route_request(
    prompt="Implement a REST API endpoint",
    task_type=TaskType.CODE_GENERATION,  # Optional override
    model_id=None  # Optional force specific model
)
```

**CLI Interface:**
```bash
./scripts/orchestrator_cli.py route "Your prompt" --strategy balanced
./scripts/orchestrator_cli.py analyze "Your prompt"
./scripts/orchestrator_cli.py list --verbose
./scripts/orchestrator_cli.py cost
```

---

### 3.3 Engineering Framework Specification

**Status:** Planned

#### 3.3.1 Scaffolding CLI

**Purpose:** Create compliant project structures with minimal friction.

**Command:**
```bash
lattice-lock init <project-name> [--template agent|service|library]
```

**Generated Structure:**
```
project-name/
├── lattice.yaml              # Schema definition
├── src/
│   ├── shared/               # Generated types (DO NOT EDIT)
│   └── services/             # Implementation code
├── tests/
│   └── test_contracts.py     # Generated tests
├── .github/
│   └── workflows/
│       └── lattice-lock.yml  # CI integration
└── README.md
```

**Validation:**
- Directory uniqueness check
- Write permission verification
- Template compatibility check

#### 3.3.2 Configuration Validator

**Purpose:** Validate project configuration against policy rules.

**Validated Artifacts:**
| Artifact | Validation Rules |
|----------|------------------|
| `lattice.yaml` | Schema compliance, version format, entity references |
| `.env` | No secrets in plaintext, required variables present |
| Agent manifests | Spec v2.1 compliance, required sections present |

**CLI Interface:**
```bash
lattice-lock validate [--fix]
```

#### 3.3.3 CI/CD Integration

**Supported Platforms:** AWS CodePipeline, GCP Cloud Build, GitHub Actions

**Pipeline Stages:**

```yaml
# .github/workflows/lattice-lock.yml
name: Lattice-Lock Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Compile Lattice Schema
        run: lattice-lock compile
        
      - name: Run Sheriff (AST Validation)
        run: lattice-lock sheriff src/
        
      - name: Run Gauntlet (Semantic Tests)
        run: lattice-lock gauntlet
        
      - name: Orchestrator Smoke Test
        run: lattice-lock test-orchestrator
```

**AWS/GCP Templates:** Pre-built YAML snippets in `templates/ci/`

#### 3.3.4 Error Boundaries and Rollback

**Error Classification:**

| Error Type | Handling | Recovery |
|------------|----------|----------|
| Schema Validation | Block deployment | Fix lattice.yaml |
| Sheriff Violation | Block deployment | Fix code or add escape hatch |
| Gauntlet Failure | Block deployment | Fix implementation |
| Runtime Error | Log + alert | Automatic rollback to last known good |

**Rollback Mechanism:**
- Automatic on validation failure
- Manual trigger via CLI or API
- Preserves audit trail of all state changes

#### 3.3.5 Admin API

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/projects` | GET | List all registered projects |
| `/api/v1/projects/{id}/status` | GET | Project health and validation status |
| `/api/v1/projects/{id}/errors` | GET | Recent errors and incidents |
| `/api/v1/projects/{id}/rollback` | POST | Trigger rollback to previous state |

**Authentication:** Standard internal auth headers (OAuth2/JWT)

---

## Operational Workflows

### 4.1 Developer Onboarding Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Discover  │────▶│  Scaffold   │────▶│  Configure  │────▶│   Validate  │
│  Lattice-   │     │   Project   │     │   Schema    │     │    Local    │
│    Lock     │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                    lattice-lock init    Edit lattice.yaml   lattice-lock validate
                                                             lattice-lock compile
                                                             
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Integrate │────▶│    Test     │────▶│   Deploy    │
│    CI/CD    │     │   Pipeline  │     │             │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  Add workflow.yml    Push to branch    Merge to main
```

**Target:** <30 minutes from discovery to first successful CI validation

### 4.2 CI/CD Validation Flow

```
┌─────────────┐
│  PR Opened  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Compile   │────▶│   Sheriff   │────▶│  Gauntlet   │
│   Schema    │     │    (AST)    │     │   (Tests)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │              PASS/FAIL           PASS/FAIL
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│                  All Checks Pass?                    │
└──────────────────────────┬──────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   Approve   │          │   Block +   │
       │    Merge    │          │   Feedback  │
       └─────────────┘          └─────────────┘
```

### 4.3 Runtime Orchestration Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Receive   │────▶│   Analyze   │────▶│   Select    │
│    Task     │     │    Task     │     │    Model    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    TaskAnalyzer         ModelScorer
                    
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Execute   │────▶│   Handle    │────▶│   Return    │
│   Request   │     │   Fallback  │     │   Result    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  API Client         Retry/Alternate      APIResponse
```

---

## Roadmap and Phasing

### Current State (as of 2025-11-30)

| Component | Status | Notes |
|-----------|--------|-------|
| Model Orchestrator | Implemented | Core routing, 63 models, CLI |
| Agent Definitions | Implemented | YAML specs, workflows, memory directive |
| Governance Core | Specified | Defined in this specification (Section 3.1), not yet productionized |
| Engineering Framework | Not Started | This spec defines requirements |

### Phase 1: Foundation (Week 1-2)

**Deliverables:**
- [ ] Scaffolding CLI (`lattice-lock init`)
- [ ] Configuration validator
- [ ] Package Model Orchestrator as importable library
- [ ] Repository structure enforcement

**Dependencies:** Internal repo access

**Exit Criteria:**
- New project can be scaffolded in <5 minutes
- Validation catches 100% of structure violations
- Model Orchestrator importable as `from lattice_lock import ModelOrchestrator`

### Phase 2: CI/CD Integration (Week 2-3)

**Deliverables:**
- [ ] GitHub Actions workflow template
- [ ] AWS CodePipeline integration
- [ ] GCP Cloud Build integration
- [ ] Sheriff CLI wrapper
- [ ] Gauntlet test runner

**Dependencies:** Cloud CI/CD access, Governance Core v1

**Exit Criteria:**
- CI validates all PRs automatically
- Sheriff blocks forbidden imports
- Gauntlet runs semantic tests

### Phase 3: Error Handling & Admin (Week 3-4)

**Deliverables:**
- [ ] Error boundary system
- [ ] Automatic rollback mechanism
- [ ] Admin API (REST endpoints)
- [ ] Basic status dashboard

**Dependencies:** Logging/incident pipelines

**Exit Criteria:**
- Failed deployments auto-rollback
- Admin can view all project statuses via API
- Error logs include actionable remediation steps

### Phase 4: Documentation & Pilot (Week 4)

**Deliverables:**
- [ ] Comprehensive documentation
- [ ] Tutorial videos/walkthroughs
- [ ] Pilot 2-3 internal projects
- [ ] Feedback collection and iteration

**Dependencies:** User feedback channels

**Exit Criteria:**
- 2+ projects successfully onboarded
- Documentation covers all workflows
- User satisfaction score >4/5

### Future Phases (v2.0+)

- Edge case simulator for adversarial testing
- Advanced metrics dashboard
- Multi-cloud orchestration
- External developer platform (if scope expands)

---

## Success Metrics

### User-Centric Metrics

| Metric | Target | Phase |
|--------|--------|-------|
| Time to first CI validation | <30 minutes | Phase 1 |
| Projects using framework weekly | 5+ | Phase 4 |
| Agents passing validation pre-integration | >95% | Phase 2 |
| User satisfaction (survey) | >4/5 | Phase 4 |

### Business Metrics

| Metric | Target | Phase |
|--------|--------|-------|
| Reduction in onboarding incidents | 50%+ | Phase 2 |
| Cost savings from avoided rework | Measurable | Phase 3 |
| Adoption rate (new projects) | 80% in 6 months | Phase 4 |

### Technical Metrics

| Metric | Target | Phase |
|--------|--------|-------|
| Framework uptime | 99.9% | Phase 3 |
| Lint/test false negative rate | <2% | Phase 2 |
| Rollback success rate | >99% | Phase 3 |
| Average orchestration latency | <500ms | Phase 1 |

### Tracking Plan

Events to instrument:
- Project scaffolding (init, complete, error)
- Validation runs (start, pass, fail, error type)
- CI integration events (trigger, verdict, duration)
- Orchestrator requests (model selected, latency, cost)
- Admin API usage (endpoint, user, action)
- Incidents (type, severity, resolution time)

---

## Technical Requirements

### Infrastructure

| Requirement | Purpose |
|-------------|---------|
| Python 3.10+ | Runtime environment |
| Ollama | Local model execution |
| Docker | Containerized deployments |
| PostgreSQL | State persistence (optional) |

### Security

| Requirement | Implementation |
|-------------|----------------|
| Credential Management | HashiCorp Vault / AWS Secrets Manager |
| Secret Redaction | Never log secrets; .env validation |
| API Authentication | OAuth2/JWT for admin endpoints |
| Audit Logging | All state changes logged with actor |

### Scalability

| Dimension | Target |
|-----------|--------|
| Active projects | Hundreds |
| Validation events/day | Thousands |
| Concurrent model requests | Dozens |

### Non-Functional Guardrails

- MUST NOT require non-standard Git workflows
- MUST NOT hard-code provider secrets
- MUST be usable from headless environments
- MUST support offline operation (local models only)
- MUST NOT break existing CI pipelines on upgrade

---

## Repository Governance

### This Specification Supersedes

The following documents are superseded by this specification for architectural decisions:

| Document | Status | Action |
|----------|--------|--------|
| `WARP.md` | Superseded | Archive or delete |
| `context/lattice_lock_project_context.md` | Superseded | Archive or delete |
| `directory/repository_organization_recommendations.md` | Superseded | Archive or delete |
| `directory/file_inventory.json` | Stale | Delete |
| Standalone PRD | Superseded | Archive or delete |

### Documents to Retain (Updated Role)

| Document | New Role |
|----------|----------|
| `agent_specifications/agent_instructions_file_format_v2_1.md` | Normative agent spec (aligned with this doc) |
| `directory/repository_structure_standards.md` | Normative structure spec (aligned with this doc) |
| `developer_documentation/*` | How-to guides (must align with this spec) |

**Note:** The original reference implementation (`research/lattice_lock_llm_specification.txt`) has been archived. For historical context on the original design, see the [power-prompts repository](https://github.com/klappe-pm/power-prompts).

### Future Documentation

All new documentation MUST:
- Reference this specification as the authoritative source
- Not contradict architectural decisions herein
- Be placed in appropriate `developer_documentation/` subdirectory

---

## Appendix A: Agent Roles in Lattice-Lock

### Architect Agent
- Outputs ONLY valid `lattice.yaml` files
- Never writes implementation code
- Defines entities, invariants, interfaces, scaffold patterns

### Mason Agent
- Implements business logic within pre-defined scaffolds
- Imports ONLY from generated shared modules
- Must pass Sheriff AND Gauntlet validation
- Restarted with exact error feedback on failure

### Orchestrator
- Uses topological sorting for dependency-aware execution
- Orders file generation based on `depends_on` declarations
- Manages parallel execution where dependencies allow

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Constrained Assembly** | Paradigm treating code as filling logic within pre-defined typed modules |
| **Governance Cage** | The set of generated artifacts that constrain agent behavior |
| **Interface Drift** | Failure where agents invent non-existent APIs or data structures |
| **Lattice Schema** | The `lattice.yaml` file defining all types and contracts |
| **Mason Agent** | Implementation-focused LLM filling business logic inside scaffolds |
| **Polyglot Compiler** | Tool that transforms lattice.yaml into multiple target artifacts |
| **Schema ROI** | Ratio of generated code lines to schema definition lines |
| **Semantic Drift** | Code that compiles but violates business invariants |
| **Sheriff** | AST-based enforcer for import discipline and type hints |
| **Style Divergence** | Inconsistent, unmaintainable code from varied agent styles |
| **The Gauntlet** | Auto-generated pytest suite enforcing semantic contracts |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-30 | Kevin Lappe | Initial unified specification |

---

*This document is the authoritative specification for the Lattice-Lock Framework. All implementation decisions should reference this document.*
