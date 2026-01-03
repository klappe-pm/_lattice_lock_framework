# Issue Backlog

## Lattice Lock Framework - Prioritized Issues with Remediation Steps

This document contains all identified issues prioritized from P0 (blocker) to P4 (nice-to-have), with specific remediation steps for each.

## Priority Definitions

| Priority | Definition | SLA |
|----------|------------|-----|
| P0 | Blocker - Prevents CI/deployment | Immediate |
| P1 | Critical - Major functionality broken | 1-2 days |
| P2 | High - Significant quality issue | 1 week |
| P3 | Medium - Should fix soon | 2 weeks |
| P4 | Low - Nice to have | Backlog |

## P0 - Blockers

### P0-001: Test Coverage Below Threshold
**Status:** Open  
**Category:** Testing  
**Location:** `tests/`  
**Impact:** CI pipeline fails on coverage check

**Description:**
Current test coverage is 67.31%, failing the 70% minimum requirement configured in `pyproject.toml:96`.

**Remediation Steps:**
1. Run `pytest --cov=src/lattice_lock --cov-report=html` to generate coverage report
2. Identify files with lowest coverage:
   - `src/lattice_lock/sheriff/sheriff.py` (19%)
   - `src/lattice_lock/tracing.py` (49%)
   - `src/lattice_lock/validator/structure.py` (67%)
3. Add tests for uncovered code paths
4. Target: Increase coverage to 72%+ to provide buffer

**Estimated Effort:** 2-3 days

### P0-002: Failing Tests in Orchestrator Module
**Status:** Open  
**Category:** Testing  
**Location:** `tests/orchestrator/test_model_registry.py`, `tests/orchestrator/test_bedrock_implementation.py`  
**Impact:** CI pipeline fails on test step

**Description:**
10 tests are failing, primarily related to model registry loading and Bedrock implementation.

**Failing Tests:**
```
tests/orchestrator/test_model_registry.py::TestModelRegistryLoading::test_loads_from_yaml
tests/orchestrator/test_model_registry.py::TestModelRegistryLoading::test_loads_all_providers
tests/orchestrator/test_model_registry.py::TestModelRegistryValidation::test_validates_registry_yaml
tests/orchestrator/test_model_registry.py::TestModelRegistryValidation::test_validation_counts_models
tests/orchestrator/test_model_registry.py::TestModelRegistryValidation::test_validation_counts_providers
tests/orchestrator/test_model_registry.py::TestRegistryModelCount::test_registry_has_expected_model_count
tests/orchestrator/test_model_registry.py::TestRegistryModelCount::test_registry_has_models_from_major_providers
tests/orchestrator/test_model_registry_loading.py::test_registry_load_yaml
tests/orchestrator/test_bedrock_implementation.py::TestBedrockClient::test_init_sets_region
tests/orchestrator/test_api_refactor.py::test_base_api_client_exceptions
```

**Remediation Steps:**
1. Review `src/lattice_lock/orchestrator/models.yaml` for current model count
2. Update test expectations in `test_model_registry.py` to match actual model count
3. Fix Bedrock client initialization in `src/lattice_lock/orchestrator/providers/bedrock.py`
4. Run `pytest tests/orchestrator/ -v` to verify fixes

**Estimated Effort:** 1 day

## P1 - Critical

### P1-001: Type Errors (99 total)
**Status:** Open  
**Category:** Code Quality  
**Location:** 40 files across codebase  
**Impact:** Type safety compromised, potential runtime errors

**Description:**
MyPy reports 99 type errors across 40 files. Critical issues in middleware, providers, and database modules.

**Top Error Locations:**
- `src/lattice_lock/errors/middleware.py` (3 errors)
- `src/lattice_lock/tracing.py` (multiple async errors)
- `src/lattice_lock/orchestrator/consensus/engine.py` (6 errors)
- `src/lattice_lock/database/connection.py` (2 errors)
- Provider implementations (bedrock, azure, anthropic, google, local)

**Remediation Steps:**
1. Run `mypy src/lattice_lock --show-error-codes` to get full error list
2. Fix critical errors first:
   - `middleware.py`: Add proper overloads for sync/async variants
   - `connection.py`: Fix async context manager return type
   - `consensus/engine.py`: Add type guards for union types
3. Fix provider type errors
4. Run `mypy src/lattice_lock` to verify all errors resolved

**Estimated Effort:** 2-3 days

### P1-002: Lint Errors (125 total)
**Status:** Open  
**Category:** Code Quality  
**Location:** Throughout codebase  
**Impact:** Code quality standards not met

**Description:**
Ruff reports 125 lint errors, 107 of which are auto-fixable.

**Error Breakdown:**
- W293 blank-line-with-whitespace: 69
- UP006 non-pep585-annotation: 17
- F401 unused-import: 13
- UP035 deprecated-import: 10
- I001 unsorted-imports: 9
- W291 trailing-whitespace: 4
- W292 missing-newline-at-end-of-file: 2
- UP015 redundant-open-modes: 1

