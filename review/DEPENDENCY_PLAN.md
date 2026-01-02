# Dependency Plan

## Lattice Lock Framework - Dependency Management Recommendations

This document outlines packages to remove, replace, upgrade, and add based on the comprehensive review.

## Summary

| Action | Count | Priority |
|--------|-------|----------|
| Remove | 3 | P2 |
| Add | 4 | P1 |
| Upgrade | 5 | P3 |
| Replace | 0 | - |
| Frontend Fix | 5 | P1 |

## Packages to Remove

### 1. tenacity
**Location:** `pyproject.toml:37`  
**Reason:** Not imported anywhere in codebase  
**Verification:** `grep -r "import tenacity" src/` returns no results  
**Risk:** Low - retry logic may be implemented differently  
**Action:**
```bash
# Remove from pyproject.toml dependencies section
# Then regenerate lock file
pip-compile requirements.in -o requirements.lock
```

### 2. python-multipart
**Location:** `pyproject.toml:44`  
**Reason:** Not imported anywhere in codebase  
**Verification:** `grep -r "import multipart" src/` returns no results  
**Risk:** Medium - FastAPI may use this for file uploads  
**Action:**
```bash
# Test file upload endpoints before removing
# If no file uploads exist, remove from pyproject.toml
```

### 3. aiosqlite
**Location:** `pyproject.toml:49`  
**Reason:** Not imported anywhere in codebase  
**Verification:** `grep -r "import aiosqlite" src/` returns no results  
**Risk:** Low - SQLAlchemy handles async SQLite differently  
**Action:**
```bash
# Remove from pyproject.toml dependencies section
```

## Packages to Add

### 1. psutil (Required)
**Location:** Missing from `pyproject.toml`  
**Used in:** `scripts/utilities/local_model_automation.py:9`  
**Purpose:** System monitoring for local model management  
**Action:**
```toml
# Add to pyproject.toml dependencies
dependencies = [
    # ... existing ...
    "psutil>=5.9.0",
]
```

### 2. google-cloud-firestore (Optional - GCP)
**Location:** Missing from `pyproject.toml`  
**Used in:** `src/database/gcp_clients.py:33`  
**Purpose:** GCP Firestore client  
**Action:**
```toml
# Add to pyproject.toml optional dependencies
[project.optional-dependencies]
gcp = [
    "google-cloud-firestore>=2.16.0",
    "google-cloud-bigquery>=3.14.0",
]
```

### 3. google-cloud-bigquery (Optional - GCP)
**Location:** Missing from `pyproject.toml`  
**Used in:** `src/database/gcp_clients.py:56`  
**Purpose:** GCP BigQuery client  
**Action:** See above (combined with firestore)

### 4. redis (Optional - Caching)
**Location:** Missing from `pyproject.toml`  
**Used in:** `src/database/gcp_clients.py:90`  
**Purpose:** Redis client for caching  
**Action:**
```toml
# Add to pyproject.toml optional dependencies
[project.optional-dependencies]
cache = [
    "redis>=5.0.0",
]
```

## Packages to Upgrade

### 1. httpx
**Current:** `>=0.25.0`  
**Recommended:** `>=0.27.0`  
**Reason:** Security patches, performance improvements  
**Risk:** Low - API stable

### 2. pydantic
**Current:** `>=2.0.0`  
**Recommended:** `>=2.6.0`  
**Reason:** Bug fixes, performance improvements  
**Risk:** Low - minor version

### 3. fastapi
**Current:** `>=0.100.0`  
**Recommended:** `>=0.109.0`  
**Reason:** Security patches, new features  
**Risk:** Low - API stable

### 4. sqlalchemy
**Current:** `>=2.0.0`  
**Recommended:** `>=2.0.25`  
**Reason:** Bug fixes, async improvements  
**Risk:** Low - patch version

### 5. rich
**Current:** `>=13.0.0`  
**Recommended:** `>=13.7.0`  
**Reason:** Bug fixes, new features  
**Risk:** Low - minor version

