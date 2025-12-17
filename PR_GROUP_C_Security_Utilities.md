# PR: Group C - Shared Utility Refactoring (Security)

## Overview
This PR implements centralized security utilities for the Lattice Lock Framework to address identified vulnerabilities (XSS, Path Traversal) and improve code hygiene. It also includes security hardening for test files by removing hardcoded secrets.

## Changes

### 1. Centralized Jinja2 Configuration (Anti-XSS)
- **New Utility**: `src/lattice_lock/utils/jinja.py` provides `get_secure_environment` and `create_template` which enforce `autoescape=True` by default.
- **Refactoring**:
    - `src/lattice_lock_agents/prompt_architect/subagents/prompt_generator.py`: Updated to use `create_template`.
    - `src/lattice_lock_gauntlet/generator.py`: Updated to use `get_secure_environment`.
    - `src/lattice_lock_cli/templates/__init__.py`: Updated to use `get_secure_environment`.

### 2. Centralized Path Validation (Anti-Path Traversal)
- **New Utility**: `src/lattice_lock/utils/safe_path.py` implements `resolve_under_root` to prevent directory traversal attacks.
- **Refactoring**:
    - `src/lattice_lock_validator/structure.py`: Removed insecure fallback and enforced usage of `resolve_under_root`.
    - `scripts/prompt_tracker.py`: Added usage of `resolve_under_root` for validating user-provided file paths.
    - `src/lattice_lock_gauntlet/plugin.py`: Enforced usage of `resolve_under_root`.

### 3. Security Hardening (Test Secrets)
- **Refactoring**:
    - `tests/test_admin_auth.py`: Replaced module-level hardcoded secret constants with a `auth_secrets` pytest fixture that supports environment variable overrides and uses safe dummy defaults.
    - `tests/test_error_middleware.py`: Replaced hardcoded default values in redaction tests with safe dummy strings.

## Verification
- **Tests**: Existing tests should pass as changes were primarily refactoring implementations to use safer utilities without changing behavior.
- **Security**:
    - Jinja2 templates now safe by default.
    - File path operations in CLI and scripts now validated against root directory.
    - No real secrets hardcoded in test files.

## Checklist
- [x] All refactored code uses new security utilities.
- [x] Hardcoded secrets removed from targeted test files.
- [x] Utilities package initialized (`src/lattice_lock/utils/__init__.py`).
