---
title: "Lattice Lock Framework Specification"
type: reference
status: stable
categories: [Technical, Core]
sub_categories: [Framework]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [framework-spec-001]
tags: [framework, specification, core]
author: Architect Agent
---

# Lattice-Lock Framework Specification

**Version:** 1.0.0 | **Last Updated:** 2025-11-30 | **Author:** Kevin Lappe

---

## 01. Overview

Lattice-Lock is a **governance-first framework for AI-assisted software development** that provides deterministic, policy-enforced code generation and agent orchestration through three integrated layers:

1. **Governance Core** — Schema-driven code generation with compile-time enforcement
2. **Model Orchestrator** — Intelligent routing of AI tasks across multiple providers
3. **Engineering Framework** — Standardized tooling for repo scaffolding, CI/CD, and validation

The framework transforms code generation from probabilistic synthesis into constrained assembly, guaranteeing structural compliance and semantic correctness through pre-compilation enforcement.

### Target Audience

- Internal engineers building AI-powered applications
- DevOps/Platform teams integrating agent workflows into CI/CD
- Orchestration administrators managing multi-agent systems
- LLM agent developers creating new agent definitions

### Implementation Status

|Layer|Status|Location|
|---|---|---|
|Governance Core|Specified|Section 3.1|
|Model Orchestrator|**Implemented**|`src/lattice_lock_orchestrator/`|
|Engineering Framework|Planned|Section 3.3|

---

## 02. Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    ENGINEERING FRAMEWORK                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Scaffolding │  │   CI/CD     │  │ Validation  │  │   Admin    │ │
│  │    CLI      │  │   Hooks     │  │   Engine    │  │    API     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
          ▼                ▼                ▼               ▼
┌────────────────────────────────────────────────────────────────────┐
│                     MODEL ORCHESTRATOR                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │    Task     │  │   Model     │  │   Cost      │  │  Provider  │ │
│  │  Analyzer   │  │   Scorer    │  │  Tracker    │  │  Clients   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
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

|Layer|Purpose|Key Guarantee|
|---|---|---|
|**Governance Core**|Eliminate interface/style/semantic drift via schema-first generation|100% structural, >99% semantic compliance|
|**Model Orchestrator**|Route AI tasks across providers with cost optimization|Local-first, automatic fallback, cost-aware|
|**Engineering Framework**|Standardize project setup, CI/CD, and operations|<30 min to first CI validation|

### Layer Contracts

|Provider|Consumer|Contract|
|---|---|---|
|Governance Core|Model Orchestrator|Generated types, validation rules, forbidden imports|
|Governance Core|Engineering Framework|Sheriff CLI, Gauntlet tests, schema validation|
|Model Orchestrator|Engineering Framework|`ModelOrchestrator` class, CLI, cost/performance APIs|
|Engineering Framework|End Users|Scaffolding CLI, CI templates, admin API|

---

## 03. Component Specifications

### 3.1 Governance Core

#### Lattice Schema (`lattice.yaml`)

The **Single Source of Truth** for all type definitions, interfaces, and constraints.

```yaml
version: v2.1                    # Semantic versioning
generated_module: types_v2       # Output module name

config:
  forbidden_imports: [requests, psycopg2, sqlite3, float]
  orm_engine: sqlmodel

entities:
  EntityName:
    description: "..."
    persistence: table
    fields:
      id: { type: uuid, primary_key: true }
      price: { type: decimal, gt: 0, scale: 8 }
      status: { enum: [pending, filled, cancelled], default: pending }

interfaces:
  IServiceName:
    file: src/services/service.py
    scaffold: repository_pattern
    depends_on: []
    methods:
      method_name:
        params: { param: EntityType }
        returns: ResultType
        ensures: ["result.value > 0"]  # Semantic post-conditions
```

**Invariants:** Use semantic versioning • Define entities before referencing • No forbidden imports • Include `ensures` for critical logic

#### Polyglot Compiler (`compile_lattice.py`)

