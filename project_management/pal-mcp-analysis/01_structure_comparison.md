# Module 1: Project Structure & Organization Comparison

## Executive Summary

Lattice Lock follows a **deep, domain-driven hierarchy** while PAL MCP uses a **flat, tool-centric structure**. Both approaches are valid for their respective purposes—Lattice Lock's structure supports governance and compliance, while PAL MCP's flat structure enables rapid tool development and discovery.

---

## Directory Structure Comparison

### Root Level

| Aspect | Lattice Lock | PAL MCP |
|--------|--------------|---------|
| Source code | `src/lattice_lock/` | Root-level `tools/`, `providers/`, `utils/` |
| Configuration | `pyproject.toml`, `Makefile` | `.env.example`, `conf/*.json` |
| Documentation | `docs/` | `docs/tools/`, `systemprompts/` |
| Tests | `tests/` | `tests/`, `simulator_tests/` |
| CI/CD | `.github/workflows/` | `.github/workflows/` |
| Scripts | `scripts/` | `run-server.sh`, `run-server.ps1` |
| Containers | `Dockerfile`, `docker-compose.yml` | `docker-compose.yml` + multi-platform scripts |

### Lattice Lock Root Structure (Actual)
```
lattice-lock-framework/
├── .github/workflows/      # 8 files (ci, release, reusable-*, snyk-security)
├── docs/                   # 11 subdirs (agents, architecture, guides, etc.)
├── frontend/               # Web frontend
├── infrastructure/         # IaC configs
├── project-management/     # Planning docs
├── scripts/                # 26 utility scripts
├── shared/                 # Shared resources
├── src/lattice_lock/       # Core Python package
├── tests/                  # 22 test subdirectories
├── contributing.md         # Single source of truth (540 lines)
├── pyproject.toml          # Project config (180 lines)
├── Makefile                # Build automation
├── Dockerfile              # Container definition
└── docker-compose.yml      # Container orchestration
```

### Key Differences

| Pattern | Lattice Lock | PAL MCP Equivalent |
|---------|--------------|-------------------|
| Agent instructions | ❌ **Missing** | `CLAUDE.md`, `AGENTS.md` at root |
| Environment template | ❌ **Missing** | `.env.example` with sections |
| Per-provider config | Code-embedded in `models.yaml` | `conf/*.json` external catalogs |
| Cross-platform scripts | Single platform | `.sh` + `.ps1` pairs |

---

## Source Code Organization

### Lattice Lock: Deep Hierarchy

```
src/lattice_lock/
├── orchestrator/           # 10 subdirs, 14 files
│   ├── analysis/           # Task analysis
│   ├── consensus/          # Multi-model consensus
│   ├── cost/               # Cost tracking
│   ├── execution/          # Execution engine
│   ├── providers/          # API clients (11 files)
│   ├── routing/            # Request routing
│   ├── scoring/            # Model scoring
│   ├── selection/          # Model selection
│   ├── models.yaml         # Model definitions
│   └── registry.py         # Model registry
├── sheriff/                # Static analysis (7 files)
├── gauntlet/               # Runtime testing (6 files)
├── validator/              # Validation rules (5 files)
├── cli/                    # Command-line interface (39 files)
├── admin/                  # Admin API (18 files)
├── dashboard/              # Dashboard UI (22 files)
├── database/               # ORM models (5 files)
├── agents/                 # Agent definitions (26 files)
├── config/                 # Config management
├── errors/                 # Error handling
├── feedback/               # User feedback
├── rollback/               # Rollback functionality
└── utils/                  # Utilities
```

### PAL MCP: Flat Tool-Centric

```
/
├── tools/                  # One file per tool
│   ├── chat.py
│   ├── thinkdeep.py
│   ├── planner.py
│   ├── consensus.py
│   ├── codereview.py
│   └── [base classes in utils/]
├── providers/              # Provider clients
├── utils/                  # Shared utilities
└── conf/                   # External configs
```

### Analysis

| Metric | Lattice Lock | PAL MCP |
|--------|--------------|---------|
| Nesting depth | 4-5 levels | 2-3 levels |
| Module coupling | Tight (governance domain) | Loose (tool independence) |
| Feature discovery | Requires docs | Self-documenting file names |
| Extension model | Add to existing hierarchy | Add flat file to `tools/` |

---

## Configuration Organization

### Lattice Lock Configuration Files

| File | Purpose | Lines |
|------|---------|-------|
| `pyproject.toml` | Project config, dependencies, tool settings | 180 |
| `Makefile` | Build automation (lint, test, ci, deps) | 47 |
| `.pre-commit-config.yaml` | Pre-commit hooks | ~50 |
| `contributing.md` | All standards (single source of truth) | 540 |
| `src/lattice_lock/orchestrator/models.yaml` | Model definitions | ~100 |
| `src/lattice_lock/orchestrator/scorer_config.yaml` | Scorer settings | ~30 |

### PAL MCP Configuration Pattern

```
.env.example                    # Comprehensive template
├── DISABLED_TOOLS=...          # Feature flags
├── DEFAULT_MODEL=auto          # Model selection
├── Provider API keys           # Secrets template
├── *_MODELS_CONFIG_PATH=...    # External catalog paths
└── Docker/logging config

conf/
├── openai_models.json          # External model catalog
├── gemini_models.json
├── openrouter_models.json
├── azure_models.json
└── custom_models.json
```

