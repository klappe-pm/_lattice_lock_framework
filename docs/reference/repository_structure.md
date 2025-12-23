# Repository Structure Standards

This document mandates file naming conventions, folder structures, and file storage locations for the Lattice Lock Framework. **All contributions must adhere to these standards.**

**Version:** 3.0.0
**Last Updated:** 2025-11-28
**Status:** MANDATORY - All files must follow these conventions

## Table of Contents

1. [Root Directory Structure](#root-directory-structure)
2. [File Naming Conventions](#file-naming-conventions)
3. [Folder Organization Standards](#folder-organization-standards)
4. [Agent Definition Structure](#agent-definition-structure)
5. [Documentation Standards](#documentation-standards)
6. [Configuration Files](#configuration-files)
7. [Code Organization](#code-organization)
8. [Legacy and Migration](#legacy-and-migration)
9. [Enforcement](#enforcement)

---

## Root Directory Structure

### Mandatory Root-Level Files

Lattice Lock Framework/

├──.gitignore # Git ignore patterns (MANDATORY)

├── LICENSE.md # Project license (MANDATORY)

├── README.md # Project overview (MANDATORY)

├── version.txt # Current version number

└── directory/ # Repository standards and plans

	├── repository_structure_standards.md

	└── repository_organization_recommendations.md

### Root-Level Directories (Standard Structure)

Lattice Lock Framework/

├── agent_definitions/ # Agent definition files (YAML/Markdown)

├── agent_interactions/ # Interaction protocols and logs

├── agent_memory/ # Memory structures and storage

├── agent_specifications/ # High-level agent specs and templates

├── agent_workflows/ # Defined workflows and processes

├── context/ # Contextual information and global state

├── developer_documentation/ # Developer guides and API docs

├── directory/ # Repository meta-documentation

├── instructions/ # AI/LLM specific instructions

├── specifications/ # Framework specifications

├── scripts/ # Utility and automation scripts

└── src/ # Source code (Python modules)

**DO NOT CREATE:**
- Temporary files at root level
- Personal/private files at root level
- Non-standard top-level directories without approval

## File Naming Conventions

### General Rules

1. **Use snake_case for ALL directories and files**
   - ✅ `agent_definitions/`
   - ✅ `business_review_agent/`
   - ✅ `engineering_agent_definition.yaml`
   - ❌ `Agent Definitions/`
   - ❌ `agent-definitions/`
   - ❌ `business-review-agent/`

2. **Use descriptive, full words** (avoid abbreviations unless standard)
   - ✅ `engineering_agent_database_administrator_definition.yaml`
   - ❌ `eng_agent_dba_def.yaml`

3. **File extensions must match content type**
   - `.yaml` or `.yml` for YAML files
   - `.md` for Markdown files
   - `.json` for JSON files
   - `.py` for Python scripts
   - `.sh` for shell scripts

### Agent Definition Files

**Pattern:** `{agent_category}_{agent_name}_definition.{ext}`

**Examples:**
- ✅ `engineering_agent_backend_developer_definition.yaml`
- ✅ `business_review_agent_definition.yaml`
- ❌ `backend_developer.yaml` (missing category prefix)

### Documentation Files

**Pattern:** `{descriptive_name}.md` or `{prefix}_{name}.md`

**Examples:**
- ✅ `agent_glossary.md`
- ✅ `agent_specification_v2_1.md`
- ❌ `glossary.md` (too generic)

---

## Folder Organization Standards

### agent_definitions/ Directory Structure

**MANDATORY STRUCTURE:**

agent_definitions/

├── {agent_category}/ # One folder per agent category (snake_case)

│ ├── {category}_agent_definition.yaml

│ ├── {category}_agent_{sub_agent}_definition.yaml

│ └── …

├── templates/ # (Optional) Templates for new agents

└── …

**Rules:**
- ✅ Agent categories use **snake_case** (e.g., `business_review_agent`).
- ✅ Definition files reside directly within their category folder.

### developer_documentation/ Directory Structure

**MANDATORY STRUCTURE:**

```
developer_documentation/
├── architecture/
├── commands/
├── development/
├── features/
├── getting_started/
├── models/
└── testing/
```

**Rules:**
- ✅ Use **snake_case** for documentation subdirectories.
- ✅ All files must be `.md` (Markdown).

### scripts/ Directory

**MANDATORY STRUCTURE:**

```
scripts/
├── setup/
├── validation/
├── transformation/
└── utilities/
```

**Rules:**
- ✅ All scripts must have appropriate shebang.
- ✅ Python scripts: `#!/usr/bin/env python3`
- ✅ Shell scripts: `#!/bin/bash`

---

## Agent Definition Structure

### File Location Rules

**MANDATORY:**
- All agent definitions: `agent_definitions/{category}/`
- One agent category per top-level folder in `agent_definitions/`

**Example:**

agent_definitions/

├── engineering_agent/

│ ├── engineering_agent_definition.yaml

│ └── engineering_agent_backend_developer_definition.yaml

├── business_review_agent/

│ └── business_review_agent_definition.yaml

### Agent Category Naming

**Pattern:** `{category_name}_agent`

**Standard Categories:**
- `business_review_agent`
- `cloud_agent`
- `content_agent`
- `context_agent`
- `engineering_agent`
- `google_apps_script_agent`
- `product_agents` (plural allowed for collections)
- `project_agent`
- `public_relations_agent`
- `research_agent`
- `ux_agent`

## Documentation Standards

### Markdown File Naming

**Pattern:** `snake_case.md` or `kebab-case.md` (be consistent within folders)

**Examples:**
- ✅ `agent_analysis_report.md`
- ✅ `catalog.md`

### Documentation Content Structure

All Markdown documentation must include:

1. **Title** (H1): Clear, descriptive title
2. **Sections** with clear headings (H2, H3)
3. **Last Updated** date (optional but recommended)

## Configuration Files

### Location Rules

**Root-Level Configs:**
- ✅ `.gitignore`
- ✅ `LICENSE.md`
- ✅ `README.md`

**Environment Configs:**
- ❌ DO NOT commit `.env` files
- ✅ Use `.env.example` as template

## Code Organization

### Python Files

**Location:**
- Main code: `src/`
- Scripts: `scripts/`
- Tests: `tests/` (if applicable)

**Naming:**
- ✅ Use `snake_case` for Python files and modules
- ✅ Use `PascalCase` for class names

## Legacy and Migration

### Legacy Repository (`power-prompts`)

**Status:** LEGACY / EXTERNAL REFERENCE
- The original implementation lives in the external [power-prompts repository](https://github.com/klappe-pm/power-prompts).
- **DO NOT** add new work there.
- Reference only for historical context on original design decisions.

## Enforcement

### Pre-Commit Checks

Before committing, verify:

1. ✅ Files are in the correct new directory structure (`agent_definitions`, etc.).
2. ✅ File names follow conventions.
3. ✅ No prohibited patterns (spaces, special chars).


# Repository Structure Standards

This document mandates file naming conventions, folder structures, and file storage locations for the Lattice Lock Framework. **All contributions must adhere to these standards.**

**Version:** 3.0.0
**Last Updated:** 2025-11-28
**Status:** MANDATORY - All files must follow these conventions

## Table of Contents

1. [Root Directory Structure](#root-directory-structure)
2. [File Naming Conventions](#file-naming-conventions)
3. [Folder Organization Standards](#folder-organization-standards)
4. [Agent Definition Structure](#agent-definition-structure)
5. [Documentation Standards](#documentation-standards)
6. [Configuration Files](#configuration-files)
7. [Code Organization](#code-organization)
8. [Legacy and Migration](#legacy-and-migration)
9. [Enforcement](#enforcement)

---

## Root Directory Structure

### Mandatory Root-Level Files

Lattice Lock Framework/

├──.gitignore # Git ignore patterns (MANDATORY)

├── LICENSE.md # Project license (MANDATORY)

├── README.md # Project overview (MANDATORY)

├── version.txt # Current version number

└── directory/ # Repository standards and plans

	├── repository_structure_standards.md

	└── repository_organization_recommendations.md

### Root-Level Directories (Standard Structure)

Lattice Lock Framework/

├── docs/ # Developer guides, Agent Definitions
│   ├── agent_definitions/ # Agent definition files (YAML/Markdown)
│   ├── agent_interactions/ # Interaction protocols and logs
│   ├── agent_memory/ # Memory structures and storage
│   ├── agent_specifications/ # High-level agent specs and templates
│   ├── agent_workflows/ # Defined workflows and processes
│   ├── models/ # Model configuration and registry
│   └── specifications/ # Framework specifications
│
├── context/ # Contextual information and global state

├── directory/ # Repository meta-documentation

├── instructions/ # AI/LLM specific instructions

├── specifications/ # Framework specifications

├── scripts/ # Utility and automation scripts

└── src/ # Source code (Python modules)

**DO NOT CREATE:**
- Temporary files at root level
- Personal/private files at root level
- Non-standard top-level directories without approval

## File Naming Conventions

### General Rules

1. **Use snake_case for ALL directories and files**
   - ✅ `agent_definitions/`
   - ✅ `business_review_agent/`
   - ✅ `engineering_agent_definition.yaml`
   - ❌ `Agent Definitions/`
   - ❌ `agent-definitions/`
   - ❌ `business-review-agent/`

2. **Use descriptive, full words** (avoid abbreviations unless standard)
   - ✅ `engineering_agent_database_administrator_definition.yaml`
   - ❌ `eng_agent_dba_def.yaml`

3. **File extensions must match content type**
   - `.yaml` or `.yml` for YAML files
   - `.md` for Markdown files
   - `.json` for JSON files
   - `.py` for Python scripts
   - `.sh` for shell scripts

### Agent Definition Files

**Pattern:** `{agent_category}_{agent_name}_definition.{ext}`

**Examples:**
- ✅ `engineering_agent_backend_developer_definition.yaml`
- ✅ `business_review_agent_definition.yaml`
- ❌ `backend_developer.yaml` (missing category prefix)

### Documentation Files

**Pattern:** `{descriptive_name}.md` or `{prefix}_{name}.md`

**Examples:**
- ✅ `agent_glossary.md`
- ✅ `agent_specification_v2_1.md`
- ❌ `glossary.md` (too generic)

---

## Folder Organization Standards

### agent_definitions/ Directory Structure

**MANDATORY STRUCTURE:**

agent_definitions/

├── {agent_category}/ # One folder per agent category (snake_case)

│ ├── {category}_agent_definition.yaml

│ ├── {category}_agent_{sub_agent}_definition.yaml

│ └── …

├── templates/ # (Optional) Templates for new agents

└── …

**Rules:**
- ✅ Agent categories use **snake_case** (e.g., `business_review_agent`).
- ✅ Definition files reside directly within their category folder.

### developer_documentation/ Directory Structure

**MANDATORY STRUCTURE:**

```
developer_documentation/
├── architecture/
├── commands/
├── development/
├── features/
├── getting_started/
├── models/
└── testing/
```

**Rules:**
- ✅ Use **snake_case** for documentation subdirectories.
- ✅ All files must be `.md` (Markdown).

### scripts/ Directory

**MANDATORY STRUCTURE:**

```
scripts/
├── setup/
├── validation/
├── transformation/
└── utilities/
```

**Rules:**
- ✅ All scripts must have appropriate shebang.
- ✅ Python scripts: `#!/usr/bin/env python3`
- ✅ Shell scripts: `#!/bin/bash`

---

## Agent Definition Structure

### File Location Rules

**MANDATORY:**
- All agent definitions: `agent_definitions/{category}/`
- One agent category per top-level folder in `agent_definitions/`

**Example:**

agent_definitions/

├── engineering_agent/

│ ├── engineering_agent_definition.yaml

│ └── engineering_agent_backend_developer_definition.yaml

├── business_review_agent/

│ └── business_review_agent_definition.yaml

### Agent Category Naming

**Pattern:** `{category_name}_agent`

**Standard Categories:**
- `business_review_agent`
- `cloud_agent`
- `content_agent`
- `context_agent`
- `engineering_agent`
- `google_apps_script_agent`
- `product_agents` (plural allowed for collections)
- `project_agent`
- `public_relations_agent`
- `research_agent`
- `ux_agent`

## Documentation Standards

### Markdown File Naming

**Pattern:** `snake_case.md` or `kebab-case.md` (be consistent within folders)

**Examples:**
- ✅ `agent_analysis_report.md`
- ✅ `catalog.md`

### Documentation Content Structure

All Markdown documentation must include:

1. **Title** (H1): Clear, descriptive title
2. **Sections** with clear headings (H2, H3)
3. **Last Updated** date (optional but recommended)

## Configuration Files

### Location Rules

**Root-Level Configs:**
- ✅ `.gitignore`
- ✅ `LICENSE.md`
- ✅ `README.md`

**Environment Configs:**
- ❌ DO NOT commit `.env` files
- ✅ Use `.env.example` as template

## Code Organization

### Python Files

**Location:**
- Main code: `src/`
- Scripts: `scripts/`
- Tests: `tests/` (if applicable)

**Naming:**
- ✅ Use `snake_case` for Python files and modules
- ✅ Use `PascalCase` for class names

## Legacy and Migration

### Legacy Repository (`power-prompts`)

**Status:** LEGACY / EXTERNAL REFERENCE
- The original implementation lives in the external [power-prompts repository](https://github.com/klappe-pm/power-prompts).
- **DO NOT** add new work there.
- Reference only for historical context on original design decisions.

## Enforcement

### Pre-Commit Checks

Before committing, verify:

1. ✅ Files are in the correct new directory structure (`agent_definitions`, etc.).
2. ✅ File names follow conventions.
3. ✅ No prohibited patterns (spaces, special chars).