|Output|Purpose|Location|
|---|---|---|
|Pydantic Models|API contracts, validation|`src/shared/types_vX.py`|
|SQLModel ORM|Database schema|`src/shared/models_vX.py`|
|Alembic Migrations|Database versioning|`migrations/`|
|Pytest Contracts|Semantic validation|`tests/test_contracts_vX.py`|

**Guarantees:** Deterministic • Version-aware • Backward compatible

#### Sheriff (AST Enforcement)

|Rule|Description|
|---|---|
|Import Discipline|MUST import from generated types module|
|Forbidden Imports|MUST NOT use libraries in forbidden list|
|Type Hints|MUST have return type hints on all functions|
|Version Compliance|MUST use current lattice version|

**Escape Hatch:** `# lattice:ignore` bypasses specific rules (audit logged)

#### The Gauntlet (Semantic Testing)

Auto-generates pytest contracts from `ensures` clauses: post-condition validation, boundary tests, invariant preservation tests. Execution latency ~8s.

---

### 3.2 Model Orchestrator

#### 63 Supported Models

|Provider|Models|Cost|Strengths|
|---|---|---|---|
|Local/Ollama|20|Free|Privacy, offline, zero cost|
|OpenAI|11|Paid|GPT-4o, O1 reasoning, vision|
|Anthropic|7|Paid|Claude 4.1 Opus, advanced reasoning|
|Google|6|Paid|Gemini 2.0, 2M context|
|xAI Grok|5|Paid|2M context, vision|
|Azure|4|Paid|Enterprise compliance|
|Bedrock|8|Paid|AWS managed service|
|DIAL|2|Paid|Enterprise gateway|

#### Task Classification & Routing

|Task Type|Primary Local|Primary Cloud|Criteria|
|---|---|---|---|
|CODE_GENERATION|codellama:34b|claude-sonnet-4.5|accuracy > speed|
|CODE_REVIEW|deepseek-r1:70b|claude-opus-4.1|depth > speed|
|DEBUGGING|deepseek-r1:70b|o1-pro|reasoning depth|
|REASONING|deepseek-r1:70b|o1-pro|chain-of-thought|
|VISION|llama-3.2-90b|gpt-4o|multimodal|
|QUICK_RESPONSE|llama3.1:8b|gpt-4o-mini|speed > accuracy|

#### Scoring Algorithm

```
Score = (Task Affinity × 0.40) + (Performance × 0.30) +
        (Accuracy × 0.20) + (Cost Efficiency × 0.10)
```

#### Interaction Patterns

|Pattern|Use Case|
|---|---|
|Single Model|Default routing|
|Chain of Thought|Fast draft → quality refine|
|Parallel Consensus|Critical decisions (multiple models vote)|
|Hierarchical|Multi-agent workflows|

#### API Usage

```python
from scripts.core import ModelOrchestrator
orchestrator = ModelOrchestrator()
response = await orchestrator.route_request(
    prompt="Implement a REST API endpoint",
    task_type=TaskType.CODE_GENERATION
)
```

**CLI:** `./scripts/orchestrator_cli.py route|analyze|list|cost`

---

### 3.3 Engineering Framework _(Planned)_

#### Scaffolding CLI

```bash
lattice-lock init <project-name> [--template agent|service|library]
```

**Generated Structure:**

```
project-name/
├── lattice.yaml
├── src/
│   ├── shared/           # Generated types (DO NOT EDIT)
│   └── services/
├── tests/
│   └── test_contracts.py
├── .github/workflows/lattice-lock.yml
└── README.md
```

#### CI/CD Integration (GitHub Actions)

```yaml
jobs:
  validate:
    steps:
      - run: lattice-lock compile
      - run: lattice-lock sheriff src/
      - run: lattice-lock gauntlet
      - run: lattice-lock test-orchestrator
```

#### Error Handling

|Error Type|Handling|Recovery|
|---|---|---|
|Schema Validation|Block deployment|Fix lattice.yaml|
|Sheriff Violation|Block deployment|Fix code or escape hatch|
|Gauntlet Failure|Block deployment|Fix implementation|
|Runtime Error|Log + alert|Auto-rollback|

