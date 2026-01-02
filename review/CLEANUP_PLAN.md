# Cleanup Plan

## Lattice Lock Framework - Repository Hygiene and Cleanup Recommendations

This document outlines files to delete, branches to clean up, configurations to update, and general repository hygiene improvements.

## Files to Delete or Move

### Root-Level Files to Move

| File | Current Location | Recommended Action | Reason |
|------|------------------|-------------------|--------|
| `multi_turn_example.py` | Root | Move to `docs/examples/` | Example code should be in docs |
| `test_prompt.py` | Root | Move to `tests/` or delete | Test file in wrong location |

### Files to Add to .gitignore

| File/Pattern | Reason |
|--------------|--------|
| `src/generated/` | Generated files should not be tracked |
| `pr_comments.json` | Temporary/generated file |
| `e2e_report.xml` | Test output file |
| `*.pyc` | Already ignored, verify |
| `__pycache__/` | Already ignored, verify |
| `.coverage` | Coverage data |
| `htmlcov/` | Coverage HTML report |
| `.pytest_cache/` | Pytest cache |
| `.mypy_cache/` | MyPy cache |
| `.ruff_cache/` | Ruff cache |
| `*.egg-info/` | Package metadata |
| `dist/` | Build output |
| `build/` | Build output |
| `.env` | Environment secrets |
| `*.db` | SQLite databases |
| `node_modules/` | Already ignored, verify |

### Recommended .gitignore Additions

```gitignore
# Generated files
src/generated/

# Temporary files
pr_comments.json
e2e_report.xml

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Terraform
*.tfstate
*.tfstate.*
.terraform/
*.tfvars
```

## Generated Files Issue

### Current State

The following generated files are tracked in git and show as modified:
- `src/generated/tests/test_contract_Customer.py`
- `src/generated/tests/test_contract_Order.py`
- `src/generated/types_v2_pydantic.py`

### Remediation Steps

```bash
# 1. Add to .gitignore
echo "src/generated/" >> .gitignore

# 2. Remove from git tracking (keeps files locally)
git rm -r --cached src/generated/

# 3. Commit the change
git add .gitignore
git commit -m "chore: stop tracking generated files"

# 4. Document generation process
# Add to README or CONTRIBUTING.md:
# "Generated files in src/generated/ are created by running:
#  python -m lattice_lock.compile lattice.yaml"
```

## Branches to Clean Up

### Recommended Branch Cleanup Policy

1. **Delete merged branches:** After PR merge, delete source branch
2. **Stale branch threshold:** 90 days without commits
3. **Protected branches:** `main` only

### GitHub Settings

```yaml
# Repository Settings > Branches
# Enable "Automatically delete head branches"
```

## Configuration Updates

### 1. Update .gitignore

**Location:** `.gitignore`

**Add:**
```gitignore
# Generated files
src/generated/

# Temporary/output files
pr_comments.json
e2e_report.xml

# Terraform state (if not already)
*.tfstate
*.tfstate.*
.terraform/
```

### 2. Update pyproject.toml

**Location:** `pyproject.toml`

**Changes:**
- Remove unused dependencies (see DEPENDENCY_PLAN.md)
- Add missing dependencies
- Update version constraints

### 3. Update pre-commit-config.yaml

**Location:** `.pre-commit-config.yaml`

**Add:**
```yaml
# Add generated file check
- repo: local
  hooks:
    - id: check-generated-files
      name: Check generated files not committed
      entry: bash -c 'git diff --cached --name-only | grep -q "^src/generated/" && echo "Error: Do not commit generated files" && exit 1 || exit 0'
      language: system
      pass_filenames: false
```

### 4. Update Dockerfile

**Location:** `Dockerfile`

**Verify:**
- Non-root user configured (already done)
- Health check configured
- Minimal image size

### 5. Update docker-compose.yml

**Location:** `docker-compose.yml`

**Verify:**
- Environment variables properly configured
- Volumes for persistent data
- Network configuration

## Repository Settings Recommendations

### GitHub Repository Settings

| Setting | Recommended Value |
|---------|-------------------|
| Default branch | `main` |
| Allow merge commits | No |
| Allow squash merging | Yes (default) |
| Allow rebase merging | No |
| Auto-delete head branches | Yes |
| Require PR before merging | Yes |
| Require status checks | Yes |
| Require conversation resolution | Yes |

### Branch Protection Rules for `main`

| Rule | Value |
|------|-------|
| Require pull request reviews | Yes |
| Required approving reviews | 1 |
| Dismiss stale reviews | Yes |
| Require review from CODEOWNERS | Yes |
| Require status checks to pass | Yes |
| Required checks | policy, quality, test |
| Require branches up to date | Yes |
| Include administrators | Yes |
| Allow force pushes | No |
| Allow deletions | No |

## Cleanup Scripts

### Script 1: Clean Generated Files

```bash
#!/bin/bash
# scripts/clean_generated.sh

echo "Cleaning generated files..."
rm -rf src/generated/
echo "Done. Run 'python -m lattice_lock.compile lattice.yaml' to regenerate."
```

### Script 2: Clean Build Artifacts

```bash
#!/bin/bash
# scripts/clean_build.sh

echo "Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info/
rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
rm -rf htmlcov/ .coverage
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "Done."
```

### Script 3: Clean Frontend

```bash
#!/bin/bash
# scripts/clean_frontend.sh

echo "Cleaning frontend..."
cd frontend
rm -rf node_modules/ dist/
echo "Done. Run 'npm install' to reinstall dependencies."
```

## Makefile Updates

**Location:** `Makefile`

**Add targets:**
```makefile
.PHONY: clean clean-all clean-generated clean-build clean-frontend

clean: clean-build
	@echo "Basic cleanup complete"

clean-all: clean-build clean-generated clean-frontend
	@echo "Full cleanup complete"

clean-generated:
	rm -rf src/generated/

clean-build:
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

clean-frontend:
	cd frontend && rm -rf node_modules/ dist/
```

## Implementation Checklist

### Immediate Actions (P1)

- [ ] Add `src/generated/` to `.gitignore`
- [ ] Remove generated files from git tracking
- [ ] Add `pr_comments.json` and `e2e_report.xml` to `.gitignore`

### Short-term Actions (P2)

- [ ] Move `multi_turn_example.py` to `docs/examples/`
- [ ] Move or delete `test_prompt.py`
- [ ] Add pre-commit hook to prevent generated file commits
- [ ] Enable auto-delete head branches in GitHub settings

### Medium-term Actions (P3)

- [ ] Add cleanup scripts to `scripts/`
- [ ] Update Makefile with clean targets
- [ ] Configure branch protection rules
- [ ] Document cleanup procedures in CONTRIBUTING.md

### Verification

After cleanup:
```bash
# Verify .gitignore working
git status  # Should not show src/generated/ files

# Verify clean targets work
make clean-all

# Verify pre-commit hooks
pre-commit run --all-files
```

## Estimated Impact

| Action | Files Affected | Risk |
|--------|----------------|------|
| Add to .gitignore | 1 file | Low |
| Remove generated from tracking | 3 files | Low |
| Move example files | 2 files | Low |
| Update Makefile | 1 file | Low |
| Add cleanup scripts | 3 files | Low |
| Update pre-commit | 1 file | Low |

**Total estimated effort:** 1-2 hours