**Remediation Steps:**
1. Run `ruff check . --fix` to auto-fix 107 errors
2. Manually review and fix remaining 18 errors
3. Run `ruff check .` to verify all errors resolved
4. Run `black .` and `isort .` to ensure formatting consistency

**Estimated Effort:** 1 hour

### P1-003: Frontend Dependency Lockfile Sync
**Status:** Open  
**Category:** Dependencies  
**Location:** `frontend/package.json`  
**Impact:** Frontend build may fail if lockfile is stale

**Description:**
The `frontend/package.json` specifies recent major versions for testing dependencies (vitest ^4.0.16, globals ^17.0.0, jsdom ^27.4.0). If the lockfile is stale or missing, npm install may produce inconsistent results.

**Remediation Steps:**
1. Delete `frontend/node_modules` and `frontend/package-lock.json`
2. Run `npm install` in frontend directory to regenerate lockfile
3. Run `npm test` to verify tests pass
4. Commit the updated `package-lock.json`

**Estimated Effort:** 30 minutes

### P1-004: Missing Dependencies
**Status:** Open  
**Category:** Dependencies  
**Location:** `pyproject.toml`  
**Impact:** Runtime errors in production

**Description:**
Three packages are imported but not declared as dependencies:
- `psutil` in `scripts/utilities/local_model_automation.py:9`
- `google-cloud-*` in `src/database/gcp_clients.py:33,56`
- `redis` in `src/database/gcp_clients.py:90`

**Remediation Steps:**
1. Add to `pyproject.toml` dependencies:
   ```toml
   dependencies = [
       # ... existing deps ...
       "psutil>=5.9.0",
   ]
   
   [project.optional-dependencies]
   gcp = [
       "google-cloud-firestore>=2.0.0",
       "google-cloud-bigquery>=3.0.0",
       "redis>=4.0.0",
   ]
   ```
2. Run `pip-compile requirements.in -o requirements.lock`
3. Run `pip install -e .` to verify installation

**Estimated Effort:** 30 minutes

## P2 - High

### P2-001: Unused Dependencies
**Status:** Open  
**Category:** Dependencies  
**Location:** `pyproject.toml`  
**Impact:** Bloated dependency tree, potential security surface

**Description:**
deptry reports 22 unused dependencies. Some are dev tools (expected), but others may be truly unused:
- `tenacity` - Retry library, may be used indirectly
- `python-multipart` - FastAPI file uploads
- `aiosqlite` - Async SQLite driver

**Remediation Steps:**
1. Verify each flagged dependency:
   - Search codebase for imports
   - Check if used by FastAPI or other frameworks
2. Remove confirmed unused dependencies
3. Run full test suite to verify no breakage

**Estimated Effort:** 2 hours

### P2-002: Generated Files in Repository
**Status:** Open  
**Category:** Repository Hygiene  
**Location:** `src/generated/`  
**Impact:** Merge conflicts, confusion about source of truth

**Description:**
Generated test files are tracked in git and show as modified:
- `src/generated/tests/test_contract_Customer.py`
- `src/generated/tests/test_contract_Order.py`
- `src/generated/types_v2_pydantic.py`

**Remediation Steps:**
1. Add to `.gitignore`:
   ```
   src/generated/
   ```
2. Remove from git tracking:
   ```bash
   git rm -r --cached src/generated/
   ```
3. Commit the `.gitignore` change
4. Document generation process in README

**Estimated Effort:** 15 minutes

### P2-003: Bandit Security Failures Ignored
**Status:** Open  
**Category:** Security  
**Location:** `.github/workflows/ci.yml:78`  
**Impact:** Security issues silently ignored

**Description:**
Bandit security scanner failures are suppressed with `|| true`:
```yaml
- name: Run Bandit security scan
  run: bandit -r src/lattice_lock -c pyproject.toml || true
```

**Remediation Steps:**
1. Remove `|| true` from Bandit command
2. Run `bandit -r src/lattice_lock -c pyproject.toml` locally
3. Fix or suppress specific issues with inline comments
4. Update CI to fail on security issues

**Estimated Effort:** 2-4 hours

### P2-004: Terraform State Backend Not Configured
**Status:** Open  
**Category:** Infrastructure  
**Location:** `infrastructure/terraform/aws/main.tf:8-13`, `infrastructure/terraform/gcp/main.tf:18-21`  
**Impact:** Infrastructure deployment blocked

**Description:**
AWS backend is commented out, GCP backend references potentially non-existent bucket.

**Remediation Steps:**
1. Create S3 bucket for AWS state:
   ```bash
   aws s3 mb s3://lattice-lock-terraform-state-aws
   ```
2. Create GCS bucket for GCP state:
   ```bash
   gsutil mb gs://lattice-lock-terraform-state
   ```
3. Uncomment and configure AWS backend
4. Verify GCP bucket exists or create it
5. Run `terraform init` in each directory

**Estimated Effort:** 1 hour

## P3 - Medium

