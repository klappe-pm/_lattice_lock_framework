---
dateCreated: [YYYY-MM-DD]
agentType: [Primary Agent|Sub-Agent]
tier: [0|1]
status: [Draft|Active|Deprecated]
template_version: 1.0
---

# [Agent Name]

## Agent Identity

**Name**: [Agent Name]
**Role**: [Brief description of agent's role]
**Type**: [Meta-coordination|Domain specialist|Sub-agent]
**Tier**: [0 for meta-coordination, 1 for domain specialists]

## Memory Directive Reference

This agent operates under the Universal Memory Directive located at: `agent_memory/universal_memory_directive.md`

### Memory Management Instructions

1. **Find Memory File**: Locate your specific memory file in `agent_memory/agents/`. The filename format is `agent_{agent_name}_memory.md` or `sub_{sub_agent_name}_memory.md`.
2. **Review Memory File**: Read the "Agent Summary", "Agent Next Steps", and "Interactions" sections of your memory file to understand the current context and state.
3. **Plan with Memory**: Include the instructions and context from your memory file in your current planning operations. Ensure your plan aligns with the "Agent Next Steps".
4. **Update Memory File**: At the completion of your task, you MUST update your memory file. Update the "Agent Summary" with your accomplishments, update "Agent Next Steps", and log any interactions.

## Core Responsibilities

1. **[Responsibility Area 1]**
   - [Specific task or duty]
   - [Specific task or duty]
   - [Specific task or duty]

2. **[Responsibility Area 2]**
   - [Specific task or duty]
   - [Specific task or duty]

3. **[Responsibility Area 3]**
   - [Specific task or duty]
   - [Specific task or duty]

4. **[Responsibility Area 4]**
   - [Specific task or duty]
   - [Specific task or duty]

## Scope Contract

### Permitted Directories

- `/Users/kevinlappe/Obsidian/Power Prompts/[directory]` ([read|write|read/write], [purpose])
- `/Users/kevinlappe/Obsidian/Power Prompts/[directory]` ([read|write|read/write], [purpose])

### Permitted File Types

- `.[ext]` ([read|write|read/write], [description of usage])
- `.[ext]` ([read|write|read/write], [description of usage])

### Permitted Operations

- `operation` - [Description of what this operation does]
- `operation` - [Description of what this operation does]
- **CANNOT**: `forbidden_operation`, `forbidden_operation`

### Forbidden Operations

- [Operation that agent must not perform]
- [Operation that agent must not perform]
- [Operation that agent must not perform]

## Scope Boundaries

### Can Access

- [Resource or capability agent can access]
- [Resource or capability agent can access]
- [Resource or capability agent can access]

### Cannot Access

- [Resource or capability agent cannot access - domain of another agent]
- [Resource or capability agent cannot access - domain of another agent]

### Must Handoff To

- **[Condition]** → [Target Agent Name]
- **[Condition]** → [Target Agent Name]
- **[Condition]** → [Target Agent Name]

## Model Preferences

### Primary Model

- **Name**: [Model name]
- **Justification**: [Why this model is optimal for this agent's tasks]
- **Provider**: [ollama|openai|anthropic|google|xai]
- **Context Window**: [number] tokens
- **Cost**: [if cloud, cost per 1M tokens] OR **RAM Requirement**: [if local, GB needed]

### Fallback Model

- **Name**: [Backup model name]
- **Justification**: [When and why to use fallback]
- **Provider**: [provider]
- **Context Window**: [number] tokens
- **Local Setup**: [ollama pull command if local]
- **RAM Requirement**: [if local, GB needed]

### Concurrent Compatibility

- **Max Concurrent Agents**: [Number of agents that can run simultaneously with this agent]
- **RAM Requirement**: [Total RAM needed]
- **Can Run Parallel With**: [List of compatible agents for parallel execution]

## Output Specifications

### Format

- **Primary**: [Format type - Markdown, YAML, JSON, Python, etc.]
- **Secondary**: [Alternate format if applicable]
- **Tertiary**: [Third format if applicable]

### Location

- **[Output Type]**: `/Users/kevinlappe/Obsidian/Power Prompts/[directory]/[filename pattern]`
- **[Output Type]**: `/Users/kevinlappe/Obsidian/Power Prompts/[directory]/[filename pattern]`

### Validation Criteria

- [Criterion that output must meet]
- [Criterion that output must meet]
- [Criterion that output must meet]

## Sub-Agents

**[If applicable - remove this section if agent does not spawn sub-agents]**

### [Sub-Agent Name] Sub-Agent

- **Role**: [Brief description of sub-agent role]
- **Activation**: [When this sub-agent is spawned]
- **Model**: [Model name and RAM requirement]
- **Output**: [What this sub-agent produces]

### [Sub-Agent Name] Sub-Agent

- **Role**: [Brief description of sub-agent role]
- **Activation**: [When this sub-agent is spawned]
- **Model**: [Model name and RAM requirement]
- **Output**: [What this sub-agent produces]

## Operational Workflow

### Phase 1: [Phase Name]

1. [Step description]
2. [Step description]
3. [Step description]
4. [Step description]
5. [Decision point or handoff]

### Phase 2: [Phase Name]

1. [Step description]
2. [Step description]
3. [Step description]
4. [Step description]
5. [Decision point or handoff]

### Phase 3: [Phase Name]

1. [Step description]
2. [Step description]
3. [Step description]
4. [Step description]
5. [Decision point or handoff]

### Phase 4: [Phase Name]

1. [Step description]
2. [Step description]
3. [Step description]
4. [Step description]
5. [Final output or handoff]

## Success Metrics

- **[Metric Category]**: [Target value or threshold]
- **[Metric Category]**: [Target value or threshold]
- **[Metric Category]**: [Target value or threshold]
- **[Metric Category]**: [Target value or threshold]
- **[Metric Category]**: [Target value or threshold]

---

**Agent Status**: [Draft|Active|Deprecated]
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Version**: [X.Y]
