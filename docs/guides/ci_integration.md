---
title: ci_integration
type: guide
status: stable
categories: [guides, integration]
sub_categories: [ci_cd]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [guide-ci-001]
tags: [guide, ci, cd, integration]
---

# CI/CD Integration

This tutorial shows you how to integrate Lattice Lock validation into your CI/CD pipeline. You'll learn to configure GitHub Actions, handle failures, and follow best practices.

**Prerequisites:** Complete [Adding Validation Rules](adding_validation.md) first.

## Overview

Lattice Lock integrates with CI/CD to enforce governance at merge time:

```
Code Push → CI Runs → Validation → Pass/Fail → Merge Decision
```

**Supported CI Providers:**
- GitHub Actions (default)
- AWS CodeBuild
- Any CI system that can run Python

## Step 1: GitHub Actions Workflow

When you run `lattice-lock init`, a workflow file is automatically created at `.github/workflows/lattice-lock.yml`.

### Default Workflow

```yaml
# .github/workflows/lattice-lock.yml
name: Lattice Lock Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install lattice-lock
          pip install -e ".[dev]"

      - name: Run Lattice Lock validation
        run: |
          lattice-lock validate

      - name: Run Sheriff AST validation
        run: |
          lattice-lock sheriff src/

      - name: Run Gauntlet semantic tests
        run: |
          lattice-lock gauntlet

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
```

### Understanding the Workflow

| Step | Purpose |
|------|---------|
| Checkout | Clone the repository |
| Set up Python | Install Python with version matrix |
| Install dependencies | Install Lattice Lock and project deps |
| Lattice Lock validate | Schema and structure validation |
| Sheriff | AST-based code analysis |
| Gauntlet | Semantic contract tests |
| pytest | Run project tests |

## Step 2: Using Reusable Workflows

For simpler configuration, use the Lattice Lock reusable workflows:

### Full Pipeline (Recommended)

```yaml
# .github/workflows/lattice-lock.yml
name: Lattice Lock

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lattice-lock:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-pipeline.yml@main
    with:
      python-version: '3.11'
```

### Validate Only

For quick validation without tests:

```yaml
jobs:
  validate:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate-only.yml@main
```

### Sheriff Only

For AST validation only:

```yaml
jobs:
  sheriff:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-sheriff-only.yml@main
    with:
      source-path: 'src/'
```

### Gauntlet Only

For semantic tests only:

```yaml
jobs:
  gauntlet:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-gauntlet-only.yml@main
```

## Step 3: Enhanced Workflow with Reporting

Add better reporting and caching:

```yaml
name: Lattice Lock CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false  # Don't cancel other jobs on failure

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install lattice-lock
          pip install -e ".[dev]"

      - name: Schema validation
        run: lattice-lock validate

      - name: Sheriff AST validation
        run: |
          lattice-lock sheriff src/ --format github
        continue-on-error: false

      - name: Gauntlet semantic tests
        run: |
          lattice-lock gauntlet --generate --run --format junit
        continue-on-error: false

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: test-results.xml

      - name: Run pytest with coverage
        run: |
          pytest tests/ -v --tb=short --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

## Step 4: GitHub Actions Annotations

Sheriff and Gauntlet support GitHub Actions annotations that appear inline on pull requests:

```yaml
- name: Sheriff with annotations
  run: |
    lattice-lock sheriff src/ --format github
```

When violations are found, they appear as annotations:

```
⚠️ warning src/services/user.py#L15
TYPE001 - Missing type hint for parameter 'data'
```

## Step 5: Handling CI Failures

### Understand Exit Codes

| Tool | Exit 0 | Exit 1 |
|------|--------|--------|
| `validate` | All validations passed | Validation errors |
| `sheriff` | No violations | Violations found |
| `gauntlet` | All tests passed | Test failures |

### Debugging Failures

When CI fails, check:

1. **Which step failed?** Look at the workflow run logs
2. **What's the error?** Read the output for specific violations
3. **Reproduce locally:**
   ```bash
   # Run the same commands locally
   lattice-lock validate
   lattice-lock sheriff src/
   lattice-lock gauntlet --generate --run
   ```

### Common CI Failure Patterns

#### Schema Validation Failure

```
✗ Validation failed: 1 error(s), 0 warning(s)
  ✗ lattice.yaml: Invalid YAML syntax at line 15
```

**Fix:** Check YAML syntax in `lattice.yaml`:
```bash
# Validate YAML locally
python -c "import yaml; yaml.safe_load(open('lattice.yaml'))"
```

#### Sheriff Violations

```
src/services/api.py:45:1 - IMPORT001 - Forbidden import: os.system
✗ Found 1 violation(s)
```

**Fix:** Remove forbidden import and use safe alternative

#### Gauntlet Test Failure

```
FAILED test_user_contracts.py::test_email_format
  AssertionError: Email must contain '@'
```

**Fix:** Update code to match entity constraints

### Allow Failures for Specific Steps

For gradual adoption, allow certain steps to fail:

```yaml
- name: Sheriff (warnings only)
  run: lattice-lock sheriff src/
  continue-on-error: true  # Don't fail the build
