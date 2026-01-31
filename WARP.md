# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Lattice Lock Framework** is a governance-first AI development framework featuring intelligent multi-model orchestration across 8 AI providers and 63+ models. It enforces code quality, architecture rules, and validation policies through static analysis (Sheriff) and runtime testing (Gauntlet).

**Core Components:**
- **Orchestrator**: Intelligent model routing across 63 models from 8 providers (OpenAI, Anthropic, Google, xAI, Azure, Bedrock, Ollama, Grok)
- **Sheriff**: Millisecond AST-based static analysis engine
- **Gauntlet**: Runtime test generator from governance rules
- **Consensus**: Multi-model voting for high-stakes decisions
- **Admin API**: FastAPI dashboard with JWT auth and RBAC

## Development Commands

### Setup and Installation
```bash
# Clone and install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests (excluding integration)
make test
# Alternative: pytest tests/ -m "not integration" --tb=short

# Run critical tests only
make test-quick
# Alternative: pytest tests/ -m "critical" --tb=short

# Run specific test file
pytest tests/core/test_feedback.py

# Run with coverage (generates HTML report)
pytest tests/ --cov=src/lattice_lock --cov-report=html

# Run integration tests
pytest tests/ -m "integration"
```

### Code Quality
```bash
# Run all linters (Ruff, Black, lattice-lock validate)
make lint

# Auto-format code
make format

# Type checking
make type-check
# Alternative: mypy src/lattice_lock

# Full CI check (lint + type-check + test)
make ci
```

### Pre-commit Checks
```bash
# Run all pre-commit checks manually
make pre-commit

# Check for untracked files (required before commit)
make check-untracked
```

### Lattice Lock CLI Commands
```bash
# Initialize new project
lattice-lock init

# Static analysis (Sheriff)
lattice-lock validate
lattice-lock validate --scope src/

# Generate and run governance tests (Gauntlet)
lattice-lock test

# Compile lattice.yaml into validation artifacts
lattice-lock compile

# Query AI orchestrator
lattice-lock ask "Explain the architecture"

# List available models
lattice-lock orchestrator list

# Route task to best model
lattice-lock orchestrator route "Design a REST API"

# Analyze task for model recommendations
lattice-lock orchestrator analyze "Implement authentication"

# Start admin dashboard
lattice-lock admin start

# Start MCP server
lattice-lock mcp
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server (port 5173)
npm run dev

# Production build
npm run build

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

### Dependency Management
```bash
# Update dependencies
make deps
# Alternative: ./scripts/update_deps.sh && pip install -r requirements.lock
```

### Cleanup
```bash
# Remove build artifacts
make clean

