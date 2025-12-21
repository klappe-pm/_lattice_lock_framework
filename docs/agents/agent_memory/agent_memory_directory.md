---
vault:
categories:
subCategories:
topics:
subTopics:
dateCreated: 2025-08-10
dateRevised: 2025-08-12
aliases: []
tags: []
---

# Agent Memory Storage & Project Tracking System

> [!IMPORTANT]
> This structure is governed by the [Universal Memory Directive](universal_memory_directive.md). Please refer to that document for the authoritative memory file structure and agent instructions.

## Purpose

Persistent memory storage for agent orchestration with comprehensive project tracking, conversation history, and progress monitoring across all agent interactions.

## Agent Memory Directory Structure

```mermaid
graph TD
    Memory[agent_memory/] --> Projects[projects/]
    Memory --> Agents[agents/]
    Memory --> Shared[shared/]

    Projects --> ProjID["{project_id}/"]
    ProjID --> Conv[conversations/]
    ProjID --> Prog[progress/]
    ProjID --> Plans[plans/]
    ProjID --> Scope[scope_changes/]
    ProjID --> Check[checkpoints/]
    ProjID --> Summary[project_summary.json]

    Conv --> ConvFiles["• {timestamp}_agent_{type}.json<br/>• {timestamp}_subagent_{lang}.json<br/>• conversation_index.json"]
    Prog --> ProgFiles["• current_sprint.json<br/>• completed_tasks.json<br/>• pending_tasks.json<br/>• progress_timeline.json"]
    Plans --> PlanFiles["• project_plan.md<br/>• technical_spec.json<br/>• milestones.json<br/>• dependencies.json"]
    Scope --> ScopeFiles["• {timestamp}_scope_change.json<br/>• change_requests.json<br/>• approved_changes.json<br/>• scope_history.md"]
    Check --> CheckFiles["• {timestamp}_checkpoint.json<br/>• checkpoint_manifest.json"]

    Agents --> AgentID["{agent_id}/"]
    Agents --> SubAgents[subagents/]

    AgentID --> AgentFiles["• state.json<br/>• memory.json<br/>• skills.json<br/>• task_history.json"]
    SubAgents --> SubAgentID["{subagent_id}/"]
    SubAgentID --> SubFiles["• language_config.json<br/>• code_patterns.json<br/>• execution_history.json"]

    Shared --> SharedFiles["• knowledge_base.md<br/>• global_config.json<br/>• metrics.json"]

    style Memory fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style Summary fill:#9f9,stroke:#333,stroke-width:2px
