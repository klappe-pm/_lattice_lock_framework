# Lattice Lock Framework: Feature Documentation

This document provides a comprehensive overview of the Lattice Lock Framework's features, integration points, and recommendations for developers.

## Overview

Lattice Lock is a governance-first framework for AI-assisted software development. It provides intelligent routing of development tasks to 63 AI models across 8 providers, automated prompt engineering, schema-driven code generation, and comprehensive governance through automated validation and rollback capabilities.

## Core Features

### 1. Model Orchestration System

The orchestration system intelligently routes AI requests to optimal models based on task analysis and capability scoring.

**Location**: `src/lattice_lock/orchestrator/`

**Key Components**:

The ModelOrchestrator class in `core.py` serves as the main entrypoint for AI requests. It coordinates with the ModelRegistry (managing 63 model definitions), TaskAnalyzer (extracting requirements from prompts), and ModelScorer (scoring models against task requirements).

The system supports 8 providers: OpenAI, Anthropic, Google, xAI, Azure, AWS Bedrock, DIAL, and Local (Ollama).

**Integration Points**:
- CLI: `lattice-lock orchestrator list|analyze|route`
- Python API: `ModelOrchestrator.route_request(prompt, task_type)`
- Configuration: `docs/models/registry.yaml` for model definitions
- Environment: Provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

**Usage Example**:
```python
from lattice_lock import ModelOrchestrator, TaskType

orchestrator = ModelOrchestrator()
response = orchestrator.route_request(
    prompt="Generate a Python function for...",
    task_type=TaskType.CODE_GENERATION
)
```

### 2. Prompt Architect Agent

Automates prompt generation, validation, and tracking for AI-assisted development workflows.

**Location**: `src/lattice_lock/agents/prompt_architect/`

**Key Components**:

The PromptGenerator provides multi-stage LLM-powered prompt creation with validation loops. The RoadmapParser analyzes WBS/Gantt/Kanban files for dependencies and critical paths (note: currently only WBS markdown format is fully implemented). The ConventionChecker validates filename patterns and placement. The TrackerClient provides a Python API for prompt state management.

**Integration Points**:
- CLI: `prompt-architect generate|validate|status`
- State File: `project_prompts/project_prompts_state.json`
- Python API: `TrackerClient` for programmatic access
- External: `ProjectAgentClient` for project discovery

**Usage Example**:
```bash
# Generate prompts from specification
prompt-architect generate my-project --phase 1 --output project_prompts/

# Track prompt execution
python scripts/prompt_tracker.py next --tool devin
python scripts/prompt_tracker.py update --id 1.1.1 --done
```

### 3. Schema Compilation System

Transforms `lattice.yaml` schemas into Pydantic models, SQLModel ORMs, and Gauntlet test contracts.

**Location**: `src/lattice_lock/compile.py`

**Key Components**:

The `compile_lattice()` function is the main compiler entrypoint. It produces a CompilationResult containing generated files, warnings, and errors. The system includes meta-policy validation for enforcing architectural standards.

**Generated Artifacts**:
- `types_generated_pydantic.py` - Request/response validation models
- `types_generated_sqlmodel.py` - Database ORM classes
- `tests/gauntlet/test_contract_*.py` - Business rule tests

**Integration Points**:
- CLI: `lattice-lock compile`
- Python API: `compile_lattice(schema_path, generate_pydantic=True, ...)`
- Input: `lattice.yaml` schema definition file

**Usage Example**:
```python
from lattice_lock import compile_lattice

result = compile_lattice(
    schema_path="lattice.yaml",
    generate_pydantic=True,
    generate_sqlmodel=True,
    generate_gauntlet=True
)
```

### 4. Governance System

Validates code quality and enforces semantic contracts through Sheriff (AST validation) and Gauntlet (semantic testing).

**Location**: `src/lattice_lock/sheriff.py`, `src/lattice_lock_gauntlet/`

**Sheriff Features**:
- Import discipline enforcement
- Type hint compliance checking
- Naming convention validation
- GitHub Action integration (`.github/actions/sheriff/`)

**Gauntlet Features**:
- Test generation from `lattice.yaml` constraints
- Business rule validation ("ensures" clauses)
- Parallel execution support with pytest-xdist

**Integration Points**:
- CLI: `lattice-lock sheriff`, `lattice-lock gauntlet`
- CI/CD: GitHub Actions workflow integration
- Python API: `run_sheriff(path="src/")`

### 5. Rollback System

Creates checkpoints and reverts system state on validation failures.

**Location**: `src/lattice_lock/rollback/`

**Key Components**:

The RollbackTrigger orchestrates rollback operations with pre/post hooks. The CheckpointManager creates and restores file snapshots with SHA256 hash validation. The CheckpointStorage provides gzip JSON persistence.

**Trigger Conditions**:
- Sheriff violations
- Gauntlet test failures
- Manual triggers via API

**Integration Points**:
- Python API: `RollbackTrigger.trigger_rollback(reason, checkpoint_id, mode)`
- Hooks: `register_pre_rollback_hook()`, `register_post_rollback_hook()`
- Modes: `restore_checkpoint` (file restoration), `git_revert` (Git revert)

### 6. Admin Dashboard

Real-time monitoring via WebSocket-connected dashboard.

**Location**: `src/lattice_lock/admin/`, `src/lattice_lock/dashboard/`

