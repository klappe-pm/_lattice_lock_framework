# Prompt 4.2.2 - Advanced Usage Guides

**Tool:** Claude Code Website
**Epic:** 4.2 - Tutorials and Guides
**Phase:** 4 - Documentation & Pilot

## Context

Experienced users need advanced guides covering complex scenarios, customization options, and best practices for production deployments. These guides build on the getting started tutorial.

## Goal

Create advanced usage guides for experienced Lattice Lock users.

## Steps

1. Create `developer_documentation/guides/` directory:
   ```
   guides/
   ├── advanced_validation.md
   ├── custom_rules.md
   ├── multi_project.md
   ├── production_deployment.md
   ├── model_orchestration.md
   └── troubleshooting_advanced.md
   ```

2. Create `advanced_validation.md`:
   - Complex constraint patterns
   - Cross-entity validation
   - Custom ensures clauses
   - Validation performance optimization

3. Create `custom_rules.md`:
   - Creating custom Sheriff rules
   - Custom Gauntlet test generators
   - Rule configuration in lattice.yaml
   - Sharing rules across projects

4. Create `multi_project.md`:
   - Monorepo setup
   - Shared schema definitions
   - Cross-project validation
   - Dependency management

5. Create `production_deployment.md`:
   - Production configuration
   - Security hardening
   - Monitoring and alerting
   - Scaling considerations

6. Create `model_orchestration.md`:
   - Model selection strategies
   - Cost optimization
   - Custom routing rules
   - Multi-model workflows

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `scripts/` (owned by various tools)

## Success Criteria

- Guides cover advanced use cases
- Examples are production-ready
- Best practices clearly stated
- Troubleshooting included

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Include real-world examples
- Reference API documentation
- Include performance considerations
