# Technology Stack Inventory

## Project Identity

**Project Name:** Lattice Lock Framework  
**Version:** 2.1.0  
**License:** MIT  
**Repository:** https://github.com/klappe-pm/lattice-lock-framework

### Project Type Classification
- **Primary:** Python Library/Framework with CLI
- **Secondary:** FastAPI REST API
- **Tertiary:** React Dashboard (frontend/)

### Primary Purpose and Target Users
Lattice Lock is a governance-first framework for AI-assisted software development that provides intelligent orchestration of Large Language Models (LLMs). Target users include development teams enforcing architectural policies, AI model users routing requests across multiple providers, and AI-assisted development workflows.

### Maturity Assessment
**Status:** Beta/Production (Development Status :: 4 - Beta)

The framework is feature-complete for core functionality (Sheriff, Gauntlet, Orchestrator) but has some quality issues that need addressing before full production readiness.

## Languages

| Language | Percentage | Files | Lines of Code | Primary Use |
|----------|------------|-------|---------------|-------------|
| Python | ~60% | 342 | 29,323 (src/) + 16,323 (tests/) | Core framework, CLI, API |
| JavaScript/JSX | ~10% | 3,457 | 5,029 | Frontend dashboard |
| YAML | ~5% | 176 | N/A | Configuration, CI/CD, model definitions |
| Markdown | ~20% | 636 | N/A | Documentation |
| HCL (Terraform) | ~2% | 10 | ~500 | Infrastructure as Code |
| JSON | ~3% | 616 | N/A | Configuration, package manifests |

## Frameworks

### Backend
| Framework | Version | Purpose | Location |
|-----------|---------|---------|----------|
| FastAPI | >=0.100.0 | REST API framework | `src/lattice_lock/admin/` |
| Pydantic | >=2.0.0 | Data validation and serialization | Throughout |
| SQLAlchemy | >=2.0.0 | ORM and database abstraction | `src/lattice_lock/admin/models.py` |
| Click | >=8.0.0 | CLI framework | `src/lattice_lock/cli/` |
| Jinja2 | >=3.1.0 | Template rendering | `src/lattice_lock/utils/jinja.py` |
| MCP | >=0.1.0 | Model Context Protocol server | `src/lattice_lock/mcp/` |

### Frontend
| Framework | Version | Purpose | Location |
|-----------|---------|---------|----------|
| React | ^19.2.0 | UI framework | `frontend/src/` |
| React Router | ^7.11.0 | Client-side routing | `frontend/src/` |
| ReactFlow | ^11.11.4 | Flow diagram visualization | `frontend/src/` |
| Zustand | ^5.0.9 | State management | `frontend/src/store/` |
| MDUI | ^2.1.4 | Material Design UI components | `frontend/src/` |
| D3 | ^7.9.0 | Data visualization | `frontend/src/` |

### Testing
| Framework | Version | Purpose | Location |
|-----------|---------|---------|----------|
| pytest | >=7.4.0 | Python test framework | `tests/` |
| pytest-asyncio | >=0.21.0 | Async test support | `tests/` |
| pytest-cov | >=4.1.0 | Coverage reporting | `tests/` |
| pytest-benchmark | >=4.0.0 | Performance benchmarks | `tests/benchmarks/` |
| hypothesis | >=6.90.0 | Property-based testing | `tests/` |
| Vitest | ^4.0.16 | Frontend testing | `frontend/` |
| Testing Library | ^16.1.0 | React component testing | `frontend/` |

## Build Tools

### Python
| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| setuptools | >=61.0 | Package building | `pyproject.toml` |
| pip-tools | >=7.0.0 | Dependency locking | `requirements.in` -> `requirements.lock` |
| Black | >=23.0.0 | Code formatting | `pyproject.toml [tool.black]` |
| Ruff | >=0.1.0 | Linting | `pyproject.toml [tool.ruff]` |
| isort | >=5.12.0 | Import sorting | `pyproject.toml [tool.isort]` |
| MyPy | >=1.0.0 | Static type checking | `pyproject.toml` |

### Frontend
| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| Vite | ^7.2.4 | Build tool and dev server | `frontend/vite.config.js` |
| ESLint | ^9.39.1 | JavaScript linting | `frontend/eslint.config.js` |

## Package Managers

| Manager | Lock File | Purpose |
|---------|-----------|---------|
| pip | `requirements.lock` | Python dependencies |
| pip-tools | `requirements.in` | Dependency specification |
| npm | `frontend/package-lock.json` | Frontend dependencies |

