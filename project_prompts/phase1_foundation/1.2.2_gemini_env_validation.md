# Prompt 1.2.2 - Environment Validation

**Tool:** Gemini CLI
**Epic:** 1.2 - Configuration Validator
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework requires `.env` files for configuration but must ensure no plaintext secrets are committed. The framework specification (Section 3.3.2) requires validation that `.env` files don't contain secrets and that required variables are present.

## Goal

Implement environment file validation to detect plaintext secrets and verify required variables.

## Steps

1. Create `src/lattice_lock_validator/env.py` implementing:
   - `validate_env_file(file_path: str, required_vars: list[str] | None = None) -> ValidationResult`
   - Detect potential plaintext secrets (API keys, passwords, tokens)
   - Check for required environment variables
   - Validate variable naming conventions (UPPER_SNAKE_CASE)

2. Implement secret detection patterns:
   - API key patterns: `*_API_KEY`, `*_SECRET`, `*_TOKEN`
   - Password patterns: `*_PASSWORD`, `*_PASS`
   - Credential patterns: `*_CREDENTIAL`, `*_AUTH`
   - Flag secrets that appear to have actual values (not placeholders)

3. Define placeholder patterns that are acceptable:
   - `your-*-here`, `<placeholder>`, `xxx`, `changeme`
   - Empty values
   - References to secret managers: `vault:*`, `aws-secrets:*`

4. Create default required variables list:
   - `ORCHESTRATOR_STRATEGY`
   - `LOG_LEVEL`

5. Write unit tests in `tests/test_env_validator.py`:
   - Test valid .env with placeholders passes
   - Test .env with plaintext secret fails
   - Test missing required variable fails
   - Test invalid variable naming warns
   - Test secret manager references pass

6. Integrate with `ValidationResult` from schema.py

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Plaintext secrets detected with specific error messages
- Missing required variables reported
- Placeholder values accepted
- Secret manager references accepted
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use python-dotenv for parsing .env files
- Be conservative: better to warn than miss a secret
