# Code Changes Backlog

## Lattice Lock Framework - Consolidated Remediation Plan

This document consolidates all code change recommendations from the comprehensive framework review. Issues are organized by priority and domain.

---

## Priority Legend

| Priority | Meaning | SLA |
|----------|---------|-----|
| **P0** | Critical - Security/data risk | Immediate |
| **P1** | High - Core functionality blocked | 1-2 days |
| **P2** | Medium - Quality/reliability impact | 1 week |
| **P3** | Low - Technical debt | 2 weeks |
| **P4** | Backlog - Nice to have | As time permits |

---

## P0 - Critical Issues (2)

### P0-1: Database Connection Manager Type Errors

**Location:** `src/lattice_lock/utils/database.py:45-89`

**Problem:** 99 MyPy type errors, 12 in database module. Async context manager returns incompatible types.

**Fix:**
```python
# Current (broken)
async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
    async with self.session_factory() as session:
        yield session

# Fixed
from typing import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session(self) -> AsyncIterator[AsyncSession]:
    async with self.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Verification:**
```bash
mypy src/lattice_lock/utils/database.py --strict
```

---

### P0-2: Test Failures in CI

**Location:** `.github/workflows/ci.yml`, `tests/`

**Problem:** 10 tests failing, coverage at 67% (below 70% threshold)

**Failing Tests:**
1. `test_sheriff_analyzer.py::test_analyze_complex_patterns` - Timeout
2. `test_gauntlet_runner.py::test_contract_validation` - Assertion error
3. `test_orchestrator_routing.py::test_model_selection` - Mock issue
4. `test_admin_api.py::test_project_creation` - Database fixture
5. `test_consensus_engine.py::test_majority_voting` - Race condition
6. Plus 5 more related failures

**Fix Strategy:**
1. Fix test fixtures for database tests
2. Add proper async mocking
3. Increase test timeout for complex operations
4. Fix race condition in consensus tests

**Verification:**
```bash
pytest tests/ -v --tb=short
pytest --cov=src/lattice_lock --cov-report=term-missing --cov-fail-under=70
```

---

## P1 - High Priority Issues (4)

### P1-1: 125 Lint Errors

**Location:** Multiple files across `src/lattice_lock/`

**Breakdown:**
| Error Type | Count | Auto-fixable |
|------------|-------|--------------|
| W293 blank-line-with-whitespace | 69 | Yes |
| UP006 non-pep585-annotation | 17 | Yes |
| F401 unused-import | 13 | Yes |
| UP035 deprecated-import | 10 | Yes |
| I001 unsorted-imports | 9 | Yes |
| W291 trailing-whitespace | 4 | Yes |
| W292 missing-newline-at-end-of-file | 2 | Yes |
| UP015 redundant-open-modes | 1 | Yes |

**Fix:**
```bash
# Auto-fix 107 errors
ruff check . --fix

# Format code
black .
isort .

# Verify remaining
ruff check .
```

---

### P1-2: 99 Type Errors (MyPy)

**Location:** 40 files across `src/lattice_lock/`

**Top Error Categories:**
- Incompatible return types (28)
- Missing type annotations (24)
- Union type attribute access (19)
- Async context manager types (15)
- Generic type issues (13)

**Priority Files:**
1. `src/lattice_lock/utils/database.py` - 12 errors
2. `src/lattice_lock/orchestrator/router.py` - 9 errors
3. `src/lattice_lock/providers/bedrock.py` - 8 errors
4. `src/lattice_lock/admin/api.py` - 7 errors
5. `src/lattice_lock/consensus/engine.py` - 6 errors

**Fix Strategy:**
1. Fix database module types (P0 dependency)
2. Add type stubs for missing packages
3. Fix provider return types
4. Use `# type: ignore[specific-error]` sparingly

---

### P1-3: Bedrock Provider Type Errors

**Location:** `src/lattice_lock/providers/bedrock.py:78-156`

**Problem:** 8 type errors due to boto3 response typing

**Fix:**
```python
# Add type definitions
from typing import TypedDict, Any

class BedrockResponse(TypedDict):
    body: Any
    contentType: str

class BedrockMessageContent(TypedDict):
    text: str

# Update method signatures
async def invoke_model(
    self,
    model_id: str,
    messages: list[dict[str, Any]],
    **kwargs: Any
) -> BedrockResponse:
    ...
```

---

### P1-4: Frontend npm Dependency Conflicts

**Location:** `frontend/package.json`

**Problem:** npm audit shows 3 high vulnerabilities, peer dependency conflicts

**Current Issues:**
- `@vitejs/plugin-react` version mismatch
- `eslint-plugin-react-hooks` peer dependency warning
- 3 high severity vulnerabilities in transitive dependencies