```

## Step 6: Branch Protection Rules

Require validation to pass before merging:

1. Go to **Settings → Branches → Branch protection rules**
2. Click **Add rule** for `main`
3. Enable **Require status checks to pass before merging**
4. Select the `validate` job

This blocks merges until all validation passes.

## Step 7: AWS CodeBuild Configuration

If using AWS CodeBuild instead of GitHub Actions:

### Generate AWS CI Files

```bash
lattice-lock init my_project --ci aws
```

This creates:
```
ci/aws/
├── buildspec.yml
├── pipeline.yml
└── codebuild-project.yml
```

### buildspec.yml

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - pip install lattice-lock
      - pip install -e ".[dev]"

  build:
    commands:
      - lattice-lock validate
      - lattice-lock sheriff src/
      - lattice-lock gauntlet --generate --run
      - pytest tests/ -v

reports:
  test-reports:
    files:
      - 'test-results.xml'
    file-format: JUNITXML

artifacts:
  files:
    - '**/*'
```

## Step 8: Best Practices

### 1. Run Validation Early

Put validation steps before expensive operations:

```yaml
steps:
  # Fast checks first
  - run: lattice-lock validate
  - run: lattice-lock sheriff src/

  # Then slower operations
  - run: lattice-lock gauntlet --run
  - run: pytest tests/ -v
```

### 2. Use Caching

Cache pip dependencies and Sheriff cache:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

- name: Cache Sheriff
  uses: actions/cache@v4
  with:
    path: .sheriff_cache
    key: sheriff-${{ hashFiles('lattice.yaml') }}
```

### 3. Parallelize Jobs

Run independent validations in parallel:

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - run: lattice-lock validate

  sheriff:
    runs-on: ubuntu-latest
    steps:
      - run: lattice-lock sheriff src/

  gauntlet:
    runs-on: ubuntu-latest
    steps:
      - run: lattice-lock gauntlet --run

  all-checks:
    needs: [validate, sheriff, gauntlet]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All checks passed!"
```

### 4. Version Pin Dependencies

Pin versions for reproducible builds:

```yaml
- run: |
    pip install lattice-lock==X.X.X
    pip install -e ".[dev]"
```

### 5. Fail Fast vs Complete

Choose based on your needs:

```yaml
strategy:
  fail-fast: true   # Stop all jobs on first failure (faster)
  fail-fast: false  # Run all jobs to completion (more info)
```

### 6. Use Matrix Builds

Test across Python versions:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

### 7. Separate Workflows for PRs vs Main

```yaml
# pr-validation.yml - Fast checks for PRs
on:
  pull_request:
jobs:
  quick-check:
    steps:
      - run: lattice-lock validate
      - run: lattice-lock sheriff src/

# main-validation.yml - Full checks for main
on:
  push:
    branches: [main]
jobs:
  full-check:
    steps:
      - run: lattice-lock validate
      - run: lattice-lock sheriff src/
      - run: lattice-lock gauntlet --run --coverage
      - run: pytest tests/ -v --cov
```

## Complete Example Workflow

Here's a production-ready workflow:

```yaml
name: Lattice Lock CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    name: Validate (${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Cache Sheriff
        uses: actions/cache@v4
        with:
          path: .sheriff_cache
          key: sheriff-${{ hashFiles('lattice.yaml', 'src/**/*.py') }}

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install lattice-lock
          pip install -e ".[dev]"

      - name: Schema validation
        run: lattice-lock validate

      - name: Sheriff AST validation
        run: lattice-lock sheriff src/ --format github

      - name: Generate Gauntlet tests
        run: lattice-lock gauntlet --generate

      - name: Run Gauntlet tests
        run: |
          lattice-lock gauntlet --run --format junit
        continue-on-error: true

      - name: Run pytest
        run: pytest tests/ -v --tb=short --junitxml=pytest-results.xml

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: |
            test-results.xml
            pytest-results.xml
```

## Troubleshooting CI Issues

### "lattice-lock: command not found"

```yaml
- name: Install lattice-lock
  run: pip install lattice-lock

- name: Verify installation
  run: which lattice-lock && lattice-lock --version
```

### "No lattice.yaml found"

Ensure the file exists and is committed:
```bash
git ls-files lattice.yaml  # Should show the file
```

### Tests Pass Locally but Fail in CI

Check for:
- Different Python versions
- Missing dependencies
- Environment variable differences
- Path differences (absolute vs relative)

Debug with:
```yaml
- name: Debug environment
  run: |
    pwd
    ls -la
    python --version
    pip list
```

## What's Next?

Congratulations! You've completed the Lattice Lock tutorial series. You now know how to:

- ✅ Set up your development environment
- ✅ Create and structure projects
- ✅ Add validation rules and constraints
- ✅ Integrate with CI/CD pipelines

### Continue Learning

- [Configuration Reference](docs/reference/configuration.md) - Full lattice.yaml schema
- [CLI Reference](docs/reference/cli/index.md) - All commands documented
- [Development Guide](development_guide.md) - Contribute to Lattice Lock

## Quick Reference

| Workflow Type | Use Case |
|---------------|----------|
| Full Pipeline | Complete validation for main branches |
| Validate Only | Quick schema checks |
| Sheriff Only | Code quality gates |
| Gauntlet Only | Contract test verification |

### Reusable Workflows

```yaml
# Full validation
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-pipeline.yml@main

# Validate only
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate-only.yml@main

# Sheriff only
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-sheriff-only.yml@main

# Gauntlet only
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-gauntlet-only.yml@main
```

## See Also

- [Getting Started](getting_started.md) - First tutorial
- [Creating Your First Project](first_project.md) - Project setup
- [Adding Validation Rules](adding_validation.md) - Validation details
- [CLI Reference](docs/reference/cli/index.md) - Command documentation
