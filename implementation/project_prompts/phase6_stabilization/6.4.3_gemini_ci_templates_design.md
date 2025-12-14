# Task 6.4.3: CI Templates & Workflows Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.4.4 (Devin AI)

---

## 1. CI Pipeline Standard

We strictly enforce a **"Fail Fast"** pipeline structure.

### Stages
1.  **Format & Lint (Fastest)**
    *   `ruff check .`
    *   `black --check .`
2.  **Governance Check (Fast)**
    *   `lattice-lock validate` (Sheriff)
    *   Ensures architecture rules are met.
3.  **Unit Tests (Medium)**
    *   `pytest tests/unit`
4.  **Semantic Tests (Slow)**
    *   `lattice-lock test` (Gauntlet)
    *   Uses LLMs to verify behavior. *Note: Only run on PRs with 'governance' label or merge to main.*
5.  **Build**
    *   Create artifacts (Docker image, pypi package).

## 2. GitHub Actions Template (`.github/workflows/ci.yml`)

```yaml
name: Lattice Lock CI

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install
        run: pip install .[dev]
      - name: Governance Check
        run: lattice-lock validate

  test:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Unit Tests
        run: pytest tests/unit
```

## 3. Dependency Hardening Strategy

*   **Problem:** Loose dependencies (`package>=1.0`) cause "it works on my machine" bugs.
*   **Solution:**
    *   `pyproject.toml`: Define loose ranges (semver compatible).
    *   `requirements.lock`: Exact hashes for CI/Production.
    *   **Bot:** Renovate/Dependabot configured to propose lockfile updates weekly.

## 4. Implementation Tasks

1.  **[ ] Create `.github/workflows/`:**
    *   `ci.yml` (PR validation)
    *   `release.yml` (Tag-triggered publish)
2.  **[ ] Create `scripts/update_deps.sh`:**
    *   Helper to compile `requirements.in` to `requirements.lock`.
3.  **[ ] Add `Makefile`:**
    *   Shortcuts: `make lint`, `make test`, `make ci`.
