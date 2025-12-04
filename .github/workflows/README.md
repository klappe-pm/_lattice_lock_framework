# Lattice Lock Reusable GitHub Actions Workflows

This directory contains reusable GitHub Actions workflows for Lattice Lock validation. These workflows can be called from any repository to integrate Lattice Lock validation into your CI/CD pipeline.

## Available Reusable Workflows

| Workflow | Purpose |
|----------|---------|
| `reusable-validate.yml` | Validates lattice.yaml, environment files, agent manifests, and repository structure |
| `reusable-sheriff.yml` | Performs AST-based Python code analysis for import discipline and type hint compliance |
| `reusable-gauntlet.yml` | Generates and runs semantic tests based on lattice.yaml contracts |
| `reusable-full-check.yml` | Combines all validation steps (validate + sheriff + gauntlet) |

## Quick Start

### Full Validation (Recommended)

The simplest way to add Lattice Lock validation to your project:

```yaml
# .github/workflows/lattice-lock.yml
name: Lattice Lock Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lattice-lock:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@main
    with:
      python-version: "3.11"
      source-directory: "src/"
```

## Usage Examples

### 1. Validate Only

Run only the configuration validation step:

```yaml
jobs:
  validate:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate.yml@main
    with:
      python-version: "3.11"
      working-directory: "."
```

**Available Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `python-version` | `"3.11"` | Python version to use |
| `working-directory` | `"."` | Working directory for validation |
| `fail-on-warning` | `false` | Fail validation if warnings are found |
| `schema-only` | `false` | Only validate lattice.yaml schema |
| `lattice-lock-version` | `""` | Specific version to install (empty = latest) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `validation-passed` | Whether validation passed (`true`/`false`) |
| `error-count` | Number of validation errors found |
| `warning-count` | Number of validation warnings found |

### 2. Sheriff AST Validation

Run AST-based code analysis:

```yaml
jobs:
  sheriff:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-sheriff.yml@main
    with:
      source-directory: "src/"
      format: "github"
      enable-cache: true
```

**Available Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `source-directory` | `"src/"` | Directory to analyze |
| `python-version` | `"3.11"` | Python version to use |
| `lattice-config` | `"lattice.yaml"` | Path to lattice.yaml |
| `format` | `"github"` | Output format: `text`, `json`, `github`, `junit` |
| `ignore-patterns` | `""` | Comma-separated glob patterns to ignore |
| `enable-cache` | `true` | Enable caching for performance |
| `cache-directory` | `".sheriff_cache"` | Cache directory path |
| `fail-on-violation` | `true` | Fail if violations found |
| `lattice-lock-version` | `""` | Specific version to install |

**Outputs:**

| Output | Description |
|--------|-------------|
| `sheriff-passed` | Whether Sheriff validation passed |
| `violations-count` | Number of violations found |
| `ignored-count` | Number of ignored violations |
| `report-path` | Path to JUnit report (if junit format) |

### 3. Gauntlet Semantic Tests

Generate and run semantic tests:

```yaml
jobs:
  gauntlet:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-gauntlet.yml@main
    with:
      test-directory: "tests/"
      coverage-enabled: true
      coverage-threshold: 80
```

**Available Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `test-directory` | `"tests/"` | Directory for generated tests |
| `python-version` | `"3.11"` | Python version to use |
| `lattice-config` | `"lattice.yaml"` | Path to lattice.yaml |
| `generate-only` | `false` | Generate tests without running |
| `coverage-enabled` | `true` | Enable coverage reporting |
| `coverage-threshold` | `80` | Minimum coverage percentage |
| `fail-on-test-failure` | `true` | Fail if tests fail |
| `extra-pytest-args` | `""` | Additional pytest arguments |
| `lattice-lock-version` | `""` | Specific version to install |

**Outputs:**