**Features**:
- Live project status updates via WebSocket
- Metrics visualization (Chart.js)
- Alert management
- Validation and rollback triggers

**Integration Points**:
- CLI: `lattice-lock admin dashboard --port 8000`
- WebSocket: `/dashboard/live`
- REST API: FastAPI endpoints for health/monitoring
- Authentication: JWT tokens + API keys with RBAC (ADMIN/OPERATOR/VIEWER)

### 7. Infrastructure Services

**Logging** (`src/lattice_lock/logging_config.py`):
- Centralized configuration with `setup_logging()`
- Automatic trace ID injection via `TraceIdFilter`
- Sensitive data redaction via `SensitiveDataFilter`
- Multiple output formats: JSON, console, simple

**Tracing** (`src/lattice_lock/tracing.py`):
- Distributed tracing with `@traced` decorator
- Performance monitoring with `@timed` decorator
- ContextVar-based span management (async-safe)

**Error Handling** (`src/lattice_lock/errors/middleware.py`):
- `@error_boundary` decorator with retry logic
- Exponential backoff with jitter
- Fallback execution support
- Error classification and metrics

**Feedback Collection** (`src/lattice_lock/feedback/`):
- Structured feedback with categories (BUG/FEATURE/QUALITY)
- JSON persistence
- CLI: `lattice-lock feedback`

## Code Quality Recommendations

Based on the comprehensive code review, the following recommendations are provided for improving code quality:

### High Priority

1. **Exception Handling**: The codebase contains 18+ bare `except Exception:` blocks that swallow errors without proper handling. Consider:
   - Logging the exception before suppressing
   - Using more specific exception types
   - Re-raising after logging when appropriate

2. **Type Annotations**: There are 30+ uses of `Any` type annotation. While some are legitimate (e.g., JSON data), others could be replaced with more specific types:
   - `rollback/trigger.py:24` - Uses `Any` for `checkpoint_manager` parameter
   - Consider using Protocol or ABC for better type safety

3. **Generated Files**: The `src/generated/types.py` file contains undefined names (`uuid`, `decimal`, `enum`). This appears to be a generated artifact that should either:
   - Be regenerated with proper imports
   - Be moved to `examples/` if it's just a sample
   - Be excluded from linting if it's expected to be regenerated

### Medium Priority

4. **ConsensusEngine Mock Logic**: The `orchestrator/consensus/engine.py` uses deterministic random seeding for mock responses. Consider:
   - Refactoring to accept an injected query function
   - Documenting it as "planned" functionality
   - Adding a clear warning when used in production

5. **Database Health Metrics**: The `database/health.py` returns placeholder values for `latency_ms` and `connections_in_pool`. Consider:
   - Implementing actual timing measurements
   - Querying connection pool statistics from SQLAlchemy

6. **Admin Dashboard CLI**: The `cli/groups/admin.py` dashboard command prints a message but doesn't actually launch uvicorn. Consider:
   - Implementing actual uvicorn launch
   - Adding proper error handling for port conflicts

### Low Priority (Style)

7. **Line Length**: 169 lines exceed the configured line length limit. While Black handles most formatting, some manual intervention may be needed for complex expressions.

8. **Mixed Spaces and Tabs**: 8 files have mixed indentation. Running `ruff --fix` with appropriate rules can resolve most of these.

## Integration Architecture


## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key | For OpenAI models |
| ANTHROPIC_API_KEY | Anthropic API key | For Claude models |
| GOOGLE_API_KEY | Google API key | For Gemini models |
| XAI_API_KEY | xAI API key | For Grok models |
| AZURE_OPENAI_API_KEY | Azure OpenAI key | For Azure models |
| AZURE_OPENAI_ENDPOINT | Azure endpoint URL | For Azure models |
| AWS_ACCESS_KEY_ID | AWS access key | For Bedrock models |
| AWS_SECRET_ACCESS_KEY | AWS secret key | For Bedrock models |
| DIAL_URL | DIAL service URL | For DIAL models |
| LATTICE_DATABASE_URL | Database connection URL | For admin features |
| DATABASE_URL | Alternative DB URL | For admin features |

## Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run linting
pre-commit run --all-files

# Run tests
python -m pytest -m "not integration" --tb=short

# Run specific test file
python -m pytest tests/test_compile.py -v
```

## CI/CD Integration

The framework includes GitHub Actions workflows for:

1. **CI Pipeline** (`.github/workflows/ci.yml`):
   - Ruff linting
   - Black format check
   - Governance checks
   - Unit tests with coverage

2. **Sheriff Action** (`.github/actions/sheriff/`):
   - Custom GitHub Action for AST validation
   - Configurable output formats
   - Caching support

3. **Release Workflow** (`.github/workflows/release.yml`):
   - Triggered on version tags
   - Builds and publishes to PyPI

## Version History

- **v2.1.0** (Current): Governance-first framework with model orchestration
- **v2.0.0**: Major refactor with prompt architect agent
- **v1.x**: Original Vibelocity Orchestrator implementation

## Related Documentation

- [README.md](scripts/README.md) - Project overview and quick start
- [AGENT_SPECIFICATION_v2.1.md](../AGENT_SPECIFICATION_v2.1.md) - Agent specification details
- [docs/getting_started/](getting_started/) - Quick start guides
- [docs/design/](design/) - Design documents
