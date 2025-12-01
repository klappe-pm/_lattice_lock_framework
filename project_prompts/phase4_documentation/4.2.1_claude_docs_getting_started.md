# Prompt 4.2.1 - Getting Started Tutorial

**Tool:** Claude Code Website
**Epic:** 4.2 - Tutorials and Guides
**Phase:** 4 - Documentation & Pilot

## Context

New users need a step-by-step tutorial that walks them through creating their first Lattice Lock project. This tutorial should be hands-on and result in a working project with validation passing.

## Goal

Create a comprehensive getting started tutorial for new Lattice Lock users.

## Steps

1. Create `developer_documentation/tutorials/` directory:
   ```
   tutorials/
   ├── getting_started.md
   ├── first_project.md
   ├── adding_validation.md
   └── ci_integration.md
   ```

2. Create `getting_started.md`:
   - Prerequisites checklist
   - Installation verification
   - Environment setup
   - First command execution
   - Expected output

3. Create `first_project.md`:
   - Create new project with `lattice-lock init`
   - Explore generated structure
   - Understand lattice.yaml
   - Add first entity
   - Run validation

4. Create `adding_validation.md`:
   - Add constraints to entities
   - Add ensures clauses
   - Run Sheriff validation
   - Run Gauntlet tests
   - Fix validation errors

5. Create `ci_integration.md`:
   - Add GitHub Actions workflow
   - Configure validation in CI
   - Handle CI failures
   - Best practices for CI

6. Include:
   - Code snippets that can be copy-pasted
   - Expected output at each step
   - Common mistakes and how to fix them
   - Links to reference documentation

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `scripts/` (owned by various tools)

## Success Criteria

- Tutorial works for complete beginners
- All code examples are tested and working
- Users end with a working project
- Links to next steps provided

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Test tutorial on fresh environment
- Use screenshots where helpful
- Keep language accessible
