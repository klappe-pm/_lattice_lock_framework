# Project Index: Lattice Lock Framework

**Generated:** 2026-01-06
**Version:** 2.1.0
**Python:** 3.10 | 3.11 | 3.12

---

## Overview

A governance-first framework for AI-assisted software development with intelligent model orchestration. Bridges static analysis and runtime testing to enforce code quality, architecture rules, and validation policies.

---

## Project Structure

```
lattice-lock-framework/
├── src/                    # Core source code (199 Python files)
│   ├── orchestrator/       # Multi-model AI routing (63 models, 8 providers)
│   ├── sheriff/            # AST-based static analysis
│   ├── gauntlet/           # Runtime test generator
│   ├── consensus/          # Multi-model voting engine
│   ├── cli/                # Command-line interface
│   ├── admin/              # Admin dashboard & auth
│   ├── compiler/           # Lattice compilation
│   ├── config/             # Configuration management
│   ├── dashboard/          # Monitoring UI
│   ├── database/           # Repository pattern & models
│   ├── errors/             # Error handling
│   ├── feedback/           # User feedback system
│   ├── mcp/                # MCP server integration
│   ├── rollback/           # State rollback system
│   ├── utils/              # Shared utilities
│   └── validator/          # Schema validation
├── agents/                 # Agent system (90 agent definitions)
│   ├── agent_definitions/  # YAML agent configs
│   ├── agent_templates/    # Reusable templates
│   ├── agent_workflows/    # Execution patterns
│   └── agent_memory/       # Memory directives
├── tests/                  # Test suite (87 test files)
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── frontend/               # Dashboard UI (React)
```

---

## Entry Points

| Type | Path | Description |
|------|------|-------------|
| **CLI** | `src/cli/__main__.py` | Main CLI entry (`lattice-lock`) |
| **Package** | `src/__init__.py` | Package initialization |
| **Scripts** | `scripts/orchestrator_cli.py` | Orchestrator testing |

**CLI Commands:**
- `lattice-lock init` - Initialize project
- `lattice-lock validate` - Run static analysis (Sheriff)
- `lattice-lock test` / `gauntlet` - Generate & run tests
- `lattice-lock ask "<query>"` - Query orchestrator
- `lattice-lock compile` - Compile lattice.yaml
- `lattice-lock doctor` - Health check
- `lattice-lock feedback` - Submit feedback
- `lattice-lock mcp` - MCP server management
- `lattice-lock admin` - Admin operations
- `lattice-lock orchestrator` - Model orchestration
- `lattice-lock chain` - Chain execution
- `lattice-lock handoff` - Context handoff

---

## Core Modules

### Orchestrator (`src/orchestrator/`)
Intelligent model routing across 63 AI models from 8 providers.

**Exports:**
- `ModelOrchestrator` - Main orchestration engine
- `ModelRegistry` - Model configuration registry
- `ModelScorer`, `TaskAnalyzer` - Scoring & analysis
- `ConsensusEngine`, `ConsensusOrchestrator` - Multi-model consensus
- `ChainOrchestrator` - Chain execution

**Submodules:** analysis, cli, consensus, cost, execution, providers, routing, scoring, selection

### Sheriff (`src/sheriff/`)
AST-based static analysis for architecture violations.

**Exports:**
- `run_sheriff` - Run analysis
- `SheriffResult`, `Violation` - Results
- `SheriffConfig`, `ViolationSeverity` - Configuration

### Gauntlet (`src/gauntlet/`)
Runtime test generator from governance rules.

**Exports:**
- `GauntletGenerator` - Test generation engine

### Consensus (`src/consensus/`)
Multi-model voting for high-stakes decisions.

**Exports:**
- `ConsensusEngine` - Voting engine
- `ConsensusRequest`, `VoteStrategy` - Types

### CLI (`src/cli/`)
Click-based command-line interface.

**Commands:** ask, chain, compile, doctor, feedback, gauntlet, handoff, init, mcp, sheriff, validate
**Groups:** admin, orchestrator

---

## Agent System

**Total Agents:** 90 YAML definitions
**Agent Types:** 14 main agents with subagents

