# Prompt 4.3.2 - Pilot Project 2 Setup

**Tool:** Devin AI
**Epic:** 4.3 - Pilot Projects
**Phase:** 4 - Documentation & Pilot

## Context

Pilot Project 2 focuses on a different use case - a data processing pipeline with complex validation requirements. This validates Lattice Lock's applicability beyond web APIs.

## Goal

Set up and configure Pilot Project 2 - a data processing pipeline using Lattice Lock governance.

## Steps

1. Create `pilot_projects/data_pipeline/` directory:
   ```
   data_pipeline/
   ├── lattice.yaml
   ├── src/
   │   ├── extractors/
   │   ├── transformers/
   │   ├── loaders/
   │   └── validators/
   ├── tests/
   ├── .github/workflows/
   └── README.md
   ```

2. Create `lattice.yaml` with pipeline entities:
   - DataSource entity with connection validation
   - DataRecord entity with schema constraints
   - TransformRule entity with expression validation
   - PipelineConfig entity with dependency validation

3. Configure CI/CD:
   - GitHub Actions workflow for pipeline validation
   - Data contract testing
   - Schema evolution checks

4. Implement sample pipeline:
   - CSV/JSON data extraction
   - Data transformation with constraints
   - Validation at each stage
   - Error handling and recovery

5. Document pilot project:
   - Pipeline architecture
   - Data flow diagrams
   - Validation checkpoints
   - Performance metrics

6. Create validation report:
   - Data quality metrics
   - Schema compliance rates
   - Processing time benchmarks

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- `.pre-commit-config.yaml` (owned by Codex CLI)

## Success Criteria

- Pipeline passes all Lattice Lock validation
- Data contracts enforced at each stage
- Documentation complete
- Metrics collected for framework improvement

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use realistic data processing scenarios
- Document any framework issues discovered
- Compare with traditional data validation approaches