### P3-001: Duplicate Documentation Files
**Status:** Open  
**Category:** Documentation  
**Location:** `docs/guides/`  
**Impact:** Confusion, maintenance burden

**Description:**
Three files cover local models setup:
- `docs/guides/local_models_setup.md`
- `docs/guides/local_models_setup_guide.md`
- `docs/guides/local_models_setup_and_management.md`

**Remediation Steps:**
1. Review all three files for unique content
2. Consolidate into single `docs/guides/local_models.md`
3. Update all references to point to new file
4. Delete duplicate files

**Estimated Effort:** 1 hour

### P3-002: Missing CODE_OF_CONDUCT.md
**Status:** Open  
**Category:** Documentation  
**Location:** Repository root  
**Impact:** Contributor experience degraded

**Description:**
No CODE_OF_CONDUCT.md file present in repository.

**Remediation Steps:**
1. Create `CODE_OF_CONDUCT.md` using Contributor Covenant template
2. Add link in CONTRIBUTING.md
3. Add link in README.md

**Estimated Effort:** 30 minutes

### P3-003: Actions Not Pinned to SHA
**Status:** Open  
**Category:** CI/CD  
**Location:** `.github/workflows/*.yml`  
**Impact:** Supply chain security risk

**Description:**
GitHub Actions use version tags instead of SHA pins:
```yaml
uses: actions/checkout@v6
uses: actions/setup-python@v6
```

**Remediation Steps:**
1. Look up current SHA for each action version
2. Update to SHA-pinned format:
   ```yaml
   uses: actions/checkout@<sha>  # v6
   uses: actions/setup-python@<sha>  # v6
   ```
3. Add Dependabot config for action updates

**Estimated Effort:** 1 hour

### P3-004: Missing Database Migration Tool
**Status:** Open  
**Category:** Database  
**Location:** `src/lattice_lock/database/`  
**Impact:** Schema changes require manual updates

**Description:**
No Alembic or similar migration tool configured for SQLAlchemy models.

**Remediation Steps:**
1. Add `alembic>=1.12.0` to dependencies
2. Run `alembic init migrations`
3. Configure `alembic.ini` with database URL
4. Create initial migration from existing models
5. Document migration workflow in CONTRIBUTING.md

**Estimated Effort:** 2-3 hours

### P3-005: Missing Concurrency Controls in CI
**Status:** Open  
**Category:** CI/CD  
**Location:** `.github/workflows/ci.yml`  
**Impact:** Wasted CI resources on duplicate runs

**Description:**
No concurrency group configured, allowing multiple CI runs for same PR.

**Remediation Steps:**
1. Add concurrency configuration to ci.yml:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

**Estimated Effort:** 5 minutes

## P4 - Low

### P4-001: Root-Level Test Files
**Status:** Open  
**Category:** Repository Hygiene  
**Location:** Repository root  
**Impact:** Cluttered root directory

**Description:**
Test and example files in root directory:
- `multi_turn_example.py`
- `test_prompt.py`
- `pr_comments.json`
- `e2e_report.xml`

**Remediation Steps:**
1. Move `multi_turn_example.py` to `docs/examples/`
2. Move or delete `test_prompt.py`
3. Add `pr_comments.json` and `e2e_report.xml` to `.gitignore`

**Estimated Effort:** 15 minutes

### P4-002: Missing Accessibility Testing
**Status:** Open  
**Category:** Frontend  
**Location:** `frontend/`  
**Impact:** Accessibility issues may go undetected

**Description:**
No accessibility testing configured (axe-core, pa11y, etc.).

**Remediation Steps:**
1. Add `@axe-core/react` to frontend dependencies
2. Configure accessibility tests in Vitest
3. Add accessibility check to CI pipeline

**Estimated Effort:** 2-3 hours

### P4-003: Incomplete API Reference Documentation
**Status:** Open  
**Category:** Documentation  
**Location:** `docs/reference/api/`  
**Impact:** Developer experience degraded

**Description:**
API reference documentation exists but may be incomplete or outdated.

**Remediation Steps:**
1. Audit existing API docs against actual endpoints
2. Generate OpenAPI spec from FastAPI
3. Update documentation to match current API

**Estimated Effort:** 4-6 hours

### P4-004: Missing ARCHITECTURE.md at Root
**Status:** Open  
**Category:** Documentation  
**Location:** Repository root  
**Impact:** New contributors may struggle to understand codebase

**Description:**
No high-level architecture document at repository root.

**Remediation Steps:**
1. Create `ARCHITECTURE.md` with:
   - System overview diagram
   - Component descriptions
   - Data flow diagrams
   - Key design decisions

**Estimated Effort:** 2-3 hours

## Summary

| Priority | Count | Estimated Total Effort |
|----------|-------|------------------------|
| P0 | 2 | 3-4 days |
| P1 | 4 | 3-4 days |
| P2 | 4 | 5-7 hours |
| P3 | 5 | 5-7 hours |
| P4 | 4 | 9-12 hours |
| **Total** | **19** | **~2 weeks** |