## Frontend Dependency Fixes

### Version Alignment Required

The following packages have version mismatches between `package.json` requirements and installed versions:

| Package | Required | Installed | Action |
|---------|----------|-----------|--------|
| vitest | ^4.0.16 | 2.1.9 | Downgrade requirement to ^2.1.9 |
| @vitest/coverage-v8 | ^4.0.16 | 2.1.9 | Downgrade requirement to ^2.1.9 |
| @vitest/ui | ^4.0.16 | 2.1.9 | Downgrade requirement to ^2.1.9 |
| globals | ^17.0.0 | 16.5.0 | Downgrade requirement to ^16.5.0 |
| jsdom | ^27.4.0 | 25.0.1 | Downgrade requirement to ^25.0.1 |

**Remediation:**
```bash
cd frontend
rm -rf node_modules package-lock.json
# Update package.json with correct versions
npm install
npm test
```

**Updated package.json devDependencies:**
```json
{
  "devDependencies": {
    "@vitest/coverage-v8": "^2.1.9",
    "@vitest/ui": "^2.1.9",
    "globals": "^16.5.0",
    "jsdom": "^25.0.1",
    "vitest": "^2.1.9"
  }
}
```

## Dependency Security Considerations

### Current Security Tooling
- Snyk integration in CI (`.github/workflows/snyk-security.yml`)
- Bandit for Python security scanning

### Recommended Additions
1. **pip-audit** - Python dependency vulnerability scanning
   ```bash
   pip install pip-audit
   pip-audit
   ```

2. **npm audit** - Already available, ensure it runs in CI
   ```bash
   cd frontend && npm audit
   ```

3. **Dependabot** - Automated dependency updates
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
     - package-ecosystem: "npm"
       directory: "/frontend"
       schedule:
         interval: "weekly"
     - package-ecosystem: "github-actions"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

## Implementation Order

### Phase 1: Critical Fixes (P1)
1. Add missing dependencies (psutil)
2. Fix frontend version conflicts
3. Regenerate lock files

### Phase 2: Cleanup (P2)
4. Remove unused dependencies
5. Add optional dependency groups (gcp, cache)

### Phase 3: Upgrades (P3)
6. Upgrade core dependencies
7. Add Dependabot configuration
8. Add pip-audit to CI

## Verification Steps

After implementing changes:

```bash
# Python dependencies
pip install -e ".[dev]"
pytest tests/ -v
mypy src/lattice_lock

# Frontend dependencies
cd frontend
npm install
npm test
npm run build

# Security scan
pip-audit
cd frontend && npm audit
```

## Updated pyproject.toml Dependencies Section

```toml
[project]
dependencies = [
    "httpx>=0.27.0",
    "pyyaml>=6.0",
    "rich>=13.7.0",
    "Jinja2>=3.1.0",
    "pydantic>=2.6.0",
    "click>=8.0.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.23.0",
    "mcp>=0.1.0",
    "defusedxml>=0.7.1",
    "aiofiles>=23.0.0",
    "bcrypt>=4.0.1",
    "PyJWT>=2.8.0",
    "sqlalchemy>=2.0.25",
    "psutil>=5.9.0",
]

[project.optional-dependencies]
gcp = [
    "google-cloud-firestore>=2.16.0",
    "google-cloud-bigquery>=3.14.0",
]
cache = [
    "redis>=5.0.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-benchmark>=4.0.0",
    "hypothesis>=6.90.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "pre-commit>=3.0.0",
    "pylint>=3.0.0",
    "mypy>=1.0.0",
    "types-PyYAML>=6.0.0",
    "types-requests>=2.31.0",
    "types-aiofiles>=23.0.0",
    "pip-tools>=7.0.0",
    "responses>=0.23.0",
    "mutmut>=2.4.0",
    "pip-audit>=2.6.0",
]
```
