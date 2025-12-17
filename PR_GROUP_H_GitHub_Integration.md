# PR: Group H - GitHub CI Integration

## Overview
This PR aligns the CI environment with the local development environment to resolve PR check failures.

## Changes

### 1. Verification of Dependencies (Task H1)
- **`pyproject.toml`**: Added `bcrypt` to dependencies. This was required for `admin/auth_routes.py` but was missing from the declared dependencies, causing `ModuleNotFoundError` in clean CI environments despite working locally (likely due to pre-installed packages).

### 2. Configure GitHub Actions (Task H2)
- **`.github/workflows/ci.yml`**: Updated the "Unit Tests" step to run `make test` instead of calling `pytest` directly.
- **`.github/workflows/python-app.yml`**: Similarly updated to use `make test`.
- **Reasoning**: `make test` encapsulates environment variables (e.g., test secrets) and flags specific to the project. Using it in CI ensures that "if it passes locally with `make test`, it passes in CI".

## Verification
- **Local**: `make test` passes (verified in Group G).
- **CI**: Pushing this commit should trigger the workflows. The `bcrypt` installation will now succeed, allowing `lattice-lock validate` and `make test` (including admin tests if their skips are removed or if `bcrypt` makes them viable) to run.