**Fix:**
```bash
cd frontend

# Update package.json
npm install @vitejs/plugin-react@latest
npm install eslint-plugin-react-hooks@latest --save-dev

# Fix vulnerabilities
npm audit fix

# If needed, force resolution
npm install --legacy-peer-deps
```

---

## P2 - Medium Priority Issues (4)

### P2-1: Bandit Security Scan Ignored in CI

**Location:** `.github/workflows/ci.yml:78`

**Current:**
```yaml
run: bandit -r src/lattice_lock -c pyproject.toml || true
```

**Fix:**
```yaml
run: bandit -r src/lattice_lock -c pyproject.toml
```

---

### P2-2: CI/CD Actions Not Pinned to SHA

**Location:** `.github/workflows/ci.yml`

**Current:**
```yaml
uses: actions/checkout@v4
uses: actions/setup-python@v5
```

**Fix:**
```yaml
# Pin to specific SHA for security
uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
uses: actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d  # v5.1.0
```

---

### P2-3: Missing Frontend CI Job

**Location:** `.github/workflows/ci.yml`

**Problem:** No CI job for frontend linting/testing

**Add:**
```yaml
frontend:
  runs-on: ubuntu-latest
  defaults:
    run:
      working-directory: frontend
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    - run: npm ci
    - run: npm run lint
    - run: npm run type-check
    - run: npm run test -- --run
    - run: npm run build
```

---

### P2-4: Missing CI Concurrency Control

**Location:** `.github/workflows/ci.yml`

**Add at top level:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## P3 - Low Priority Issues (5)

### P3-1: Unused Dependencies

**Location:** `pyproject.toml`

**Dependencies to Remove:**
| Package | Reason |
|---------|--------|
| `tenacity` | Not imported anywhere |
| `python-multipart` | FastAPI handles this |
| `aiosqlite` | Using asyncpg instead |

**Fix:**
```bash
# Remove from pyproject.toml
pip uninstall tenacity python-multipart aiosqlite
```

---

### P3-2: Missing Type Stubs

**Location:** `pyproject.toml`

**Add to dev dependencies:**
```toml
[project.optional-dependencies]
dev = [
    # ... existing
    "types-aiofiles>=23.2.0",
    "types-PyYAML>=6.0.0",
    "types-requests>=2.31.0",
]
```

**Add MyPy overrides:**
```toml
[[tool.mypy.overrides]]
module = ["mcp.*", "uvicorn.*"]
ignore_missing_imports = true
```

---

### P3-3: Generated Files Not in .gitignore

**Location:** `.gitignore`

**Add:**
```gitignore
# Generated files
src/generated/
*.generated.py
*.generated.ts

# IDE
.vscode/
.idea/
*.code-workspace

# Coverage
htmlcov/
.coverage.*
```

---

### P3-4: Example Files in Wrong Location

**Location:** Various `src/lattice_lock/` subdirectories

**Files to Move:**
```
src/lattice_lock/examples/ → examples/
src/lattice_lock/scripts/ → scripts/
```

---

### P3-5: Missing Database Migrations

**Location:** `src/lattice_lock/utils/database.py`

**Problem:** No Alembic migration system configured

**Setup:**
```bash
# Initialize Alembic
alembic init migrations

# Configure alembic.ini
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/lattice_lock

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

---

## P4 - Backlog Issues (4)

### P4-1: Add GCP Vertex AI Provider

**Location:** `src/lattice_lock/providers/`

**Create:** `src/lattice_lock/providers/vertex.py`

```python
"""Google Cloud Vertex AI provider implementation."""
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import PredictionServiceClient

class VertexAIProvider(BaseProvider):
    """Vertex AI provider for Gemini models."""

    provider_name = "vertex"
    supported_models = ["gemini-1.5-pro", "gemini-1.5-flash"]

    async def chat(
        self,
        messages: list[Message],
        model: str = "gemini-1.5-pro",
        **kwargs: Any
    ) -> ChatResponse:
        ...
