# Lattice Lock Governance Guide

> **Note:** For complete contribution standards including file naming, PR process, and commit standards, see [contributing.md](../../contributing.md) (single source of truth).

This guide walks you through the end-to-end governance workflow using the Lattice Lock Framework.

## Objective
Go from zero to a fully governed project in < 5 minutes.

## Prerequisites
- Python 3.11+
- `lattice-lock` installed (`pip install lattice-lock`)

## step 1: Define Rules (The "Contract")

The `lattice.yaml` file is the constitution of your project. It defines architecture rules and policies.

1. Create a `lattice.yaml` file in your root directory.
2. Add the following rule example (Canonical "No Print" Rule):

```yaml
version: "2.1"
rules:
  - id: "no-print"
    description: "Use logger instead of print statements in production code."
    severity: "error"
    scope: "src/**/*.py"
    excludes: ["scripts/*", "tests/*"]
    forbids: "node.is_call_to('print')"
```

## Step 2: Compile Policies

Compile your policies into Python artifacts (AST checkers and tests).

```bash
lattice-lock compile
```

You should see output indicating that rules have been generated in `build/lattice_rules.py`.

## Step 3: Verify (The "Sheriff")

Static analysis catches violations before you commit.

1. Create a file `src/bad_code.py`:

```python
def legacy_debug():
    print("I shouldn't be here!")
```

2. Run validation:

```bash
lattice-lock validate
```

**Expected Output:**
```text
[ERROR] no-print: Use logger instead of print statements in production code. (src/bad_code.py:2)
Validation Failed.
```

## Step 4: Runtime Enforcement (The "Gauntlet")

For semantic properties that cannot be checked statically, use Gauntlet.

```bash
lattice-lock test
```

This generates and runs pytest-based tests derived from your `lattice.yaml` policies.

## Next Steps
- Integrate with CI/CD (see `.github/workflows/ci.yml`).
- Explore the API Reference for advanced rule definitions.
