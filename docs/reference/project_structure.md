---
title: project_structure
type: reference
status: stable
categories: [reference, configuration]
sub_categories: [project_structure]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [ref-structure-001]
tags: [reference, project_structure, directories, configuration]
---

# Standard Project Structure

This document defines the standard directory structure for Lattice Lock projects.

## Required Root Directories

### docs/
Project documentation following a structured hierarchy:
- `01_concepts/` - Conceptual documentation, features, architecture
- `03_technical/` - Technical documentation, API references, CLI documentation
- `04_meta/` - Meta documentation about documentation standards
- `README.md` - Documentation overview

### src/
Source code organized by purpose:
- `src/shared/` - Shared utilities and types
- `src/services/` - Service implementations
- `src/<project_name>/` - Main project package (for libraries)
- `__init__.py` files in all packages

### scripts/
Utility and automation scripts:
- Build scripts
- Deployment scripts
- Development utilities
- Migration scripts
- Must follow `snake_case` naming convention

### tests/
Test suites:
- `test_*.py` - Test files following pytest conventions
- `conftest.py` - Pytest configuration
- `fixtures/` - Test fixtures
- `integration/` - Integration tests
- `unit/` - Unit tests

### agents/ (Optional)
Agent definitions and configurations:
- `agent_definitions/` - Agent YAML definitions organized by category
- `agent_diagrams/` - Agent workflow diagrams
- `agent_workflows/` - Agent workflow specifications
- `agents_config/` - Agent configuration files
- `markdown/` - Generated agent markdown files

## Required Root Files

### .gitignore
Standard Python .gitignore with Lattice Lock specific entries

### README.md
Project README with:
- Project overview
- Installation instructions
- Usage examples
- Documentation links

### lattice.yaml
Lattice Lock configuration file (v2.1 format):
- `version` - Schema version (v2.1)
- `generated_module` - Name for generated types module
- `entities` - Entity definitions with fields
- `config` - Governance rules

## Optional Directories

### .github/
GitHub specific configuration:
- `workflows/` - GitHub Actions workflows
- `ISSUE_TEMPLATE/` - Issue templates
- `PULL_REQUEST_TEMPLATE.md` - PR template

### project_management/
Project management artifacts:
- Roadmaps
- Sprint planning
- Meeting notes
- Analysis documents

### frontend/ (For full-stack projects)
Frontend application code

### terraform/ or infrastructure/
Infrastructure as code

### shared/
Shared resources across multiple projects

## File Naming Conventions

All files and folders must follow `snake_case`:
- ✓ `my_script.py`
- ✓ `deploy_app.sh`
- ✗ `myScript.py`
- ✗ `deploy-app.sh`

Exceptions:
- `README.md`
- `LICENSE.md`
- `Dockerfile`
- `Makefile`
- Files in `.github/workflows/` (can use hyphens)

## Agent Definitions Structure

When including agents, follow this hierarchy:

```
agents/
├── agent_definitions/
│   ├── agents_engineering/
│   │   ├── engineering_agent_definition.yaml
│   │   └── engineering_...
│   ├── agents_product_management/
│   │   └── product_management_agent_definition.yaml
│   ├── agents_business_review/
│   └── ...
├── agent_diagrams/
│   ├── agent_lifecycle.md
│   └── ...
├── agent_workflows/
└── agents_config/
```

## Validation

All projects are validated against this structure using:
```bash
lattice-lock validate
```

The validator checks:
1. Required directories exist
2. Required files exist
3. File naming conventions
4. lattice.yaml schema compliance
