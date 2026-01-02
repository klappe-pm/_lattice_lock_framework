# CI/CD Plan

## Lattice Lock Framework - CI/CD Pipeline Assessment and Recommendations

This document outlines the current CI/CD state, identified gaps, and recommended workflow improvements.

## Current State

### Workflow Inventory

| Workflow | File | Trigger | Purpose | Status |
|----------|------|---------|---------|--------|
| Production CI | `ci.yml` | push/PR to main | Main pipeline | Active |
| Release | `release.yml` | tags v* | PyPI publishing | Active |
| Docker Publish | `docker-publish.yml` | tags v* | GHCR publishing | Active |
| Snyk Security | `snyk-security.yml` | push/PR to main | Security scanning | Active |
| Check Untracked | `check-untracked.yml` | push/PR to main | File hygiene | Active |
| Full Check | `reusable-full-check.yml` | workflow_call | Combined validation | Reusable |
| Validate | `reusable-validate.yml` | workflow_call | Schema validation | Reusable |
| Sheriff | `reusable-sheriff.yml` | workflow_call | Static analysis | Reusable |
| Gauntlet | `reusable-gauntlet.yml` | workflow_call | Contract testing | Reusable |

### CI Pipeline Structure (`ci.yml`)

```
┌─────────────────────────────────────────────────────────────┐
│                    Production CI Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐                                                │
│  │ policy  │ (PR only)                                      │
│  │         │ - Validate PR targets main                     │
│  │         │ - Check scope label (feat/fix/chore/docs/refactor) │
│  │         │ - Check source label (human/llm/devin)         │
│  └────┬────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │ quality │ (matrix: Python 3.10, 3.11, 3.12)             │
│  │         │ - Install dependencies                         │
│  │         │ - Ruff lint check                              │
│  │         │ - Black format check                           │
│  │         │ - MyPy type check                              │
│  │         │ - Bandit security scan (failures ignored)      │
│  └────┬────┘                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐                                                │
│  │  test   │ (matrix: Python 3.10, 3.11, 3.12)             │
│  │         │ - pytest with coverage                         │
│  │         │ - 70% coverage threshold                       │
│  │         │ - Upload coverage to Codecov                   │
│  └─────────┘                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Current Strengths

1. **Multi-version Testing:** Tests run on Python 3.10, 3.11, and 3.12
2. **Policy Enforcement:** PR labels required for scope and source
3. **Reusable Workflows:** Well-designed reusable workflows for external consumption
4. **Security Integration:** Snyk scanning for SAST, SCA, and IaC
5. **Coverage Tracking:** Codecov integration with 70% threshold
6. **Docker Publishing:** Automated container builds on release

## Identified Gaps

### Gap 1: Actions Not Pinned to SHA
**Location:** All workflow files  
**Risk:** Supply chain attacks via compromised action versions  
**Current:**
```yaml
uses: actions/checkout@v6
uses: actions/setup-python@v6
```
**Recommended:**
```yaml
uses: actions/checkout@<sha>  # v6
uses: actions/setup-python@<sha>  # v6
```

### Gap 2: Bandit Failures Silently Ignored
**Location:** `.github/workflows/ci.yml:78`  
**Risk:** Security vulnerabilities go undetected  
**Current:**
```yaml
- name: Run Bandit security scan
  run: bandit -r src/lattice_lock -c pyproject.toml || true
```
**Recommended:**
```yaml
- name: Run Bandit security scan
  run: bandit -r src/lattice_lock -c pyproject.toml