#### Admin API

|Endpoint|Method|Purpose|
|---|---|---|
|`/api/v1/projects`|GET|List projects|
|`/api/v1/projects/{id}/status`|GET|Health status|
|`/api/v1/projects/{id}/rollback`|POST|Trigger rollback|

---

## 04. Versioning Strategy

### Semantic Versioning (MAJOR.MINOR.PATCH)

|Increment|When|Migration Required|
|---|---|---|
|**MAJOR**|Breaking schema/API changes, architectural redesigns|Yes|
|**MINOR**|New backward-compatible features|No|
|**PATCH**|Bug fixes, security patches, docs|No|

### Dual Versioning

1. **Framework Version** — Overall system (`version.txt`)
2. **Schema Version** — Individual `lattice.yaml` files

```yaml
version: v2.1
generated_module: types_v2  # Major version in module name
```

### Compatibility Matrix

|Framework|Schema v1|Schema v2|Schema v3|
|---|---|---|---|
|v1.x|✅|❌|❌|
|v2.x|⚠️ Deprecated|✅|❌|
|v3.x|❌|✅|✅|

---

## 05. Roadmap

### Current State (2025-11-30)

|Component|Status|
|---|---|
|Model Orchestrator|✅ Implemented (63 models, CLI)|
|Agent Definitions|✅ Implemented (YAML specs)|
|Governance Core|📋 Specified|
|Engineering Framework|📋 Planned|

### Phases

|Phase|Weeks|Deliverables|Exit Criteria|
|---|---|---|---|
|**1: Foundation**|1-2|Scaffolding CLI, config validator, packaged orchestrator|<5 min scaffold, 100% violation detection|
|**2: CI/CD**|2-3|GitHub/AWS/GCP integration, Sheriff/Gauntlet wrappers|Auto-validate PRs, block forbidden imports|
|**3: Error Handling**|3-4|Error boundaries, auto-rollback, Admin API|>99% rollback success|
|**4: Documentation**|4|Docs, tutorials, 2-3 pilot projects|>4/5 satisfaction score|

---
## 06. Technical Requirements

### Infrastructure

Python 3.10+ • Ollama (local models) • Docker • PostgreSQL (optional)

### Security

HashiCorp Vault / AWS Secrets Manager • Never log secrets • OAuth2/JWT for admin • Audit logging

### Non-Functional Guardrails

- MUST NOT require non-standard Git workflows
- MUST NOT hard-code provider secrets
- MUST support headless and offline operation
- MUST NOT break existing CI on upgrade

---

## 07. Agent Roles

|Agent|Responsibility|
|---|---|
|**Architect**|Outputs ONLY valid `lattice.yaml`; never writes implementation|
|**Mason**|Implements logic within scaffolds; imports ONLY from generated modules; must pass Sheriff + Gauntlet|
|**Orchestrator**|Topological sorting, dependency-aware execution, parallel management|

---

## 08. Glossary

|Term|Definition|
|---|---|
|**Constrained Assembly**|Code as filling logic within pre-defined typed modules|
|**Governance Cage**|Generated artifacts that constrain agent behavior|
|**Interface Drift**|Agents inventing non-existent APIs/structures|
|**Semantic Drift**|Code that compiles but violates business invariants|
|**Sheriff**|AST-based enforcer for imports and type hints|
|**The Gauntlet**|Auto-generated pytest suite for semantic contracts|
|**Schema ROI**|Ratio of generated code lines to schema definition lines|

---

## 09. Document Governance

This specification **supersedes** all previous documentation (WARP.md, standalone PRDs, context docs) for architectural decisions.

**Retained documents:**

- `agent_specifications/agent_instructions_file_format_v2_1.md` — Normative agent spec
- `directory/repository_structure_standards.md` — Normative structure spec
- `developer_documentation/*` — How-to guides (must align with this spec)

All new documentation MUST reference this specification as authoritative.

---

_This document is the authoritative specification for the Lattice-Lock Framework._
