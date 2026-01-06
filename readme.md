# Lattice Lock Framework

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-82%25-green)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-2.1.0-orange)

**A governance-first framework for AI-assisted software development with intelligent model orchestration.**

Lattice Lock keeps humans and AI agents in perfect sync by enforcing code quality, architecture rules, and validation policies across your codebase. It bridges the gap between static analysis and runtime testing, ensuring your project adheres to its defined structure ("The Lattice").

---

## Table of Contents

- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Core Components](#core-components)
  - [Orchestrator](#orchestrator)
  - [Sheriff](#sheriff)
  - [Gauntlet](#gauntlet)
  - [Consensus Engine](#consensus-engine)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Admin Dashboard](#admin-dashboard)
- [Feature Flags](#feature-flags)
- [Project Structure](#project-structure)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Orchestrator** | Intelligent multi-model routing across 8 AI providers (OpenAI, Anthropic, Google, xAI, Azure, Bedrock, Ollama, Grok) with automatic model selection |
| **Sheriff** | AST-based static analysis engine that catches architecture violations in milliseconds |
| **Gauntlet** | Runtime test generator that creates pytest suites from governance rules defined in `lattice.yaml` |
| **Consensus** | Multi-model voting engine for high-stakes decision making through model agreement |
| **Admin API** | FastAPI-based dashboard with JWT authentication and role-based access control |
| **Agent System** | 90+ pre-defined AI agent specifications for specialized tasks |
| **MCP Integration** | Model Context Protocol support for extended AI capabilities |

---

## Quick Start

```bash
# Install the package
pip install lattice-lock

# Initialize a new project
lattice-lock init

# Create your governance rules in lattice.yaml
# (see Configuration section below)

# Run static analysis
lattice-lock validate

# Generate and run tests
lattice-lock test

# Query the AI orchestrator
lattice-lock ask "Explain the architecture of this project"
```

### Minimal Example

Create a `lattice.yaml` in your project root:

```yaml
version: "2.1"
rules:
  - id: "no-print"
    description: "Use logger instead of print statements in production code."
    severity: "error"
    scope: "src/**/*.py"
    excludes: ["scripts/*", "tests/*"]
    forbids: "node.is_call_to('print')"
```

Then validate:

```bash
lattice-lock validate
# Output: [ERROR] no-print: Use logger instead of print... (src/bad_code.py:2)
```

---

## Installation

### From PyPI

```bash
pip install lattice-lock
```

### From Source

```bash
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework
pip install -e ".[dev]"
```

### Requirements

- **Python**: 3.10, 3.11, or 3.12
- **At least one AI provider API key** (for orchestration features)

---

## Core Components

### Orchestrator

The Orchestrator provides intelligent model routing and selection across multiple AI providers. It analyzes tasks and routes them to the most appropriate model based on capability scoring.

**Supported Providers:**

| Provider | Models | Context |
|----------|--------|---------|
| OpenAI | GPT-4, GPT-4 Turbo, GPT-3.5, O1 | Up to 128K |
| Anthropic | Claude 3.x, Claude 4.x | Up to 200K |
| Google | Gemini 2.x, Gemini 1.5 | Up to 2M |
| xAI | Grok models | Up to 2M |
| Azure OpenAI | Azure-hosted OpenAI models | Varies |
| AWS Bedrock | Multiple providers via AWS | Varies |
| Ollama | Local open-source models | Varies |
| Grok | Custom implementation | Up to 2M |

**Usage:**

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

**CLI:**

```bash
# List all available models
lattice-lock orchestrator list

# Route a task to the best model
lattice-lock orchestrator route "Design a REST API"

# Analyze task for model recommendations
lattice-lock orchestrator analyze "Implement authentication system"
```

### Sheriff

Sheriff is the static analysis engine that uses AST (Abstract Syntax Tree) traversal to catch architecture violations in milliseconds without running your code.

**Key Features:**
- AST-based Python analysis
- Rule-based violation detection
- Caching for performance
- Multiple output formats

**Usage:**

```python
from lattice_lock.sheriff import run_sheriff

# Run analysis on current project
violations = run_sheriff()

for violation in violations:
    print(f"[{violation.severity}] {violation.rule_id}: {violation.message}")
    print(f"  Location: {violation.file}:{violation.line}")
```

**CLI:**

```bash
# Run static analysis
lattice-lock validate

# With specific scope
lattice-lock validate --scope src/
```

### Gauntlet

Gauntlet generates pytest test suites from your governance rules defined in `lattice.yaml`. It creates runtime tests for semantic properties that cannot be checked statically.

**Usage:**

```python
from lattice_lock.gauntlet import GauntletGenerator

generator = GauntletGenerator()

# Generate tests from lattice.yaml
tests = generator.generate()

# Run generated tests
results = generator.run()
```

**CLI:**

```bash
# Generate and run governance tests
lattice-lock test

# Alias
lattice-lock gauntlet
```

### Consensus Engine

The Consensus Engine enables high-stakes decision making by querying multiple AI models and aggregating their responses through voting.

**Usage:**

```python
from lattice_lock.consensus import ConsensusEngine

consensus = ConsensusEngine()

# Get multi-model consensus on a decision
result = await consensus.vote(
    prompt="Should we use microservices or monolithic architecture?",
    models=["gpt-4", "claude-3-opus", "gemini-2.0-pro"],
    threshold=0.7  # 70% agreement required
)

print(f"Decision: {result.decision}")
print(f"Confidence: {result.confidence}")
print(f"Model votes: {result.votes}")
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

**Required (at least one provider):**

```bash
# AI Provider API Keys
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
LATTICE_FEATURE_PRESET=full          # minimal, standard, full
LATTICE_DISABLED_FEATURES=           # Comma-separated: sheriff,gauntlet,feedback,rollback,consensus,mcp
LATTICE_DEFAULT_MODEL=auto           # auto, manual, or specific model ID
LATTICE_LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Database
DATABASE_URL=sqlite:///lattice.db

# Admin API (for dashboard)
ADMIN_SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Lattice Policy File

The `lattice.yaml` file is the constitution of your project. It defines all governance rules.

```yaml
version: "2.1"

# Global settings
settings:
  severity_threshold: warning
  fail_fast: false

# Rule definitions
rules:
  - id: "no-print"
    description: "Use logger instead of print statements"
    severity: error
    scope: "src/**/*.py"
    excludes: ["scripts/*", "tests/*"]
    forbids: "node.is_call_to('print')"

  - id: "max-function-length"
    description: "Functions should not exceed 50 lines"
    severity: warning
    scope: "src/**/*.py"
    check: "node.line_count <= 50"

  - id: "require-docstrings"
    description: "Public functions must have docstrings"
    severity: error
    scope: "src/**/*.py"
    requires: "node.has_docstring()"
    filter: "node.is_public_function()"
```

---

## CLI Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `lattice-lock init` | Initialize a new project with lattice.yaml |
| `lattice-lock validate` | Run static analysis (Sheriff) |
| `lattice-lock test` | Generate and run governance tests (Gauntlet) |
| `lattice-lock compile` | Compile lattice.yaml into validation artifacts |
| `lattice-lock ask "<prompt>"` | Query the AI orchestrator |
| `lattice-lock doctor` | Diagnose project configuration issues |
| `lattice-lock feedback` | Submit feedback about the framework |

### Orchestrator Commands

```bash
lattice-lock orchestrator list              # List available models
lattice-lock orchestrator route "<task>"    # Route task to best model
lattice-lock orchestrator analyze "<task>"  # Get model recommendations
```

### Admin Commands

```bash
lattice-lock admin start      # Start admin dashboard server
lattice-lock admin users      # Manage users
lattice-lock admin keys       # Manage API keys
```

### Context Handoff

```bash
lattice-lock handoff export   # Export current context
lattice-lock handoff import   # Import context from another session
```

### MCP Server

```bash
lattice-lock mcp              # Start MCP server
lattice-lock mcp --stdio      # Start in stdio mode
```

---

## Admin Dashboard

Lattice Lock includes a FastAPI-based admin dashboard for managing users, monitoring usage, and configuring the system.

### Starting the Dashboard

```bash
# Using CLI
lattice-lock admin start

# Using uvicorn directly
uvicorn lattice_lock.admin:admin_app --port 8080
```

### Features

- **JWT Authentication**: Secure token-based auth with bcrypt password hashing
- **Role-Based Access Control**: Admin, user, and read-only roles
- **User Management**: Create, update, delete users
- **API Key Management**: Generate and revoke API keys
- **Health Monitoring**: `/api/v1/health` endpoint

### API Endpoints

The admin API provides 29 REST endpoints:

```
GET    /api/v1/health          # Health check
POST   /api/v1/auth/login      # User login
POST   /api/v1/auth/logout     # User logout
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get user
PUT    /api/v1/users/{id}      # Update user
DELETE /api/v1/users/{id}      # Delete user
# ... and more
```

### Frontend Dashboard

A React-based frontend is included in `frontend/`:

```bash
cd frontend
npm install
npm run dev      # Development server on port 5173
npm run build    # Production build
```

---

## Feature Flags

Control which features are enabled using environment variables.

### Presets

| Preset | Features |
|--------|----------|
| `full` (default) | All features enabled |
| `standard` | Orchestrator, Sheriff, Gauntlet |
| `minimal` | Core Orchestrator only |

```bash
LATTICE_FEATURE_PRESET=standard
```

### Granular Control

Disable specific features:

```bash
LATTICE_DISABLED_FEATURES=sheriff,consensus,mcp
```

Available feature flags:
- `sheriff` - Static analysis
- `gauntlet` - Test generation
- `feedback` - User feedback collection
- `rollback` - Transaction rollback system
- `consensus` - Multi-model voting
- `mcp` - Model Context Protocol

---

## Project Structure

```
lattice-lock-framework/
├── src/lattice_lock/           # Core Python package
│   ├── orchestrator/           # Model routing & selection (8 providers)
│   ├── sheriff/                # Static analysis engine (AST-based)
│   ├── gauntlet/               # Runtime test generation
│   ├── consensus/              # Multi-model voting engine
│   ├── cli/                    # Click-based CLI
│   ├── admin/                  # FastAPI admin dashboard
│   ├── dashboard/              # WebSocket monitoring
│   ├── database/               # SQLAlchemy repository pattern
│   ├── agents/                 # Agent definitions & templates
│   ├── config/                 # Feature flags & app config
│   ├── mcp/                    # Model Context Protocol
│   └── utils/                  # Utility functions
│
├── frontend/                   # React + Vite dashboard
├── tests/                      # Test suite (87 files)
├── docs/                       # Documentation (30+ guides)
├── agents/                     # AI agent definitions (90+)
├── scripts/                    # Automation scripts
└── infrastructure/             # Deployment configs
```

---

## Development

### Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# All tests
make test

# Quick tests only
make test-quick

# With coverage
pytest tests/ --cov=src/lattice_lock --cov-report=html

# Specific test file
pytest tests/core/test_feedback.py
```

### Code Quality

```bash
# Run all linters
make lint

# Auto-format code
make format

# Type checking
make type-check

# Full CI check
make ci
```

### Make Targets

| Target | Description |
|--------|-------------|
| `make lint` | Run Ruff, Black, MyPy, Lattice Validate |
| `make format` | Auto-format with Black and Ruff |
| `make test` | Run unit tests |
| `make test-quick` | Run critical tests only |
| `make type-check` | Static type checking |
| `make ci` | Full CI (lint, type-check, test) |
| `make deps` | Update dependencies |
| `make clean` | Remove build artifacts |
| `make pre-commit` | Run all pre-commit checks |

### Code Standards

- **File Naming**: `lowercase_with_underscores.py`
- **Class Names**: `PascalCase`
- **Formatting**: Black (100 char line length)
- **Linting**: Ruff + Pylint
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the complete coding standards (single source of truth).

---

## Documentation

Documentation is organized in the `docs/` directory:

| Directory | Content |
|-----------|---------|
| [docs/guides/](docs/guides/) | 29 tutorial guides covering all features |
| [docs/architecture/](docs/architecture/) | System design and architecture docs |
| [docs/reference/](docs/reference/) | API reference documentation |
| [docs/examples/](docs/examples/) | Example projects and code samples |
| [docs/testing/](docs/testing/) | Testing guides and strategies |

### Key Guides

- [Installation Guide](docs/guides/installation.md) - Getting started
- [Governance Guide](docs/guides/governance.md) - End-to-end workflow
- [Model Orchestration](docs/guides/model_orchestration.md) - Using the orchestrator
- [Local Models Setup](docs/guides/local_models_setup.md) - Ollama configuration
- [Troubleshooting](docs/guides/troubleshooting.md) - Common issues

---

## Contributing

We welcome contributions! Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) first - it is the **single source of truth** for all coding standards, naming conventions, and workflow requirements.

### Quick Contribution Checklist

1. Fork the repository
2. Create a branch: `your-name/feature-description`
3. Follow naming conventions (lowercase with underscores)
4. Add tests for new features
5. Run `make ci` to verify all checks pass
6. Open a PR targeting `main`
7. Add required labels: type (`feat`, `fix`, etc.) + source (`human`, `llm`, `devin`)

### Git Workflow

- **Single permanent branch**: `main`
- **Merge strategy**: Squash-and-merge only
- **CI Requirements**: Tests, lint, and typecheck must pass
- **Review**: `@greptileai` is auto-assigned

---

## Support

- **Issues**: [GitHub Issues](https://github.com/klappe-pm/lattice-lock-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/klappe-pm/lattice-lock-framework/discussions)
- **Documentation**: [docs/](docs/)

---

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

---

## Acknowledgments

Lattice Lock Framework is built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Admin API
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [httpx](https://www.python-httpx.org/) - Async HTTP client

---

<p align="center">
  <strong>Built for humans and AI agents working in perfect sync.</strong>
</p>