```

### Gap 3: No Concurrency Controls
**Location:** `.github/workflows/ci.yml`  
**Risk:** Wasted CI resources on duplicate runs  
**Recommended:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Gap 4: No Dependency Caching
**Location:** `.github/workflows/ci.yml`  
**Risk:** Slow CI runs due to repeated dependency installation  
**Recommended:**
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.lock') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Gap 5: No Frontend CI
**Location:** Missing  
**Risk:** Frontend issues not caught before merge  
**Recommended:** Add frontend job to ci.yml

### Gap 6: No Dependabot Configuration
**Location:** Missing `.github/dependabot.yml`  
**Risk:** Dependencies become outdated, security vulnerabilities accumulate  

### Gap 7: No Branch Protection Documentation
**Location:** Missing  
**Risk:** Inconsistent enforcement of branch protection rules  

## Recommended Workflows

### 1. Enhanced CI Workflow

```yaml
# .github/workflows/ci.yml
name: Production CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  policy:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - name: Validate PR targets main and has required labels
        env:
          GITHUB_EVENT_PATH: ${{ github.event_path }}
        run: |
          # ... existing policy check script ...

  quality:
    needs: [policy]
    if: always() && (needs.policy.result == 'success' || needs.policy.result == 'skipped')
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@0a5c61591373683505ea898e09a3ea4f39ef2b9c  # v5.0.0
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache pip dependencies
        uses: actions/cache@0c45773b623bea8c8e75f6c82b208c3cf94ea4f9  # v4.0.2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('requirements.lock') }}
          restore-keys: |
            ${{ runner.os }}-pip-${{ matrix.python-version }}-
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.lock
          pip install -e ".[dev]"
      
      - name: Run Ruff
        run: ruff check .
      
      - name: Run Black
        run: black --check .
      
      - name: Run MyPy
        run: mypy src/lattice_lock
      
      - name: Run Bandit security scan
        run: bandit -r src/lattice_lock -c pyproject.toml

  test:
    needs: [quality]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@0a5c61591373683505ea898e09a3ea4f39ef2b9c  # v5.0.0
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache pip dependencies
        uses: actions/cache@0c45773b623bea8c8e75f6c82b208c3cf94ea4f9  # v4.0.2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('requirements.lock') }}
          restore-keys: |
            ${{ runner.os }}-pip-${{ matrix.python-version }}-
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.lock
          pip install -e ".[dev]"
      
      - name: Run tests with coverage
        run: pytest --cov=src/lattice_lock --cov-report=xml --cov-fail-under=70
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@e28ff129e5465c2c0dcc6f003fc735cb6ae0c673  # v4.5.0
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      
      - name: Setup Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8  # v4.0.2
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run lint
        run: npm run lint
      
      - name: Run tests
        run: npm test -- --run
      
      - name: Build
        run: npm run build
```

### 2. Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "chore"
    commit-message:
      prefix: "chore(deps)"

  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "chore"
    commit-message:
      prefix: "chore(deps)"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "chore"
    commit-message:
      prefix: "chore(ci)"
```

### 3. Branch Protection Rules

**Recommended Settings for `main` branch:**

| Setting | Value |
|---------|-------|
| Require pull request reviews | Yes |
| Required approving reviews | 1 |
| Dismiss stale reviews | Yes |
| Require review from CODEOWNERS | Yes |
| Require status checks | Yes |
| Required checks | policy, quality, test, frontend |
| Require branches up to date | Yes |
| Require conversation resolution | Yes |
| Require signed commits | Optional |
| Include administrators | Yes |
| Allow force pushes | No |
| Allow deletions | No |

## Implementation Plan

### Phase 1: Quick Wins (1 day)
1. Add concurrency controls to ci.yml
2. Remove `|| true` from Bandit command
3. Add pip caching to workflows

### Phase 2: Security Hardening (2-3 days)
4. Pin all actions to SHA
5. Create dependabot.yml
6. Document branch protection rules

### Phase 3: Frontend Integration (1 day)
7. Add frontend job to ci.yml
8. Configure npm caching

### Phase 4: Advanced Features (1 week)
9. Add code coverage badges
10. Add performance benchmarks to CI
11. Add mutation testing (mutmut)
12. Add dependency vulnerability scanning (pip-audit)

## Verification Checklist

After implementing changes:

- [ ] All CI jobs pass on a test PR
- [ ] Concurrency cancels duplicate runs
- [ ] Bandit failures block PRs
- [ ] Frontend tests run in CI
- [ ] Dependabot creates update PRs
- [ ] Branch protection rules enforced
- [ ] Actions pinned to SHA
- [ ] Caching reduces CI time by >30%
