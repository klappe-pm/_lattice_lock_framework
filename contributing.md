# Contributing to Lattice Lock Framework

**THE SINGLE SOURCE OF TRUTH FOR ALL CONTRIBUTION STANDARDS**

This document contains all coding standards, naming conventions, workflow requirements, and contribution guidelines for the Lattice Lock Framework. Both humans and AI agents should reference this file exclusively.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Code Review Requirements](#code-review-requirements)
3. [File Naming Conventions](#file-naming-conventions)
4. [Repository Structure](#repository-structure)
5. [Branching & Workflow](#branching--workflow)
6. [Pull Request Process](#pull-request-process)
7. [Commit Standards](#commit-standards)
8. [Code Standards](#code-standards)
9. [Governance Workflow](#governance-workflow)
10. [Local Tooling](#local-tooling)

---

## Quick Start

**TL;DR:**
- All file names are **lowercase with underscores** (e.g., `my_file.py`, not `MyFile.py` or `my-file.py`)
- Work in short-lived branches in your fork, open a PR to `main`, squash-merge, auto-delete branch
- No direct pushes to `origin/main`. Local pre-push hook blocks non-`main` pushes to `origin`
- CI must pass (tests, lint, typecheck) before merge
- `@greptileai` is automatically tagged for review on all PRs
- Required PR labels: one type (`feat`, `fix`, `chore`, `docs`, `refactor`) + one source (`human`, `llm`, `devin`)

**Why this approach:**
- Keep history linear and readable (one commit per change on `main`)
- Avoid branch drift and stale remote branches
- Make it easy for humans and AI agents to contribute safely

---

## Code Review Requirements

### Automated Review Assignment

All files in this repository require review from `@greptileai`. This is enforced via the `.github/CODEOWNERS` file.

### Human Review

- At least one approving human review is recommended for non-trivial changes
- Reviewers should verify adherence to this contributing.md document

---

## File Naming Conventions

### MANDATORY RULE: All Lowercase with Underscores

**All file names must be lowercase with underscores between words.**

**Correct Examples:**
- ✅ `my_module.py`
- ✅ `user_service.py`
- ✅ `api_client.ts`
- ✅ `database_migration_001.sql`
- ✅ `contributing.md`
- ✅ `readme.md`

**Incorrect Examples:**
- ❌ `MyModule.py` (uppercase)
- ❌ `UserService.py` (uppercase)
- ❌ `API_Client.ts` (uppercase)
- ❌ `my-module.py` (hyphens instead of underscores)
- ❌ `CONTRIBUTING.md` (uppercase)
- ❌ `README.md` (uppercase)

### Exceptions

**The following root-level files are allowed to have uppercase or special naming for compatibility:**
- `LICENSE.md` (GitHub/legal convention)
- `Makefile` (Make convention)
- `Dockerfile` (Docker convention)
- `.gitignore`, `.env.example` (dotfiles)

### Directory Naming

**All directories must use lowercase with underscores:**
- ✅ `agent_definitions/`
- ✅ `business_review_agent/`
- ✅ `project_management/`
- ❌ `Agent Definitions/` (spaces and uppercase)
- ❌ `agent-definitions/` (hyphens)
- ❌ `business-review-agent/` (hyphens)

### File Extensions

File extensions must match content type:
- `.yaml` or `.yml` for YAML files
- `.md` for Markdown files
- `.json` for JSON files
- `.py` for Python scripts
- `.sh` for shell scripts
- `.ts` for TypeScript files
- `.js` for JavaScript files

### Descriptive Naming

Use descriptive, full words (avoid abbreviations unless standard):
- ✅ `engineering_agent_database_administrator_definition.yaml`
- ❌ `eng_agent_dba_def.yaml`

### Agent Definition Files

**Pattern:** `{agent_category}_{agent_name}_definition.{ext}`

**Examples:**
- ✅ `engineering_agent_backend_developer_definition.yaml`
- ✅ `business_review_agent_definition.yaml`
- ❌ `backend_developer.yaml` (missing category prefix)

### Documentation Files

**Pattern:** `{descriptive_name}.md`

**Examples:**
- ✅ `agent_glossary.md`
- ✅ `agent_specification_v2_1.md`
- ❌ `glossary.md` (too generic)

---

## Repository Structure

### Root Directory Structure

```
lattice-lock-framework/
├── .git/                          # Version control
├── .github/                       # GitHub config (workflows, CODEOWNERS, PR template)
├── .githooks/                     # Git hooks
├── .gitignore                     # VCS ignore patterns (MANDATORY)
├── contributing.md                # This file - single source of truth (MANDATORY)
├── license.md                     # Project license (MANDATORY)
├── Makefile                       # Build automation
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Container orchestration
├── pyproject.toml                 # Python project configuration
├── requirements.in                # Dependency specifications
├── requirements.lock              # Locked dependencies
├── requirements-dev.lock          # Dev dependencies
├── version.txt                    # Version tracking
├── docs/                          # All documentation
├── src/                           # Source code (Python modules)
├── tests/                         # Test suite
├── scripts/                       # Utility and automation scripts
├── frontend/                      # Frontend code
├── infrastructure/                # Infrastructure as code
├── project-management/            # Project planning and tracking
├── diagrams/                      # Architecture diagrams
└── shared/                        # Shared resources
```

### Documentation Structure (`docs/`)

```
docs/
├── agents/                  # Agent-related documentation
│   ├── agent_definitions/   # Agent definition files (YAML/Markdown)
│   ├── agent_memory/        # Memory structures and storage
│   ├── agent_templates/     # Templates for new agents
│   └── agent_workflows/     # Defined workflows and processes
├── architecture/            # System architecture docs
├── database/                # Database documentation
├── design/                  # Design documents
├── examples/                # Code examples and demos
├── features/                # Feature documentation
├── guides/                  # User guides
├── reference/               # API reference docs
├── testing/                 # Testing documentation
└── tutorials/               # Tutorial content
```

### Scripts Structure (`scripts/`)

```
scripts/
├── setup/                   # Setup scripts
├── validation/              # Validation scripts
├── transformation/          # Transformation scripts
├── utilities/               # Various utility scripts
└── migrations/              # Database migrations
```

### Agent Definition Structure

**File Location Rules (MANDATORY):**
- All agent definitions: `docs/agents/agent_definitions/{category}/`
- One agent category per top-level folder

**Example:**
```
docs/agents/agent_definitions/
├── engineering_agent/
│   ├── engineering_agent_definition.yaml
│   └── engineering_agent_backend_developer_definition.yaml
├── business_review_agent/
│   └── business_review_agent_definition.yaml
└── templates/
    └── agent_template.yaml
```

**Standard Agent Categories:**
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

### Files NOT Allowed in Root

**DO NOT CREATE:**
- Temporary files at root level
- Personal/private files at root level
- Test artifacts (use `tests/reports/` or add to `.gitignore`)
- Documentation files (use `docs/` subdirectories)
- Example scripts (use `docs/examples/`)
- Non-standard top-level directories without approval

---

## Branching & Workflow

### Branch Strategy

- **Single permanent branch:** `main`
- **Short-lived branches in forks only**
- Recommended naming: `{actor}/{ticket-or-issue}-{slug}`
  - Examples: `human/1234-doc-fix`, `claude/refactor-logger`, `gemini/ci-cache`, `devin/abc-bugfix`

### Merge Strategy

- **Squash-and-merge only.** Merge commits and rebase merges are disabled at the repository level
- Auto-delete head branches on merge is enabled
- This keeps history linear and readable (one commit per change on `main`)

---

## Pull Request Process

### Opening a PR

1. Open a PR for every change
2. Use the PR template (`.github/pull_request_template.md`)
3. Fill out all required sections:
   - Summary: Describe the change and why it's needed
   - Type: Select one (`feat`, `fix`, `chore`, `docs`, `refactor`)
   - Source: Select one (`human`, `llm`, `devin`)
   - Testing: Confirm lint/typecheck pass, tests added/updated, coverage acceptable
   - Checklist: Confirm targets `main`, labels applied, `@greptileai` tagged

### Required Labels

**The CI policy job will fail if these are missing:**
- **One type label:** `feat`, `fix`, `chore`, `docs`, `refactor`
- **One source label:** `human`, `llm`, `devin`

### Required Checks

All required checks must pass before merge:
- Tests pass
- Lint pass
- Typecheck pass
- CI policy job pass (verifies labels)

Add new checks as needed for your workflow.

### Review Requirements

- `@greptileai` is automatically tagged via CODEOWNERS
- At least one approving human review is recommended

---

## Commit Standards

### Commit Message Format

**Conventional Commits style preferred:**
- `feat:` - New feature
- `fix:` - Bug fix
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `ci:` - CI/CD changes

**Examples:**
```
feat: add model selection caching
fix: resolve race condition in orchestrator
chore: update dependencies
docs: clarify governance workflow
```

### Co-Authorship

When AI agents or tools contribute to a commit, include co-author attribution:

```
feat: implement new validation rule

Co-Authored-By: Warp <agent@warp.dev>
```

Or for other tools:
```
fix: update import paths

Co-Authored-By: Claude <claude@anthropic.com>
Co-Authored-By: GitHub Copilot <copilot@github.com>
```

### Commit Scope

- Keep the scope concise
- Body may include context and follow-up notes
- Reference issues or tickets when applicable

---

## Code Standards

### Python Code

**File Naming:**
- Use `lowercase_with_underscores.py` for Python files and modules
- Use `PascalCase` for class names within files

**File Location:**
- Main code: `src/`
- Scripts: `scripts/`
- Tests: `tests/`

**Script Headers:**
- All Python scripts must include: `#!/usr/bin/env python3`

**Imports:**
- Group imports: standard library, third-party, local
- Use absolute imports from `src/` root
- Avoid circular dependencies

**Type Hints:**
- Use type hints for function signatures
- Use type hints for class attributes

**Documentation:**
- Docstrings for all public classes and functions
- Use Google-style or NumPy-style docstrings consistently

### Shell Scripts

**File Location:**
- Utility scripts: `scripts/`

**Script Headers:**
- All shell scripts must include: `#!/bin/bash`

**Naming:**
- Use `lowercase_with_underscores.sh`

### Documentation

**Markdown File Structure:**

All Markdown documentation must include:
1. **Title** (H1): Clear, descriptive title
2. **Sections** with clear headings (H2, H3)
3. **Last Updated** date (optional but recommended)

**Naming:**
- Use `lowercase_with_underscores.md`

### Configuration Files

**Root-Level Configs (Allowed):**
- `.gitignore`
- `license.md`
- `contributing.md` (this file)
- `pyproject.toml`
- `Makefile`, `Dockerfile`, `docker-compose.yml`

**Environment Configs:**
- ❌ DO NOT commit `.env` files
- ✅ Use `.env.example` as template

---

## Governance Workflow

### Overview

The Lattice Lock Framework uses a governance workflow based on `lattice.yaml` rules. This section describes the end-to-end process.

### Step 1: Define Rules

The `lattice.yaml` file is the constitution of your project. It defines architecture rules and policies.

1. Create a `lattice.yaml` file in your root directory
2. Add rules using the rule definition format

**Example:**
```yaml
version: "2.1"
rules:
  - id: "no-print"
    description: "Use logger instead of print statements in production code."
    severity: "error"
    scope: "src/**/*.py"
    excludes: ["scripts/*", "tests/*"]
    forbids: "node.is_call_to('print')"
```

### Step 2: Compile Policies

Compile your policies into Python artifacts (AST checkers and tests):

```bash
lattice-lock compile
```

You should see output indicating that rules have been generated in `build/lattice_rules.py`.

### Step 3: Validate (Static Analysis)

Static analysis catches violations before you commit:

```bash
lattice-lock validate
```

**Expected output when violations are found:**
```text
[ERROR] no-print: Use logger instead of print statements in production code. (src/bad_code.py:2)
Validation Failed.
```

### Step 4: Test (Runtime Enforcement)

For semantic properties that cannot be checked statically, use Gauntlet:

```bash
lattice-lock test
```

This generates and runs pytest-based tests derived from your `lattice.yaml` policies.

### CI/CD Integration

Integrate with CI/CD by adding validation and testing steps to your workflows. See `.github/workflows/ci.yml` for examples.

---

## Local Tooling

### Pre-Push Hook

A repo-scoped pre-push hook (in `.githooks/pre-push`) blocks pushing any branch except `main` to the canonical remote `origin`.

**Behavior:**
- Allows tags and remote branch deletions
- Only enforces for `origin` (fork remotes are allowed)
- Can be bypassed with `--no-verify` or `SKIP_BRANCH_POLICY=1` (not recommended)

### Git Aliases

**Sync and cleanup helpers:**
- `git sync` - Fetches with prune and pulls with fast-forward only
- `git prune-all` - Prunes deleted branches and tags across remotes
- `git delete-merged` - Removes fully merged local branches (excluding `main`/`master`)

### Working with AI/Agents

**Local tools (local LLMs, Claude Code, Gemini CLI):**
- Apply patches locally on a temp branch
- Push to your fork
- Open a PR

**Chat tools (Claude, Gemini Chat):**
- Request diffs/patches
- Apply locally
- Then PR

**Cloud-only (Devin.ai):**
- Operate exclusively in its own fork
- Open PRs back to this repo

---

## Enforcement

### Pre-Commit Checks

Before committing, verify:
1. ✅ Files are in the correct directory structure
2. ✅ File names follow conventions (lowercase with underscores)
3. ✅ No prohibited patterns (uppercase in file names, spaces, special chars)
4. ✅ No temporary or personal files in root

### CI Checks

- Tests must pass
- Lint must pass
- Typecheck must pass
- PR labels must be present

### Server-Side Protection

- Server-side branch protection may be limited on private repos without a paid plan
- Local hook + reviews/checks via PRs provide practical enforcement
- If/when server-side protections are available, enable: require PRs, linear history, conversation resolution, and 1+ approving review

---

## Questions or Issues

Open an issue or start a discussion if:
- The workflow needs adjustments
- You find conflicting information
- You need clarification on any standard
- You want to propose changes to this document

---

**Version:** 4.0.0  
**Last Updated:** 2026-01-01  
**Status:** MANDATORY - All contributions must adhere to these standards
