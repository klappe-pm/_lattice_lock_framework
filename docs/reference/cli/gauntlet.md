# lattice-lock gauntlet

Generate and run semantic tests from lattice.yaml.

## Synopsis

```bash
lattice-lock gauntlet [OPTIONS]
```

## Description

The `gauntlet` command generates and executes semantic contract tests based on entity definitions in your `lattice.yaml` file. It creates pytest-compatible test files that validate constraints, ensures conditions, and field types defined in your schema.

Gauntlet transforms declarative schema definitions into executable tests, ensuring your code adheres to the contracts defined in your Lattice Lock configuration.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--generate` | flag | | Generate tests from lattice.yaml without running them |
| `--run` / `--no-run` | flag | `--run` | Run the tests after generation (default: True) |
| `--output` | path | `tests/gauntlet` | Directory to output generated tests |
| `--lattice` | path | `lattice.yaml` | Path to lattice.yaml file |
| `--coverage` | flag | | Enable coverage reporting |
| `--format` | choice (multiple) | | Output format(s): `json`, `junit`, `github` |
| `--parallel` | flag/string | | Run tests in parallel. Optional: specify number of workers (default: auto) |

## Generated Tests

Gauntlet generates tests for each entity defined in `lattice.yaml`:

### Constraint Tests

Tests that validate field constraints:

```yaml
# lattice.yaml
entities:
  User:
    fields:
      email: str
    constraints:
      email: {unique: true, max_length: 255}
```

Generates:

```python
def test_user_email_max_length():
    """Verify email field respects max_length constraint."""
    # Test that email cannot exceed 255 characters
    ...

def test_user_email_uniqueness():
    """Verify email field is unique."""
    # Test that duplicate emails are rejected
    ...
```

### Ensures Tests

Tests that validate business logic conditions:

```yaml
# lattice.yaml
entities:
  Order:
    fields:
      total_cents: int
      status: str
    ensures:
      - "total_cents >= 0"
      - "status in ['pending', 'confirmed', 'shipped']"
```

Generates:

```python
def test_order_total_cents_non_negative():
    """Verify total_cents >= 0 constraint."""
    ...

def test_order_status_valid_values():
    """Verify status is in allowed values."""
    ...
```

### Type Tests

Tests that validate field types:

```python
def test_user_email_is_string():
    """Verify email field is of type str."""
    ...

def test_order_total_cents_is_integer():
    """Verify total_cents field is of type int."""
    ...
```

## Output Directory Structure

```
tests/gauntlet/
├── __init__.py
├── conftest.py
├── test_user_contracts.py
├── test_order_contracts.py
├── test_product_contracts.py
└── ...
```

## Examples

### Generate Tests Only

Generate tests without running them:

```bash
lattice-lock gauntlet --generate
```

### Generate and Run

Generate tests and run them immediately:

```bash
lattice-lock gauntlet --generate --run
```

### Run Existing Tests

Run previously generated tests:

```bash
lattice-lock gauntlet --run
```

### Custom Output Directory

```bash
lattice-lock gauntlet --generate --output tests/contracts
```

### Custom Configuration

```bash
lattice-lock gauntlet --generate --lattice schemas/api-lattice.yaml
```

### With Coverage

```bash
lattice-lock gauntlet --run --coverage
```

### Multiple Output Formats

```bash
lattice-lock gauntlet --run --format json --format junit
```

### Parallel Execution

Run tests in parallel (requires pytest-xdist):

```bash
# Auto-detect worker count
lattice-lock gauntlet --run --parallel

# Specify worker count
lattice-lock gauntlet --run --parallel 4
```

## Output Formats

### json

Enables JSON test report output. Requires the Gauntlet pytest plugin.

```bash
lattice-lock gauntlet --run --format json
```

Sets environment variable: `GAUNTLET_JSON_REPORT=true`

### junit

Generates JUnit XML report for CI integration:

```bash
lattice-lock gauntlet --run --format junit
```

Creates: `test-results.xml`

### github

Enables GitHub Actions annotations:

```bash
lattice-lock gauntlet --run --format github
```

Sets environment variable: `GAUNTLET_GITHUB_REPORT=true`

## CI/CD Integration

### GitHub Actions

```yaml
name: Contract Tests
on: [push, pull_request]

jobs:
  gauntlet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install lattice-lock pytest

      - name: Generate and Run Gauntlet Tests
        run: lattice-lock gauntlet --generate --run --format github --format junit

      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results.xml
```

### Jenkins

```groovy
pipeline {
    stages {
        stage('Contract Tests') {
            steps {
                sh 'lattice-lock gauntlet --generate --run --format junit'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
    }
}
```

## Coverage Reporting

Enable coverage with pytest-cov:

```bash
# Install pytest-cov
pip install pytest-cov

# Run with coverage
lattice-lock gauntlet --run --coverage
```

Output:

```
---------- coverage: platform darwin, python 3.11.4 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/models/user.py                   45      3    93%   12, 45-46
src/models/order.py                  62      8    87%   23-25, 67-71
---------------------------------------------------------------
TOTAL                               107     11    90%
```

## Parallel Execution

For large test suites, use parallel execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run in parallel (auto-detect CPUs)
lattice-lock gauntlet --run --parallel

# Run with specific worker count
lattice-lock gauntlet --run --parallel 8
```

**Note:** If pytest-xdist is not installed, a warning is displayed and tests run sequentially.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All tests passed |
| `1` | Test generation error or tests failed |
| Other | pytest exit code (test failures, collection errors, etc.) |

## Prerequisites

- `lattice.yaml` must exist with valid entity definitions
- pytest must be installed
- For parallel execution: pytest-xdist
- For coverage: pytest-cov

## Troubleshooting

### "Test directory does not exist"

Run with `--generate` first:

```bash
lattice-lock gauntlet --generate --run
```

### "pytest-xdist not installed"

Install the parallel execution dependency:

```bash
pip install pytest-xdist
```

### Tests Not Regenerating

Delete existing tests and regenerate:

```bash
rm -rf tests/gauntlet
lattice-lock gauntlet --generate
```

## See Also

- [CLI Overview](docs/reference/cli/index.md)
- [sheriff](docs/reference/cli/sheriff.md) - AST-based static validation
- [validate](validate.md) - Schema validation
- [Configuration Reference](docs/reference/configuration.md) - lattice.yaml schema
