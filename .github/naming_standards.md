# File and Folder Naming Standards

This document defines the mandatory naming conventions for all files and folders in the Lattice Lock Framework repository.

**Version:** 1.0.0  
**Last Updated:** 2026-01-01  
**Status:** MANDATORY - All files and folders must follow these conventions

## Core Principle

**Use `snake_case` for all files and folders unless otherwise specified.**

## Naming Conventions by Type

### Directories (Folders)

**Rule:** All lowercase with underscores between words

✅ **Correct:**
- `agent_definitions/`
- `business_review_agent/`
- `developer_documentation/`
- `.github/`

❌ **Incorrect:**
- `Agent Definitions/` (spaces, uppercase)
- `agent-definitions/` (kebab-case)
- `agentDefinitions/` (camelCase)
- `AgentDefinitions/` (PascalCase)

### Documentation Files (.md)

**Rule:** All lowercase with underscores between words

✅ **Correct:**
- `naming_standards.md`
- `labels.md`
- `pull_request_template.md`
- `contributing.md`
- `agent_glossary.md`

❌ **Incorrect:**
- `LABELS.md` (uppercase)
- `naming-standards.md` (kebab-case)
- `namingStandards.md` (camelCase)

**Exception:** `README.md`, `LICENSE.md`, `CONTRIBUTING.md` (standard GitHub files may use uppercase)

### Python Files (.py)

**Rule:** All lowercase with underscores between words

✅ **Correct:**
- `structure.py`
- `prompt_validator.py`
- `convention_checker.py`
- `__init__.py`

❌ **Incorrect:**
- `structureValidator.py` (camelCase)
- `StructureValidator.py` (PascalCase)
- `structure-validator.py` (kebab-case)

**Note:** Python class names inside files should use `PascalCase` per PEP 8:
```python
# File: prompt_validator.py
class PromptValidator:  # PascalCase for class names
    pass
```

### Configuration Files

**Rule:** Follow ecosystem conventions

✅ **Correct:**
- `pyproject.toml` (Python standard)
- `package.json` (npm standard)
- `.pre-commit-config.yaml` (tool standard)
- `dependabot.yml` (GitHub standard)
- `.gitignore` (Git standard)

### YAML/JSON Files

**Rule:** All lowercase with underscores between words

✅ **Correct:**
- `engineering_agent_definition.yaml`
- `business_review_agent_definition.yaml`
- `pr_comments.json`

❌ **Incorrect:**
- `engineeringAgentDefinition.yaml` (camelCase)
- `Engineering-Agent-Definition.yaml` (kebab-case with caps)

### Shell Scripts (.sh)

**Rule:** All lowercase with underscores between words

✅ **Correct:**
- `check_no_secrets.sh`
- `deploy.sh`
- `setup_environment.sh`

❌ **Incorrect:**
- `checkNoSecrets.sh` (camelCase)
- `check-no-secrets.sh` (kebab-case)

### JavaScript/TypeScript Files

**Rule:** Use camelCase for files, PascalCase for React components

✅ **Correct:**
- `projectHelpers.js`
- `projectAPI.js`
- `ProjectCard.jsx` (React component)
- `ModelRegistry.jsx` (React component)

❌ **Incorrect for utilities:**
- `project_helpers.js` (snake_case not typical for JS)
- `ProjectHelpers.js` (PascalCase for non-components)

### GitHub-Specific Files

**Rule:** Follow GitHub conventions (usually lowercase with underscores)

✅ **Correct:**
- `.github/labels.md`
- `.github/pull_request_template.md`
- `.github/dependabot.yml`
- `.github/workflows/ci.yml`
- `.github/CODEOWNERS`

## Naming Patterns for Specific File Types

### Agent Definition Files

**Pattern:** `{category}_agent_{subagent}_definition.{yaml|yml}`

✅ **Correct:**
- `engineering_agent_definition.yaml`
- `engineering_agent_backend_developer_definition.yaml`
- `business_review_agent_data_quality_manager_definition.yaml`

❌ **Incorrect:**
- `backend_developer.yaml` (missing category prefix)
- `Engineering_Agent_Definition.yaml` (incorrect casing)

### Test Files

**Pattern:** `test_{module_name}.py`

✅ **Correct:**
- `test_prompt_validator.py`
- `test_validator_structure.py`
- `test_cli_init.py`

### Template Files

**Pattern:** `{name}.{ext}.j2` (for Jinja2 templates)

✅ **Correct:**
- `codebuild_project.yml.j2`
- `deployment_template.yaml.j2`