# Clean merged branches
make git-cleanup
```

## Architecture and Code Structure

### High-Level Architecture

The framework uses a **Repository Pattern** for data access with **SQLAlchemy ORM**, feature flags for modular functionality, and a CLI built with **Click**. All components communicate through well-defined interfaces.

**Data Flow:**
1. User input → CLI → Command handlers
2. Commands invoke orchestrator/sheriff/gauntlet
3. Results flow back through CLI → Console output

### Source Code Organization

```
src/lattice_lock/
├── orchestrator/          # Multi-model routing (main intelligence)
│   ├── core.py           # ModelOrchestrator - main entry point
│   ├── registry.py       # Model configuration registry (63 models)
│   ├── scorer.py         # Capability scoring algorithm
│   ├── analysis/         # Task analysis and classification
│   ├── providers/        # 8 provider implementations
│   └── consensus/        # Multi-model voting engine
├── sheriff/              # Static analysis engine
│   ├── sheriff.py        # Main Sheriff class - AST analysis
│   ├── ast_visitor.py    # Python AST traversal
│   ├── rules.py          # Rule evaluation
│   └── cache.py          # Performance caching
├── gauntlet/             # Runtime test generator
│   ├── generator.py      # GauntletGenerator - main class
│   ├── parser.py         # Lattice YAML parser
│   └── plugin.py         # pytest plugin integration
├── admin/                # FastAPI admin dashboard
│   ├── app.py           # Main FastAPI app
│   ├── auth.py          # JWT authentication
│   └── routes/          # REST endpoints (29 endpoints)
├── cli/                  # Click-based CLI
│   ├── __main__.py      # CLI entry point
│   ├── commands/        # Individual commands
│   └── groups/          # Command groups
├── database/             # SQLAlchemy repository pattern
├── config/               # Feature flags and app config
├── mcp/                  # Model Context Protocol server
└── utils/                # Shared utilities
```

### Key Design Patterns

**Repository Pattern**: All database access goes through repository classes in `database/`. Never use raw SQLAlchemy queries in business logic.

**Feature Flags**: Controlled via `config/feature_flags.py`. Features can be disabled with `LATTICE_DISABLED_FEATURES` env var.

**Provider Interface**: All AI providers implement a common interface in `orchestrator/providers/base.py`. Adding a new provider means implementing this interface.

**Scoring System**: Task routing uses multi-factor scoring (0.0-1.0) based on:
- Base score (0.50)
- Primary task match (0.30)
- Secondary task match (0.10)
- Complexity boost (0.10)

**AST-Based Analysis**: Sheriff uses Python's `ast` module to traverse code without execution. Rules are defined in `lattice.yaml` and compiled to checkers.

### Module Dependencies

**Core dependencies:**
- `orchestrator` → No internal dependencies (can be used standalone)
- `sheriff` → `config`, `utils`
- `gauntlet` → `config`, `utils`
- `cli` → All modules (orchestrates everything)
- `admin` → `database`, `config`, `auth`

**External dependencies:**
- `httpx` for async HTTP (all provider calls)
- `pydantic` for data validation
- `rich` for terminal formatting
- `click` for CLI
- `fastapi` + `uvicorn` for admin API
- `sqlalchemy` + `aiosqlite` for database

### Testing Strategy

**Test Organization:**
- Unit tests: `tests/{module}/test_*.py`
- Integration tests: `tests/integration/` (marked with `@pytest.mark.integration`)
- Critical path tests: Marked with `@pytest.mark.critical`
- Cross-module tests: Marked with `@pytest.mark.cross_module`

**Fixtures:** Global fixtures in `tests/conftest.py`, module-specific in `tests/{module}/conftest.py`

**Coverage Target:** 70% minimum (enforced by pytest config), currently at 82%

## Coding Standards

### File and Directory Naming

**MANDATORY RULE**: All file and directory names must be `lowercase_with_underscores`

**Correct:** `my_module.py`, `user_service.py`, `api_client.ts`
**Incorrect:** `MyModule.py`, `UserService.py`, `my-module.py`

**Exceptions:** `LICENSE.md`, `Makefile`, `Dockerfile`, `.gitignore` (conventions)

### Python Code Standards

**File Headers:** All Python scripts must start with `#!/usr/bin/env python3`

**Import Order:**
1. Standard library
2. Third-party packages
3. Local imports (absolute imports from `src/`)

**Type Hints:** Required for all public APIs (functions, class methods)

**Docstrings:** Google-style or NumPy-style for all public classes and functions

**Formatting:**
- Line length: 100 characters (Black config)
- Class names: `PascalCase`
- Functions/variables: `snake_case`

### Pre-commit Requirements

**⚠️ CRITICAL**: Commits are **blocked** if untracked files exist (excluding standard ignores like `.env`, `node_modules`, etc.)

**Always run before committing:**
```bash
make check-untracked
```

All pre-commit hooks must pass:
- Trailing whitespace check
- YAML validation
- Black formatting
- Ruff linting
- File naming convention check
- Lattice structure validation
- Untracked files check

## Git Workflow

### Branch Strategy

- **Single permanent branch:** `main`
- **Work in forks:** Create short-lived feature branches in your fork
- **Branch naming:** `{actor}/{ticket-or-issue}-{slug}`
  - Examples: `human/1234-doc-fix`, `claude/refactor-logger`, `warp/add-feature`

### Merge Strategy

- **Squash-and-merge only** (enforced at repo level)
- Auto-delete head branches after merge
- Linear history maintained on `main`

### Pull Request Requirements

**Required Labels:**
- One type: `feat`, `fix`, `chore`, `docs`, `refactor`
- One source: `human`, `llm`, `devin`

**Required Checks:**
- Tests pass
- Lint pass
- Typecheck pass
- CI policy job pass

