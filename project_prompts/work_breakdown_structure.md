# Lattice Lock Framework - Work Breakdown Structure

## Project Overview

The Lattice Lock Framework is a governance-first framework for AI-assisted software development with three integrated layers: Governance Core, Model Orchestrator, and Engineering Framework.

## Phases and Epics

### Phase 1: Foundation (Week 1-2)

**Exit Criteria:**
- New project can be scaffolded in <5 minutes
- Validation catches 100% of structure violations
- Model Orchestrator importable as `from lattice_lock import ModelOrchestrator`

| Epic | Description | Owner Tools |
|------|-------------|-------------|
| 1.1 | Package Model Orchestrator | Devin AI |
| 1.2 | Configuration Validator | Gemini CLI, Codex CLI |
| 1.3 | Repository Structure Enforcement | Codex CLI |
| 1.4 | Scaffolding CLI | Claude Code CLI, Claude Code App |

### Phase 2: CI/CD Integration (Week 2-3)

**Exit Criteria:**
- CI validates all PRs automatically
- Sheriff blocks forbidden imports
- Gauntlet runs semantic tests

| Epic | Description | Owner Tools |
|------|-------------|-------------|
| 2.1 | GitHub Actions Integration | Claude Code CLI |
| 2.2 | AWS CodePipeline Integration | Devin AI |
| 2.3 | GCP Cloud Build Integration | Devin AI |
| 2.4 | Sheriff CLI Wrapper | Gemini CLI |
| 2.5 | Gauntlet Test Runner | Codex CLI |

### Phase 3: Error Handling & Admin (Week 3-4)

**Exit Criteria:**
- Failed deployments auto-rollback
- Admin can view all project statuses via API
- Error logs include actionable remediation steps

| Epic | Description | Owner Tools |
|------|-------------|-------------|
| 3.1 | Error Boundary System | Devin AI |
| 3.2 | Automatic Rollback Mechanism | Gemini CLI |
| 3.3 | Admin API | Claude Code App |
| 3.4 | Status Dashboard | Codex CLI |

### Phase 4: Documentation & Pilot (Week 4)

**Exit Criteria:**
- 2+ projects successfully onboarded
- Documentation covers all workflows
- User satisfaction score >4/5

| Epic | Description | Owner Tools |
|------|-------------|-------------|
| 4.1 | Comprehensive Documentation | Claude Code Website |
| 4.2 | Tutorial Content | Claude Code Website |
| 4.3 | Pilot Projects | Devin AI |
| 4.4 | Feedback Integration | Claude Code App |

### Phase 5: Prompt Automation (Week 5)

**Exit Criteria:**
- Prompt Architect Agent can generate prompts from specifications
- Generated prompts pass validation against v2.1 spec
- Integration with prompt_tracker.py complete
- Agent can update existing prompts based on spec changes

| Epic | Description | Owner Tools |
|------|-------------|-------------|
| 5.1 | Prompt Architect Core | Devin AI |
| 5.2 | Specification Analysis | Gemini CLI |
| 5.3 | Prompt Generation Engine | Codex CLI |
| 5.4 | Tracker Integration | Claude Code App |

## Tool Ownership Matrix

| Tool | Primary Files | Do NOT Touch |
|------|---------------|--------------|
| Devin AI | `pyproject.toml`, `version.txt`, `src/lattice_lock/__init__.py`, `scripts/orchestrator_cli.py`, CI templates (AWS/GCP), error boundaries | `src/lattice_lock_cli/`, `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, `developer_documentation/` |
| Gemini CLI | `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, Sheriff CLI, rollback system | `src/lattice_lock_validator/agents.py`, `src/lattice_lock_validator/structure.py`, `pyproject.toml`, `src/lattice_lock_cli/` |
| Codex CLI | `src/lattice_lock_validator/agents.py`, `src/lattice_lock_validator/structure.py`, `.pre-commit-config.yaml`, Gauntlet, dashboard | `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, `pyproject.toml`, `src/lattice_lock_cli/commands/` |
| Claude Code CLI | `src/lattice_lock_cli/__main__.py`, `src/lattice_lock_cli/commands/init.py`, `src/lattice_lock_cli/templates/`, GitHub Actions | `src/lattice_lock_cli/commands/validate.py`, `src/lattice_lock_cli/commands/doctor.py`, `src/lattice_lock_validator/`, `pyproject.toml` |
| Claude Code App | `src/lattice_lock_cli/commands/validate.py`, `src/lattice_lock_cli/commands/doctor.py`, `tests/integration/`, Admin API | `src/lattice_lock_cli/__main__.py`, `src/lattice_lock_cli/commands/init.py`, `src/lattice_lock_cli/templates/`, `pyproject.toml` |
| Claude Code Website | `developer_documentation/` | All `src/` files, `pyproject.toml`, `tests/` |

## Prompt Numbering Convention

`{phase}.{epic}.{task}_{tool}.md`

Example: `1.1.1_devin.md` = Phase 1, Epic 1.1, Task 1, assigned to Devin AI

## Dependencies

### Phase 1 Dependencies
1. Epic 1.1 (Package Orchestrator) - No dependencies, start first
2. Epic 1.2 (Validator) - No dependencies, can run parallel with 1.1
3. Epic 1.3 (Structure) - Depends on 1.2 validator module structure
4. Epic 1.4 (CLI) - Depends on 1.2 and 1.3 for validation integration

### Phase 2 Dependencies
- All Phase 2 epics depend on Phase 1 completion
- Epic 2.4 (Sheriff) depends on 2.1 (GitHub Actions) for CI integration
- Epic 2.5 (Gauntlet) depends on 2.1 (GitHub Actions) for CI integration

### Phase 3 Dependencies
- All Phase 3 epics depend on Phase 2 completion
- Epic 3.3 (Admin API) depends on 3.1 (Error Boundaries)
- Epic 3.4 (Dashboard) depends on 3.3 (Admin API)

### Phase 4 Dependencies
- All Phase 4 epics depend on Phase 3 completion
- Epic 4.3 (Pilots) depends on 4.1 (Documentation)

### Phase 5 Dependencies
- All Phase 5 epics depend on Phase 1 completion (agent definitions structure)
- Epic 5.2 (Specification Analysis) depends on 5.1 (Core Agent)
- Epic 5.3 (Prompt Generation) depends on 5.1 and 5.2
- Epic 5.4 (Tracker Integration) depends on 5.3