| Agent | Purpose |
|-------|---------|
| `engineering_agent` | Backend, frontend, DevOps, security, testing |
| `product_agent` | Business analysis, metrics, strategy |
| `project_agent` | Planning, status, task management |
| `research_agent` | Market research, competitive analysis |
| `content_agent` | Writing, SEO, localization |
| `ux_agent` | Design, accessibility, usability |
| `cloud_agent` | AWS, Azure, GCP |
| `context_agent` | Memory, knowledge synthesis |
| `prompt_architect_agent` | Prompt generation & optimization |
| `business_review_agent` | Financial, performance analysis |
| `google_apps_script_agent` | GAS development |
| `public_relations_agent` | Press releases |
| `model_orchestration_agent` | Model routing |

---

## Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package config, dependencies, tool settings |
| `docker-compose.yml` | Container orchestration |
| `.env.example` | Environment template (API keys, features) |
| `lattice.yaml` | Project governance rules (user-created) |
| `.mcp/` | MCP server configurations |

**Feature Flags (LATTICE_FEATURE_PRESET):**
- `full` (default) - All features
- `standard` - Orchestrator, Sheriff, Gauntlet
- `minimal` - Core Orchestrator only

**Disable Features (LATTICE_DISABLED_FEATURES):**
- `sheriff`, `gauntlet`, `feedback`, `rollback`, `consensus`, `mcp`

---

## Test Coverage

**Test Files:** 87
**Coverage Target:** 70% (configured)
**Test Framework:** pytest + pytest-asyncio

| Category | Files | Focus |
|----------|-------|-------|
| `orchestrator/` | 20+ | Model routing, providers, scoring |
| `cli/` | 6 | Command validation |
| `gauntlet/` | 4 | Test generation |
| `integration/` | 5 | Cross-module |
| `api/` | 4 | Admin API, auth |
| `governance/` | 3 | Sheriff rules |
| `templates/` | 4 | CI/CD templates |
| `e2e_300/` | 1 | E2E matrix |
| `benchmarks/` | 1 | Performance |

**Run Tests:**
```bash
pytest                          # All tests
pytest tests/orchestrator/      # Specific module
pytest -m critical              # Critical path only
```

---

## Key Dependencies

| Package      | Version   | Purpose             |     |
| ------------ | --------- | ------------------- | --- |
| `httpx`      | >=0.25.0  | HTTP client         |     |
| `pydantic`   | >=2.0.0   | Data validation     |     |
| `click`      | >=8.0.0   | CLI framework       |     |
| `fastapi`    | >=0.100.0 | API framework       |     |
| `rich`       | >=13.0.0  | Terminal formatting |     |
| `tenacity`   | >=8.2.0   | Retry logic         |     |
| `Jinja2`     | >=3.1.0   | Templating          |     |
| `mcp`        | >=0.1.0   | MCP protocol        |     |
| `sqlalchemy` | >=2.0.0   | Database ORM        |     |
| `bcrypt`     | >=4.0.1   | Password hashing    |     |
| `PyJWT`      | >=2.8.0   | JWT tokens          |     |

---

## Documentation

| Path | Content |
|------|---------|
| `docs/guides/` | Tutorials, setup, workflows (29 files) |
| `docs/reference/` | API docs, CLI reference |
| `docs/architecture/` | System design, diagrams |
| `docs/tutorials/` | Step-by-step guides |
| `contributing.md` | **SINGLE SOURCE OF TRUTH** for standards |
| `docs/MODELS.md` | Supported AI models |

---

## Quick Start

```bash
# 1. Install
pip install lattice-lock

# 2. Initialize project
lattice-lock init

# 3. Configure (edit lattice.yaml)

# 4. Validate architecture
lattice-lock validate

# 5. Generate tests
lattice-lock test

# 6. Ask the orchestrator
lattice-lock ask "Explain the architecture"
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
black src/ --check

# Type check
mypy src/
```

---

## Key Files for Context

When starting a session, read these first:
1. This file (`PROJECT_INDEX.md`)
2. `contributing.md` - Coding standards
3. `docs/CLAUDE.md` - AI assistant instructions
4. `pyproject.toml` - Dependencies & config

---

*Index size: ~3KB | Full codebase: ~58K tokens | Savings: 94%*