| Output | Description |
|--------|-------------|
| `gauntlet-passed` | Whether Gauntlet tests passed |
| `tests-generated` | Number of tests generated |
| `tests-passed` | Number of tests passed |
| `tests-failed` | Number of tests failed |
| `coverage-percentage` | Code coverage percentage |

### 4. Full Check (All Steps)

Run all validation steps together:

```yaml
jobs:
  lattice-lock:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@main
    with:
      python-version: "3.11"
      source-directory: "src/"
      test-directory: "tests/"
      coverage-enabled: true
      coverage-threshold: 80
```

**Available Inputs:**

| Input | Default | Description |
|-------|---------|-------------|
| `python-version` | `"3.11"` | Python version to use |
| `working-directory` | `"."` | Working directory |
| `source-directory` | `"src/"` | Source directory for Sheriff |
| `test-directory` | `"tests/"` | Test directory for Gauntlet |
| `lattice-config` | `"lattice.yaml"` | Path to lattice.yaml |
| `skip-validate` | `false` | Skip validate step |
| `skip-sheriff` | `false` | Skip Sheriff step |
| `skip-gauntlet` | `false` | Skip Gauntlet step |
| `coverage-enabled` | `true` | Enable coverage in Gauntlet |
| `coverage-threshold` | `80` | Coverage threshold |
| `sheriff-format` | `"github"` | Sheriff output format |
| `fail-fast` | `true` | Stop on first failure |
| `lattice-lock-version` | `""` | Specific version to install |

**Outputs:**

| Output | Description |
|--------|-------------|
| `validation-passed` | Whether validation passed |
| `sheriff-passed` | Whether Sheriff passed |
| `gauntlet-passed` | Whether Gauntlet passed |
| `all-passed` | Whether all checks passed |

## Advanced Usage

### Using Outputs in Dependent Jobs

```yaml
jobs:
  validate:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate.yml@main

  deploy:
    needs: validate
    if: needs.validate.outputs.validation-passed == 'true'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "Deploying validated code..."
```

### Matrix Testing with Multiple Python Versions

```yaml
jobs:
  validate:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@main
    with:
      python-version: ${{ matrix.python-version }}
```

### Selective Validation

Skip specific steps when needed:

```yaml
jobs:
  quick-check:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@main
    with:
      skip-gauntlet: true  # Skip tests for quick PR checks
      fail-fast: true
```

### Custom Ignore Patterns for Sheriff

```yaml
jobs:
  sheriff:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-sheriff.yml@main
    with:
      source-directory: "src/"
      ignore-patterns: "**/migrations/*,**/generated/*,tests/*"
```

### Pinning Lattice Lock Version

For reproducible builds, pin to a specific version:

```yaml
jobs:
  validate:
    uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-validate.yml@main
    with:
      lattice-lock-version: "0.1.0"
```

## Workflow Reference

You can reference a specific version of the reusable workflows:

```yaml
# Latest (main branch)
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@main

# Specific tag
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@v1.0.0

# Specific commit SHA (most reproducible)
uses: klappe-pm/lattice-lock-framework/.github/workflows/reusable-full-check.yml@abc1234
```

## Troubleshooting

### Common Issues

1. **"lattice-lock not found"**: Ensure the package is published to PyPI or use a custom installation step

2. **"lattice.yaml not found"**: Check that `lattice-config` input points to the correct path

3. **Sheriff cache issues**: Try disabling cache with `enable-cache: false` or clear cache directory

4. **Gauntlet test failures**: Check that your `tests/` directory exists and dependencies are installed

### Debug Mode

Add `ACTIONS_STEP_DEBUG` secret set to `true` in your repository for detailed logs.

## Requirements

- GitHub Actions runner with Python support
- `lattice-lock` package available (PyPI or local installation)
- `lattice.yaml` configuration file in your repository

## See Also

- [Lattice Lock Documentation](../../../README.md)
- [Sheriff CLI Reference](../actions/sheriff/action.yml)
- [Template Examples](../../src/lattice_lock_cli/templates/ci/github_actions/)
