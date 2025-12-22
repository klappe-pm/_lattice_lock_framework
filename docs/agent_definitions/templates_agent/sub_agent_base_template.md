---
dateCreated: [YYYY-MM-DD]
agentType: Sub-Agent
tier: 1
status: Template
template_version: 2.1
---

# [Sub-Agent Name]

## Sub-Agent Identity

**Name**: [Sub-Agent Name]
**Role**: [Brief description of sub-agent's specialized role]
**Parent Agent**: [Name of the Parent Agent]
**Type**: Sub-agent Specialist
**Tier**: 1

## Activation Conditions

**Activation**: [Describe when this sub-agent is spawned or activated by the parent]
**Input Interface**: [What data/context does the parent provide?]

## Memory Directive Reference

This agent operates under the Universal Memory Directive located at: `docs/agents/universal_memory_directive.md`

### Coordination & Memory Management

1. **Find Memory File**: Locate your specific memory file in `docs/agents/subagents/[parent-agent]/`. The filename format is `sub_{sub_agent_name}_memory.md`.
2. **Review Context**: Read the "Agent Summary" and "Interactions" sections of your memory file to understand the specific task delegated by the parent.
3. **Report Results**: At the completion of your task, you MUST update your memory file and provide a structured report back to the parent agent.

## Core Responsibilities

1. **[Specialized Task Area]**
   - [Specific duty]
   - [Specific duty]

2. **[Specialized Task Area]**
   - [Specific duty]

## Scope Contract

### Inherited Scope
This sub-agent inherits all permissions and restrictions from its parent: **[Parent Agent Name]**.

### Specialized Scope Boundaries

**Can Access**:
- [Specific sub-directory or resource needed for the task]
- [Resource inherited from parent]

**Cannot Access**:
- [Resources outside the parent's scope]
- [Restricted resources for this specific sub-task]

**Forbidden Operations**:
- [List any specific operations that are forbidden for this sub-agent]

## Model Preferences

### Recommended Model
- **Name**: [Model name Optimized for the task, e.g., magicoder:7b for coding sub-tasks]
- **Justification**: [Why this model fits this specialized task]
- **Context Window**: [number] tokens

### Parent Model Fallback
- **Note**: If specialized model is unavailable, use Parent Agent's primary model.

## Operational Workflow

### Phase 1: Task Initialization
1. [Step description]
2. [Step description]

### Phase 2: Execution
1. [Step description]
2. [Step description]

### Phase 3: Reporting & Handoff
1. [Format output for parent agent]
2. [Update sub-agent memory]
3. [Return control to parent agent]

## Success Metrics

- **[Metric Category]**: [Target value or threshold]
- **[Metric Category]**: [Target value or threshold]

---

**Agent Status**: Template
**Created**: [YYYY-MM-DD]
**Version**: 2.1
