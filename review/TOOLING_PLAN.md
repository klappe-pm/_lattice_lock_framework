# Tooling Plan

## Lattice Lock Framework - Linting, IDE Setup, and Pre-commit Recommendations

This document outlines the current tooling configuration, identified issues, and recommended improvements for code quality tooling.

## Current State

### Linting Tools

| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| Ruff | >=0.1.0 | Fast Python linter | `pyproject.toml [tool.ruff]` |
| Black | >=23.0.0 | Code formatter | `pyproject.toml [tool.black]` |
| isort | >=5.12.0 | Import sorter | `pyproject.toml [tool.isort]` |
| MyPy | >=1.0.0 | Static type checker | `pyproject.toml` |
| Pylint | >=3.0.0 | Additional linting | `pyproject.toml` |
| Bandit | - | Security linting | CI pipeline |
| ESLint | ^9.39.1 | JavaScript linting | `frontend/eslint.config.js` |

### Current Configuration

**Ruff (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM"]
ignore = ["E501"]  # Line length handled by formatter
```

**Black (`pyproject.toml`):**
```toml
[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]
```

**isort (`pyproject.toml`):**
```toml
[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["lattice_lock"]
```

**MyPy (`pyproject.toml`):**
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

### Pre-commit Hooks

**Location:** `.pre-commit-config.yaml`

**Current Hooks:**
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files
- check-merge-conflict
- check-case-conflict
- detect-private-key
- Black formatter
- isort import sorter
- Ruff linter
- Local Lattice Lock structure checks

## Identified Issues

### Issue 1: 125 Lint Errors (P1)

**Current State:**
```
W293 blank-line-with-whitespace: 69
UP006 non-pep585-annotation: 17
F401 unused-import: 13
UP035 deprecated-import: 10
I001 unsorted-imports: 9
W291 trailing-whitespace: 4
W292 missing-newline-at-end-of-file: 2
UP015 redundant-open-modes: 1
```

**Fix:**
```bash
# Auto-fix 107 errors
ruff check . --fix

# Format code
black .
isort .

# Verify
ruff check .
```

### Issue 2: 99 Type Errors (P1)

**Current State:** MyPy reports 99 errors across 40 files

**Top Error Categories:**
- Incompatible return types
- Missing type annotations
- Union type attribute access
- Async context manager types

**Fix Strategy:**
1. Fix critical errors in core modules first
2. Add type stubs for missing packages
3. Use `# type: ignore` sparingly with comments

### Issue 3: Bandit Failures Ignored (P2)

**Location:** `.github/workflows/ci.yml:78`

**Current:**
```yaml
run: bandit -r src/lattice_lock -c pyproject.toml || true
```

**Fix:**
```yaml
run: bandit -r src/lattice_lock -c pyproject.toml
```

### Issue 4: Missing Type Stubs (P3)

**Missing stubs for:**
- `mcp`
- `aiofiles`
- Custom packages

**Fix:**
```bash
pip install types-aiofiles
# For mcp, add to pyproject.toml:
# [[tool.mypy.overrides]]
# module = "mcp.*"
# ignore_missing_imports = true
```

## Recommended Configuration Updates

### 1. Enhanced Ruff Configuration

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
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "W",      # pycodestyle warnings
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "S",      # flake8-bandit (security)
    "A",      # flake8-builtins
    "COM",    # flake8-commas
    "DTZ",    # flake8-datetimez
    "T10",    # flake8-debugger
    "EXE",    # flake8-executable
    "ISC",    # flake8-implicit-str-concat
    "ICN",    # flake8-import-conventions
    "G",      # flake8-logging-format
    "INP",    # flake8-no-pep420
    "PIE",    # flake8-pie
    "T20",    # flake8-print
    "PYI",    # flake8-pyi
    "PT",     # flake8-pytest-style
    "Q",      # flake8-quotes
    "RSE",    # flake8-raise
    "RET",    # flake8-return
    "SLF",    # flake8-self
    "SLOT",   # flake8-slots
    "TID",    # flake8-tidy-imports
    "TCH",    # flake8-type-checking
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate
    "PL",     # pylint
    "TRY",    # tryceratops
    "FLY",    # flynt
    "PERF",   # perflint
    "RUF",    # ruff-specific
]
ignore = [
    "E501",   # Line length (handled by formatter)
    "S101",   # Assert usage (OK in tests)
    "PLR0913", # Too many arguments
    "TRY003", # Long exception messages
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG", "PLR2004"]
"scripts/**/*.py" = ["T20"]  # Allow print in scripts

[tool.ruff.lint.isort]
known-first-party = ["lattice_lock"]
```

### 2. Enhanced MyPy Configuration

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_equality = true
strict_concatenate = true
check_untyped_defs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
show_error_codes = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = [
    "mcp.*",
    "aiofiles.*",
    "uvicorn.*",
]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### 3. Enhanced Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  # Standard hooks
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

  # Black formatter
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.10
        args: [--config=pyproject.toml]

  # isort import sorter
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--settings-path=pyproject.toml]

  # Ruff linter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  # MyPy type checker
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

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: [-c, pyproject.toml, -r, src/lattice_lock]
        additional_dependencies: ["bandit[toml]"]

  # Local hooks
  - repo: local
    hooks:
      - id: check-generated-files
        name: Check generated files not committed
        entry: bash -c 'git diff --cached --name-only | grep -q "^src/generated/" && echo "Error: Do not commit generated files" && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: lattice-naming-check
        name: Check naming conventions
        entry: python scripts/check_naming.py
        language: python
        types: [python]
```

## IDE Setup Recommendations

### VS Code

**`.vscode/settings.json`:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  
  "ruff.enable": true,
  "ruff.lint.run": "onSave",
  "ruff.format.args": ["--config=pyproject.toml"],
  
  "mypy-type-checker.args": ["--config-file=pyproject.toml"],
  
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/src/generated": true
  },
  
  "editor.rulers": [100],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

**`.vscode/extensions.json`:**
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

### PyCharm

**Recommended Settings:**
1. Enable Black formatter: Settings > Tools > Black
2. Enable Ruff: Settings > Tools > External Tools
3. Enable MyPy: Settings > Editor > Inspections > Python > Type checker
4. Set line length to 100: Settings > Editor > Code Style > Python

### Cursor/AI IDEs

**`.cursorrules` or similar:**
```
# Lattice Lock Framework Coding Standards

## Python Style
- Use Black formatting with 100 character line length
- Use isort for import sorting with "black" profile
- Follow PEP 8 naming conventions
- Use type hints for all function signatures

## File Organization
- Use snake_case for all file names
- Place tests in tests/ mirroring src/ structure
- Generated files go in src/generated/ (not committed)

## Code Quality
- All functions must have return type annotations
- Use Pydantic for data validation
- Use SQLAlchemy for database operations
- Use httpx for HTTP requests

## Testing
- Write pytest tests for all new code
- Maintain 70% minimum coverage
- Use pytest-asyncio for async tests
```

## Implementation Roadmap

### Phase 1: Fix Current Issues (1 day)
1. Run `ruff check . --fix` to auto-fix 107 errors
2. Run `black .` and `isort .` to format code
3. Fix remaining 18 manual lint errors
4. Commit fixes

### Phase 2: Fix Type Errors (2-3 days)
5. Fix critical type errors in core modules
6. Add type stubs for missing packages
7. Update MyPy configuration
8. Target: Reduce to <20 type errors

### Phase 3: Update Tooling (1 day)
9. Update Ruff configuration with enhanced rules
10. Update pre-commit configuration
11. Add IDE configuration files
12. Update CI to fail on Bandit errors

### Phase 4: Documentation (1 day)
13. Document tooling setup in CONTRIBUTING.md
14. Add IDE setup guide
15. Document pre-commit hook usage

## Quick Fix Commands

```bash
# Fix all auto-fixable lint errors
ruff check . --fix

# Format all Python files
black .
isort .

# Check for remaining issues
ruff check .
mypy src/lattice_lock

# Run all pre-commit hooks
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

## Verification Checklist

- [ ] `ruff check .` returns 0 errors
- [ ] `black --check .` returns 0 errors
- [ ] `isort --check .` returns 0 errors
- [ ] `mypy src/lattice_lock` returns <20 errors
- [ ] `bandit -r src/lattice_lock` returns 0 high-severity issues
- [ ] `pre-commit run --all-files` passes
- [ ] IDE configuration files added
- [ ] CI fails on lint/type errors (no `|| true`)
