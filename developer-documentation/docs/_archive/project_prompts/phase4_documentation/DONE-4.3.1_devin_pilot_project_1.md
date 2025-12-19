# Prompt 4.3.1 - Pilot Project 1 Setup

**Tool:** Devin AI
**Epic:** 4.3 - Pilot Projects
**Phase:** 4 - Documentation & Pilot

## Context

The Lattice Lock Framework needs real-world pilot projects to validate the framework in production scenarios. Pilot Project 1 focuses on a typical web API service with database persistence.

## Goal

Set up and configure Pilot Project 1 - a REST API service using Lattice Lock governance.

## Steps

1. Create `pilot_projects/api_service/` directory:
   ```
   api_service/
   ├── lattice.yaml
   ├── src/
   │   ├── api/
   │   ├── models/
   │   └── services/
   ├── tests/
   ├── .github/workflows/
   └── README.md
   ```

2. Create `lattice.yaml` with realistic entities:
   - User entity with authentication fields
   - Product entity with inventory constraints
   - Order entity with status workflow
   - Payment entity with amount validation

3. Configure CI/CD:
   - GitHub Actions workflow using Lattice Lock
   - Pre-commit hooks for validation
   - Automated testing on PR

4. Implement sample API endpoints:
   - CRUD operations for each entity
   - Business logic with constraints
   - Error handling with Lattice Lock errors

5. Document pilot project:
   - Setup instructions
   - Architecture overview
   - Lessons learned
   - Metrics collected

6. Create validation report:
   - Sheriff validation results
   - Gauntlet test coverage
   - Performance benchmarks

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- Pilot project passes all Lattice Lock validation
- CI/CD pipeline works correctly
- Documentation complete
- Metrics collected for framework improvement

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use realistic data models
- Document any framework issues discovered
- Collect feedback for framework improvement
