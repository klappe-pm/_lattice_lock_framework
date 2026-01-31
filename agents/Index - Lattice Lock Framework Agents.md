# Index - Lattice Lock Framework Agents

**Generated**: 2026-01-10
**Version**: Agent System v2.1
**Total Agent Definitions**: 762 YAML files across 16 domains

---

## Quick Reference

| Item               | Value                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------- |
| **Purpose**        | AI agent definition and sync system for Lattice Lock Framework, Claude Code, and more. |
| **Entry Point**    | `sync_agents_to_claude.py`                                                             |
| **Watcher**        | `watch_and_sync.py`                                                                    |
| **Agent Format**   | YAML v2.1 specification                                                                |
| **Output Targets** | Claude Code `.claude/agents/`, Lattice Lock `markdown/`                                |

---

## Project Structure

```
agents/
├── agent_definitions/          # Source YAML agent files (762 total)
│   ├── agents_business_review/ # 9 agents
│   ├── agents_cloud/           # 4 agents (AWS, Azure, GCP)
│   ├── agents_content/         # 14 agents
│   ├── agents_context/         # 7 agents
│   ├── agents_education/       # 4 agents
│   ├── agents_engineering/     # 9 agents
│   ├── agents_financial/       # 645 agents (largest domain)
│   ├── agents_glossary/        # Specs & format docs
│   ├── agents_google_apps_script/ # 9 agents
│   ├── agents_model_orchestration/ # 1 agent
│   ├── agents_product_management/ # 23 agents
│   ├── agents_project_management/ # 5 agents
│   ├── agents_prompt_architect/   # 5 agents
│   ├── agents_public_relations/   # 3 agents
│   ├── agents_research/        # 8 agents
│   └── agents_ux/              # 16 agents
│
├── agent_diagrams/             # Mermaid workflow diagrams
├── agent_memory/               # Memory directive specs
├── agent_workflows/            # Execution patterns (hybrid, parallel, sequential)
├── agents_config/              # Inheritance & mixins
├── templates_agents/           # Base templates & creation guides
│
├── sync_agents_to_claude.py    # Main sync script (CLI)
├── watch_and_sync.py           # File watcher for auto-sync
├── Makefile                    # make install|sync|watch|clean
└── requirements.txt            # pyyaml, watchdog
```

---

## Entry Points

### CLI: `sync_agents_to_claude.py`
**Purpose**: Convert YAML agents to Claude Code markdown format
**Usage**: `python3 sync_agents_to_claude.py`
**Options**:
1. Claude Code (project) + archive [RECOMMENDED]
2. Claude Code (user) + archive
3. All targets
4. Archive only

### Watcher: `watch_and_sync.py`
**Purpose**: Auto-sync on YAML file changes
**Usage**: `python3 watch_and_sync.py` or `make watch`

---

## Core Modules

### AgentConverter (sync_agents_to_claude.py:50-238)
- `to_claude_code_format()` → YAML frontmatter + markdown
- `to_lattice_lock_format()` → Documentation markdown

### AgentSyncer (sync_agents_to_claude.py:259-370)
- Orchestrates sync across multiple targets
- Handles main agents and subagents

### SyncTarget (sync_agents_to_claude.py:25-47)
- Dataclass defining sync destinations
- Configurable converter and path

---

## Agent Domains Summary

| Domain | Count | Key Roles |
|--------|-------|-----------|
| **Financial** | 645 | Trading, analysis, insurance, advisors |
| **Product Management** | 23 | Strategists, analysts, designers |
| **UX** | 16 | Designers, testers, accessibility |
| **Content** | 14 | Writers, editors, SEO, localization |
| **Engineering** | 9 | Frontend, backend, DevOps, security |
| **Business Review** | 9 | OKR, risk, competitive intel |
| **Google Apps Script** | 9 | Script dev, deploy, test |
| **Research** | 8 | Market, user, competitive |
| **Context** | 7 | Memory, synthesis, validation |
| **Project Management** | 5 | Planning, status, tasks |
| **Prompt Architect** | 5 | Spec analysis, tool matching |
| **Cloud** | 4 | AWS, Azure, GCP |
| **Education** | 4 | Curriculum, training |
| **Public Relations** | 3 | Press, advertising |
| **Model Orchestration** | 1 | LLM routing & selection |

---

## Configuration

### Agent YAML Structure (v2.1)
```yaml
agent:
  identity: {name, version, role, description, tags}
  directive: {primary_goal, constraints}
  scope: {can_access, can_modify, cannot_access}
  delegation: {enabled, allowed_subagents}
  model_selection: {default_provider, strategies}
  planning: {enabled, phases}
  estimation: {cost_limits}
```

### Inheritance System
```
agents_config/inheritance/
├── base/
│   ├── base_agent.yaml
│   ├── base_model.yaml
│   └── base_subagent.yaml
└── mixins/
    ├── agents/ (delegation, memory, tools, code)
    └── models/ (anthropic, openai, local)
```

---

## Documentation

| File | Purpose |
|------|---------|
| `QUICKSTART.md` | 5-minute setup guide |
| `SYNC_README.md` | Full sync documentation |
| `EXTENDING.md` | Add new sync targets |
| `SYSTEM_OVERVIEW.md` | Architecture & design |
| `glossary.md` | Variable & type reference |
| `metrics_calibration.md` | Performance tuning |

---

## Workflows

| Pattern | File | Use Case |
|---------|------|----------|
| Sequential | `workflows_sequential_execution.md` | Linear task chains |
| Parallel | `workflows_parallel_execution.md` | Independent subtasks |
| Hybrid | `workflows_hybrid.md` | Mixed execution |

---

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# One-time sync (interactive)
python3 sync_agents_to_claude.py

# Auto-watch mode
make watch

# Verify sync
ls ../.claude/agents/
```

---

## Validation Tools

### `validate_agents.py` - Automated Validation
Programmatic validation without LLM. Checks 12 rule categories.

```bash
# Validate single file
python3 validate_agents.py path/to/agent.yaml

# Validate domain
python3 validate_agents.py --domain engineering

# Validate all with JSON report
python3 validate_agents.py --all --json --output report.json

# List domains
python3 validate_agents.py --list-domains
```

### `prepare_for_linting.py` - LLM Prompt Generator
Prepares agent files for validation with local LLM (Qwen3-Next-80B).

```bash
# Generate prompt for single file
python3 prepare_for_linting.py path/to/agent.yaml

# Generate batched prompts for domain
python3 prepare_for_linting.py --domain financial --batch-size 15 --output batches/

# Quick mode (errors only)
python3 prepare_for_linting.py --domain ux --quick
```

### `AGENT_LINTING_PROMPT.md` - LLM Instructions
Complete validation spec for Qwen3-Next-80B including:
- System prompt
- 12 validation rules
- JSON output format
- Usage examples

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyyaml | >=6.0 | YAML parsing |
| watchdog | >=3.0 | File system monitoring |

---

## Agent Specification Format

See `agent_definitions/agents_glossary/agent_instructions_file_format.md` for the complete v2.1 specification including:
- 18 YAML sections
- Model selection framework (63 models, 8 providers)
- Planning protocol (6 phases)
- Estimation protocol
- Delegation protocol