## Runtime Environments

| Runtime | Version | Purpose |
|---------|---------|---------|
| Python | 3.10, 3.11, 3.12 | Backend runtime (requires-python = ">=3.10") |
| Node.js | 22.x | Frontend build and development |

## Infrastructure as Code

### Terraform
| Provider | Version | Location | Purpose |
|----------|---------|----------|---------|
| AWS | ~> 5.0 | `infrastructure/terraform/aws/` | AWS infrastructure |
| Google | ~> 5.0 | `infrastructure/terraform/gcp/` | GCP infrastructure |
| Google Beta | ~> 5.0 | `infrastructure/terraform/gcp/` | GCP beta features |

### AWS Resources (Defined)
- VPC and networking (`vpc.tf`)
- RDS/Database (`database.tf`)
- ElastiCache/Redis (`cache.tf`)
- CloudWatch monitoring (`monitoring.tf`)
- DynamoDB (`nosql.tf`)
- Kinesis Analytics (`analytics.tf`)

### GCP Resources (Defined)
- VPC Network and Subnets
- Cloud SQL (PostgreSQL 15)
- Firestore
- BigQuery (analytics tables)
- Memorystore (Redis 7.0)
- Cloud KMS (encryption keys)
- Secret Manager

## Containerization

### Docker
| File | Purpose |
|------|---------|
| `Dockerfile` | Production container image (Python 3.12-slim) |
| `docker-compose.yml` | Local development orchestration |

**Dockerfile Details:**
- Base image: `python:3.12-slim`
- Exposes port: 8080
- Runs as non-root user: `lattice`
- Entry point: `uvicorn lattice_lock.admin.api:app`

## CI/CD Platforms

### GitHub Actions
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push/PR to main | Main CI pipeline (policy, quality, test) |
| `release.yml` | Tags v* | PyPI publishing |
| `docker-publish.yml` | Tags v* | Docker image publishing to GHCR |
| `snyk-security.yml` | Push/PR to main | Security scanning |
| `check-untracked.yml` | Push/PR to main | Untracked files check |
| `reusable-full-check.yml` | Workflow call | Combined validation |
| `reusable-validate.yml` | Workflow call | Schema validation |
| `reusable-sheriff.yml` | Workflow call | Static analysis |
| `reusable-gauntlet.yml` | Workflow call | Contract testing |

## External Services

### LLM Providers (Supported)
| Provider | Models | Configuration |
|----------|--------|---------------|
| OpenAI | o1-pro, gpt-4o, gpt-4o-mini, o1-mini | `OPENAI_API_KEY` |
| Anthropic | claude-4-5-sonnet, claude-4-sonnet, claude-3-7-sonnet, claude-3-5-haiku | `ANTHROPIC_API_KEY` |
| Google | gemini-2.5-pro, gemini-2.5-flash | `GOOGLE_API_KEY` |
| xAI | grok-4-fast-reasoning, grok-code-fast-1, grok-3 | `XAI_API_KEY` |
| AWS Bedrock | bedrock-claude-3-opus, bedrock-llama-3.1-* | AWS credentials |
| Azure OpenAI | azure-gpt-4o, azure-gpt-4-turbo | `AZURE_OPENAI_KEY` |
| Ollama (Local) | qwen3-next-80b, deepseek-r1:70b, glm4, codellama:34b | `OLLAMA_HOST` |

### Security Services
| Service | Purpose | Configuration |
|---------|---------|---------------|
| Snyk | Vulnerability scanning | `SNYK_TOKEN` |
| Bandit | Python security linting | CI pipeline |

## Database Technologies

| Database | Type | Purpose | Configuration |
|----------|------|---------|---------------|
| SQLite | Relational | Default local database | `DATABASE_URL=sqlite:///lattice.db` |
| PostgreSQL | Relational | Production database (GCP Cloud SQL) | Terraform |
| Firestore | Document | Session storage (GCP) | Terraform |
| BigQuery | Analytics | Request logs, audit events | Terraform |
| Redis | Cache | Response caching | Terraform (Memorystore) |

## Configuration Files Summary

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python package configuration, tool settings |
| `.env.example` | Environment variable template |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |
| `Makefile` | Build automation commands |
| `.github/CODEOWNERS` | Code review assignment |
| `lattice.yaml` | Governance rules (if present) |
| `src/lattice_lock/orchestrator/models.yaml` | Model registry |
| `src/lattice_lock/orchestrator/scorer_config.yaml` | Scoring configuration |
