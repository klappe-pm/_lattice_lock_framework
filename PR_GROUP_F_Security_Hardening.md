# PR: Group F - Security Hardening

## Overview
This PR addresses critical security hardening tasks, specifically XML External Entity (XXE) vulnerability mitigation and the removal of hardcoded secrets from the test suite.

## Changes

### 1. XXE Vulnerability Mitigation (Task F1)
- **Verification**: Audited `src/lattice_lock_sheriff/formatters.py` and confirmed that `defusedxml.minidom` is already used for parsing XML strings, preventing XXE attacks.
- **Dependency**: `defusedxml` is present in `pyproject.toml` and verified as a dependency.
- **Decision**: Option A (Use `defusedxml`) was implicitly adopted and is now confirmed.

### 2. Remove Hardcoded Secrets (Task F2)
- **Review**: Identified hardcoded secret usage in `tests/test_admin_auth.py` and `tests/test_error_middleware.py`.
- **Refactoring**:
    - **`tests/conftest.py`**: Created a session-scoped `auth_secrets` fixture that loads secrets from environment variables (`LATTICE_TEST_*`) or falls back to safe dummy defaults (lines 35-43).
    - **`tests/test_admin_auth.py`**: Updated all tests to use the `auth_secrets` fixture instead of module-level constants.
    - **`tests/test_error_middleware.py`**: Replaced hardcoded default values in redaction tests with explicit dummy placeholder strings.
- **CI Impact**: CI pipelines should be configured to inject these secrets via environment variables for testing against real credentials if needed, though defaults ensure tests pass safely.

## Verification
- **Tests**: `pytest` should pass without modification to test logic. Verified that tests use the new fixture architecture.
- **Security Check**: Codebase search confirms no obvious hardcoded credentials related to admin authentication remain in the test files.