**Review:** `@greptileai` is auto-assigned via CODEOWNERS

### Commit Messages

Use Conventional Commits style:
```
feat: add model selection caching
fix: resolve race condition in orchestrator
chore: update dependencies
docs: clarify governance workflow
```

**Co-authorship for AI contributions:**
```
feat: implement new validation rule

Co-Authored-By: Warp <agent@warp.dev>
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

**Required (at least one provider):**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
XAI_API_KEY=...
```

**Optional:**
```bash
# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Local Models
OLLAMA_HOST=http://localhost:11434

# Feature Control
LATTICE_FEATURE_PRESET=full  # minimal, standard, full
LATTICE_DISABLED_FEATURES=   # sheriff,gauntlet,feedback,rollback,consensus,mcp
LATTICE_DEFAULT_MODEL=auto   # auto, manual, or specific model ID
LATTICE_LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///lattice.db

# Admin API
ADMIN_SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Lattice Policy File

The `lattice.yaml` file defines governance rules (not present by default - created via `lattice-lock init`):

```yaml
version: "2.1"
rules:
  - id: "no-print"
    description: "Use logger instead of print statements"
    severity: error
    scope: "src/**/*.py"
    excludes: ["scripts/*", "tests/*"]
    forbids: "node.is_call_to('print')"
```

## Model Orchestration

### Task Types and Routing

The orchestrator automatically routes tasks to optimal models based on task type:

- **code_generation**: o1-pro > claude-4-5-opus > claude-4-5-sonnet
- **debugging**: o1-pro > claude-4-sonnet > grok-4-fast-reasoning
- **architectural_design**: o1-pro > claude-4-5-opus > qwen3-next-80b
- **documentation**: claude-4-5-sonnet > gpt-4o > gemini-2.5-pro
- **testing**: o1-mini > claude-4-sonnet > gemini-2.5-flash

See `MODELS.md` for complete routing preferences and capability matrix.

### Cost Tiers

- **Premium** ($15+/1M tokens): o1-pro, claude-4-5-opus
- **Standard** ($3-15/1M tokens): claude-4-5-sonnet, gpt-4o, claude-4-sonnet
- **Budget** ($0.15-3/1M tokens): grok-code-fast-1, gemini-2.5-pro, claude-3-5-haiku
- **Free** (Local): qwen3-next-80b, deepseek-r1:70b, glm4, codellama:34b

### Priority Modes

- `quality`: Favors reasoning and coding scores
- `speed`: Favors fast models
- `cost`: Favors low-cost models
- `balanced`: Equal weighting (default)

## Common Patterns

### Using the Orchestrator

```python
from lattice_lock.orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Auto-route to best model
response = await orchestrator.route("Analyze this code for security issues", context)

# List available models
models = orchestrator.list_models()

# Get routing recommendation
recommendation = orchestrator.analyze_task("Design a microservices architecture")
```

### Running Sheriff

```python
from lattice_lock.sheriff import run_sheriff

# Run analysis on current project
violations = run_sheriff()

for violation in violations:
    print(f"[{violation.severity}] {violation.rule_id}: {violation.message}")
    print(f"  Location: {violation.file}:{violation.line}")
```

### Generating Tests with Gauntlet

```python
from lattice_lock.gauntlet import GauntletGenerator

generator = GauntletGenerator()

# Generate tests from lattice.yaml
tests = generator.generate()

# Run generated tests
results = generator.run()
```

## Important Notes

**Documentation is the Single Source of Truth**: `CONTRIBUTING.md` is the authoritative source for all contribution standards. This WARP.md provides Warp-specific guidance but defers to CONTRIBUTING.md for standards.

**No Direct Pushes to Main**: Local pre-push hook blocks non-main branch pushes to origin. Always work in a fork and open PRs.

**Untracked Files Policy**: Commits are blocked if untracked files exist. Add files to git or `.gitignore` before committing.

**Testing Philosophy**: Tests must pass before merge. Add tests for new features. Maintain 70%+ coverage.

**AI Provider Keys**: Never commit API keys. Use `.env` file (gitignored). Use environment variables in code.

**Feature Flags**: Disable features via `LATTICE_DISABLED_FEATURES` env var for testing or resource constraints.