## Special Cases and Exceptions

### Standard Files (Allowed Uppercase)
These files follow established conventions and may use uppercase:
- `README.md`
- `LICENSE.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `CODEOWNERS`
- `Makefile`

### Environment Variables
- Use SCREAMING_SNAKE_CASE for environment variable names
- File: `.env.example` (lowercase)
- Variables inside: `API_KEY`, `DATABASE_URL`, `AWS_REGION`

### Constants in Python
- Use SCREAMING_SNAKE_CASE for constants
- Example: `MAX_RETRIES = 3`, `DEFAULT_TIMEOUT = 30`

## Validation and Enforcement

### Automated Checks

The repository uses automated validation via pre-commit hooks:

1. **Structure Validator** (`lattice-structure-check`)
   - Validates directory structure
   - Checks file locations

2. **Naming Validator** (`lattice-naming-check`)
   - Enforces snake_case for Python files, directories, and docs
   - Validates agent definition naming patterns
   - Checks for prohibited patterns (spaces, mixed case)

### Pre-Commit Configuration

See `.pre-commit-config.yaml` for the complete configuration.

### Running Checks Manually

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run naming checks only
python3 -m lattice_lock.validator.structure --naming-only
```

## Code Style Standards

### Python (PEP 8 Compliant)

**Configuration:** See `pyproject.toml`

- **Line length:** 100 characters
- **Formatters:** Black, isort
- **Linter:** Ruff
- **Files:** `snake_case`
- **Classes:** `PascalCase`
- **Functions/Methods:** `snake_case`
- **Constants:** `SCREAMING_SNAKE_CASE`
- **Private methods:** `_leading_underscore`

**Example:**
```python
# File: prompt_validator.py
MAX_PROMPT_LENGTH = 1000  # Constant

class PromptValidator:  # Class
    def validate_prompt(self, prompt_text: str) -> bool:  # Method
        return len(prompt_text) <= MAX_PROMPT_LENGTH
    
    def _internal_check(self):  # Private method
        pass
```

### JavaScript/TypeScript

- **Files (utilities):** `camelCase`
- **Files (React components):** `PascalCase`
- **Variables/Functions:** `camelCase`
- **Classes/Components:** `PascalCase`
- **Constants:** `SCREAMING_SNAKE_CASE` or `camelCase` (project dependent)

**Example:**
```javascript
// File: projectHelpers.js
const MAX_PROJECTS = 100;

function getProjectById(projectId) {
    // ...
}

// File: ProjectCard.jsx
export function ProjectCard({ project }) {
    // ...
}
```

### YAML Files

- **File names:** `snake_case`
- **Keys:** `snake_case` or `kebab-case` (be consistent within file)

**Example:**
```yaml
# File: engineering_agent_definition.yaml
agent_name: engineering_agent
agent_type: base_agent
sub_agents:
  - backend_developer
  - frontend_developer
```

## Migration Guide

### Renaming Existing Files

If you need to rename files to comply with these standards:

```bash
# Example: Rename uppercase to lowercase
mv .github/LABELS.md .github/labels.md

# Example: Change kebab-case to snake_case
mv agent-definitions/ agent_definitions/
```

### Bulk Renaming Script

For bulk operations, use this pattern:

```bash
# Find files with uppercase in .github (excluding standard files)
find .github -type f -name "*.md" ! -name "README.md" ! -name "LICENSE.md" ! -name "CONTRIBUTING.md"

# Rename to lowercase
for file in $(find .github -type f -name "*.md"); do
    lowercase=$(echo "$file" | tr '[:upper:]' '[:lower:]')
    [ "$file" != "$lowercase" ] && mv "$file" "$lowercase"
done
```

## Quick Reference

| Type | Convention | Example |
|------|------------|---------|
| Directories | snake_case | `agent_definitions/` |
| Python files | snake_case | `prompt_validator.py` |
| Python classes | PascalCase | `class PromptValidator` |
| Python functions | snake_case | `def validate_prompt()` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES = 3` |
| Markdown files | snake_case | `naming_standards.md` |
| YAML files | snake_case | `agent_definition.yaml` |
| JS utilities | camelCase | `projectHelpers.js` |
| React components | PascalCase | `ProjectCard.jsx` |
| Shell scripts | snake_case | `deploy.sh` |

## References

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Single source of truth for all contribution standards

## Questions or Exceptions?

If you believe a file should be an exception to these rules, please:
1. Open an issue explaining the use case
2. Wait for approval before committing the exception
3. Document the exception in this file