### Gap Analysis

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| `.env.example` with sections | ❌ Missing | Create comprehensive template |
| External model catalogs (JSON) | ❌ Using embedded YAML | Consider externalizing |
| `DISABLED_TOOLS` feature flags | ❌ Missing | Add for Sheriff/Gauntlet |
| Per-tool config paths | ❌ Embedded in code | OK for governance use case |

---

## Agent/AI Instruction Files

### PAL MCP Pattern
```
CLAUDE.md        # Claude Code context, build/test commands, code style
AGENTS.md        # Multi-agent coordination context
```

### Lattice Lock Status

| File | Status | Notes |
|------|--------|-------|
| `CLAUDE.md` | ❌ **Not found** | Critical gap for AI agents |
| `AGENTS.md` | ❌ **Not found** | Critical gap for multi-agent |
| `contributing.md` | ✅ Exists | Comprehensive but not AI-optimized |

### Recommendation

> [!IMPORTANT]
> Create `CLAUDE.md` immediately. This is a quick win that significantly improves AI agent effectiveness.

Proposed `CLAUDE.md` structure:
```markdown
# Lattice Lock Framework

## Quick Commands
- `make lint` - Run linters
- `make test` - Run unit tests
- `make ci` - Full CI check

## Project Structure
[Brief overview]

## Code Style
[Key conventions from contributing.md]

## Testing
[How to run tests, coverage requirements]
```

---

## Scripts Organization

### Lattice Lock: Centralized

```
scripts/
├── setup/                  # Setup scripts
├── migrations/             # DB migrations
├── tests/                  # Script tests
├── utilities/              # Various utilities
├── agent_prompts.py        # Agent prompt management
├── claude_code_agent.py    # Claude agent script
├── gemini_*.py             # Gemini agent scripts
├── devin_agent.py          # Devin agent script
├── validate_agents.py      # Agent validation
└── [20+ utility scripts]
```

### PAL MCP: Distributed + Cross-Platform

```
/
├── run-server.sh           # Unix launch script
├── run-server.ps1          # Windows launch script
└── [scripts in relevant directories]
```

### Gap Analysis

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| Cross-platform scripts | ❌ Unix-only | Consider `.ps1` equivalents if Windows support needed |
| Script distribution | Centralized | OK for governance use case |
| Agent-specific scripts | ✅ Comprehensive | Well-organized |

---

## Documentation Structure

### Lattice Lock Documentation Pattern

```
docs/
├── agents/                 # 120 files (agent definitions, workflows)
├── architecture/           # 7 files
├── database/               # 2 files
├── design/                 # 4 files
├── examples/               # 32 files
├── features/               # 2 files
├── guides/                 # 26 files
├── reference/              # 20 files
├── testing/                # 1 file
├── tutorials/              # 4 files
└── README.md               # Navigation hub
```

### PAL MCP Documentation Pattern

```
docs/
├── tools/                  # Per-tool docs with video demos
│   ├── chat.md
│   ├── codereview.md
│   └── [tool].md
├── getting-started.md
├── configuration.md
├── advanced-usage.md
├── troubleshooting.md
└── index.md
```

### Gap Analysis

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| Per-tool/module docs | ⚠️ Partial | Add dedicated pages for Sheriff, Gauntlet, Orchestrator |
| Video demos | ❌ Missing | Consider for key workflows |
| Changelog | ❌ Missing | Add `CHANGELOG.md` |
| `SECURITY.md` | ❌ Missing | Add security policy |

---

## Key Findings

### Strengths of Lattice Lock Structure

1. **Domain-driven organization** - Modules map to governance concepts
2. **Comprehensive contributing.md** - Single source of truth
3. **Rich agent definitions** - 40+ YAML agent templates
4. **Reusable CI workflows** - `reusable-*.yml` pattern
5. **Structured test hierarchy** - Mirrors source structure

### Gaps to Address

| Priority | Gap                      | Impact |
| -------- | ------------------------ | ------ |
| P0       | Missing `CLAUDE.md`      | High   |
| P0       | Missing `.env.example`   | High   |
| P1       | Missing `CHANGELOG.md`   | Medium |
| P1       | Missing `SECURITY.md`    | Medium |
| P2       | External model catalogs  | Low    |
| P2       | Per-module documentation | Medium |

### Patterns to Preserve

1. **Deep hierarchy** - Suits governance domain (don't flatten)
2. **Centralized scripts** - Easier to maintain
3. **Single contributing.md** - Keep as source of truth
4. **Reusable CI workflows** - Already better than PAL MCP

---

## Action Items

1. **Create `CLAUDE.md`** at repository root with build commands, project structure overview, and code style summary
2. **Create `.env.example`** with all configuration options, organized by section
3. **Add `CHANGELOG.md`** with semantic versioning
4. **Add `SECURITY.md`** with vulnerability reporting process
5. **Consider `AGENTS.md`** for multi-agent coordination context

---

*Module 1 completed. Next: Module 2 - Tool/Feature Architecture*