```

**Dependencies to Add:**
```toml
"google-cloud-aiplatform>=1.38.0",
"google-auth>=2.23.0",
```

---

### P4-2: Add Redis Caching Layer

**Location:** `src/lattice_lock/cache/`

**Create:** `src/lattice_lock/cache/redis_cache.py`

```python
"""Redis-based caching for LLM responses."""
import redis.asyncio as redis

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.client = redis.from_url(url)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        await self.client.setex(key, ttl, value)
```

**Dependencies to Add:**
```toml
"redis>=5.0.0",
```

---

### P4-3: Add psutil for System Monitoring

**Location:** `src/lattice_lock/admin/`

**Dependencies to Add:**
```toml
"psutil>=5.9.0",
```

**Use Case:** Admin dashboard system metrics

---

### P4-4: Frontend Accessibility Improvements

**Location:** `frontend/src/components/`

**Recommendations:**
1. Add ARIA labels to all interactive elements
2. Implement keyboard navigation
3. Add focus indicators
4. Support reduced motion preferences
5. Add skip navigation link

---

## Tooling Configuration Updates

### Enhanced Ruff Configuration

**Location:** `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
exclude = [
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "src/generated",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E", "F", "W", "I", "UP", "B", "C4", "SIM",
    "S", "A", "COM", "DTZ", "T10", "EXE", "ISC",
    "ICN", "G", "INP", "PIE", "T20", "PYI", "PT",
    "Q", "RSE", "RET", "SLF", "SLOT", "TID", "TCH",
    "ARG", "PTH", "ERA", "PL", "TRY", "FLY", "PERF", "RUF",
]
ignore = ["E501", "S101", "PLR0913", "TRY003"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG", "PLR2004"]
"scripts/**/*.py" = ["T20"]
```

### Enhanced MyPy Configuration

**Location:** `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_equality = true
check_untyped_defs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
show_error_codes = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = ["mcp.*", "aiofiles.*", "uvicorn.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### Enhanced Pre-commit Configuration

**Location:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--unsafe]
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: detect-private-key
      - id: check-ast
      - id: check-json
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        args: [--config=pyproject.toml]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--settings-path=pyproject.toml]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-PyYAML
          - types-requests
          - types-aiofiles
          - pydantic>=2.0.0
        args: [--config-file=pyproject.toml]
        pass_filenames: false
        entry: mypy src/lattice_lock

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: [-c, pyproject.toml, -r, src/lattice_lock]
        additional_dependencies: ["bandit[toml]"]

  - repo: local
    hooks:
      - id: check-generated-files
        name: Check generated files not committed
        entry: bash -c 'git diff --cached --name-only | grep -q "^src/generated/" && echo "Error: Do not commit generated files" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

---

## IDE Configuration

### VS Code Settings

**Location:** `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "ruff.enable": true,
  "ruff.lint.run": "onSave",
  "mypy-type-checker.args": ["--config-file=pyproject.toml"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/src/generated": true
  },
  "editor.rulers": [100],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

### VS Code Extensions

**Location:** `.vscode/extensions.json`

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

---

## Quick Fix Commands

```bash
# === LINT FIXES ===
ruff check . --fix
black .
isort .
ruff check .

# === TYPE CHECKING ===
mypy src/lattice_lock --strict

# === TESTING ===
pytest tests/ -v --tb=short
pytest --cov=src/lattice_lock --cov-report=term-missing --cov-fail-under=70

# === SECURITY ===
bandit -r src/lattice_lock -c pyproject.toml

# === PRE-COMMIT ===
pre-commit run --all-files
pre-commit autoupdate

# === FRONTEND ===
cd frontend
npm ci
npm audit fix
npm run lint
npm run type-check
npm run test -- --run
```

---

## Verification Checklist

### P0 - Critical
- [ ] `mypy src/lattice_lock/utils/database.py` - 0 errors
- [ ] `pytest tests/` - All tests pass
- [ ] Coverage >= 70%

### P1 - High
- [ ] `ruff check .` - 0 errors
- [ ] `mypy src/lattice_lock` - <20 errors
- [ ] Bedrock provider types fixed
- [ ] Frontend npm audit - 0 high vulnerabilities

### P2 - Medium
- [ ] Bandit runs without `|| true`
- [ ] CI actions pinned to SHA
- [ ] Frontend CI job added
- [ ] CI concurrency enabled

### P3 - Low
- [ ] Unused dependencies removed
- [ ] Type stubs added
- [ ] Generated files in .gitignore
- [ ] Example files moved
- [ ] Alembic migrations configured

### P4 - Backlog
- [ ] Vertex AI provider implemented
- [ ] Redis caching added
- [ ] psutil monitoring added
- [ ] Accessibility improvements complete

---

## Summary

| Priority | Count | Estimated Effort |
|----------|-------|------------------|
| P0 | 2 | 1-2 days |
| P1 | 4 | 2-3 days |
| P2 | 4 | 1-2 days |
| P3 | 5 | 2-3 days |
| P4 | 4 | 1-2 weeks |
| **Total** | **19** | **~2-3 weeks** |

---

*Consolidated from: ISSUE_BACKLOG.md, DEPENDENCY_PLAN.md, CLEANUP_PLAN.md, CICD_PLAN.md, LLM_INTEGRATION_PLAN.md, FRONTEND_PLAN.md, DATABASE_PLAN.md, TOOLING_PLAN.md*

*Generated: 2026-01-06*
