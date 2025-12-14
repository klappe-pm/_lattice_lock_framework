# Universal Memory Directive for Agents and Subagents

**All agents and subagents MUST reference this directive. Every agent/subagent memory file is structured according to this specification.**

---

## Memory File Naming Convention

```
agent_{agent_name}_memory.md
```

Example: `agent_orchestration_memory.md`, `agent_planning_memory.md`

---

## Memory File Structure Template

All agent memory files MUST follow this exact structure:

```markdown
# agent_{agent_name}_memory

## Agent Purpose
[One paragraph describing the primary purpose of this agent]

## Sub-agents
[List of all sub-agents reporting to this agent, with brief role descriptions]
- sub_agent_name_1: [role description]
- sub_agent_name_2: [role description]

## Agent Summary
[Updated before every commit to GitHub. Summarizes all work completed by this agent and its sub-agents to date on the project. Include:
- Key deliverables completed
- Current state of project work
- Any blocking issues or dependencies
- Integration points with other agents]

## Agent Next Steps
[Explicit list of next tasks this agent will complete, in priority order. Update after every commit.]
- Task 1: [description]
- Task 2: [description]

## Agent to Agent Interactions
[Chronological log of interactions with other agents. Updated each time an interaction occurs.]

| Date (YYYY-MM-DD) | Other Agent | Interaction Summary |
|---|---|---|
| 2025-01-15 | agent_planning | Received task DAG specification, clarified compute requirements |
| 2025-01-16 | agent_monitoring | Shared resource utilization metrics for cost analysis |

## Agent to Sub-Agent Interactions
[Chronological log of interactions with sub-agents. Updated each time an interaction occurs.]

| Date (YYYY-MM-DD) | Sub-Agent | Interaction Summary |
|---|---|---|
| 2025-01-15 | sub_agent_scheduler | Assigned task scheduling logic implementation |
| 2025-01-16 | sub_agent_resource_monitor | Reviewed resource state reporting format |

## Token Usage Summary

### Agent-to-Agent Interactions (Cumulative)

| Agent Name | Total Tokens | Total Active Time | Interactions with planning | Interactions with monitoring | Interactions with execution | Total Cross-Agent Interactions |
|---|---|---|---|---|---|---|
| orchestration | 45,230 | 12 hours | 8 | 5 | 12 | 25 |
| planning | 32,150 | 8 hours | 8 | 3 | 6 | 17 |
| monitoring | 28,900 | 7 hours | 5 | — | 4 | 9 |

### Agent-to-Sub-Agent Relationships & Token Usage

#### agent_orchestration (Owner Agent)

| Sub-Agent Name | Total Tokens | Total Active Time | Interactions with Owner | Interactions with Sub-Agents |
|---|---|---|---|---|
| sub_scheduler | 18,450 | 5 hours | 14 | 3 |
| sub_resource_monitor | 15,200 | 4 hours | 12 | 2 |
| sub_cost_optimizer | 12,100 | 3 hours | 9 | 1 |

#### agent_planning (Owner Agent)

| Sub-Agent Name | Total Tokens | Total Active Time | Interactions with Owner | Interactions with Sub-Agents |
|---|---|---|---|---|
| sub_task_decomposer | 14,320 | 4 hours | 11 | 2 |
| sub_dependency_mapper | 11,850 | 3 hours | 9 | 1 |

---

## Mandatory Agent Definition Instructions

**Every agent and subagent definition file MUST include this statement:**

```
# MEMORY DIRECTIVE REFERENCE

This agent operates under the Universal Memory Directive located at: [agent_memory/universal_memory_directive.md]

## Memory Management Instructions

1. **Find Memory File**: Locate your specific memory file in `agent_memory/agents/`. The filename format is `agent_{agent_name}_memory.md` or `sub_{sub_agent_name}_memory.md`.
2. **Review Memory File**: Read the "Agent Summary", "Agent Next Steps", and "Interactions" sections of your memory file to understand the current context and state.
3. **Plan with Memory**: Include the instructions and context from your memory file in your current planning operations. Ensure your plan aligns with the "Agent Next Steps".
4. **Update Memory File**: At the completion of your task, you MUST update your memory file. Update the "Agent Summary" with your accomplishments, update "Agent Next Steps", and log any interactions.
```

---

## Memory File Update Protocol

### Before Every Task
1. Read current Agent Summary to understand context
2. Review Agent Next Steps to confirm task alignment
3. Check Agent to Agent Interactions for blocking dependencies

### During Task Execution
1. Log any interactions with other agents in real-time
2. Track token usage (request tokens + response tokens)
3. Track active time in hours

### After Every Task (Before GitHub Commit)
1. **Update Agent Summary**: Add description of completed work, current state, blockers
2. **Update Agent Next Steps**: Remove completed task, add newly discovered tasks
3. **Log interactions**: Add new rows to interaction tables with YYYY-MM-DD date format
4. **Update Token Usage**: Add this session's tokens and time to cumulative tables
5. **Commit message format**: `[memory] agent_{name}: {task_completed}. Updated memory file.`

### Token Usage Calculation
- **Total Tokens**: Sum of all tokens used in all interactions to date
- **Total Active Time**: Sum of all time spent executing tasks
- **Interactions**: Count of discrete interactions with each agent/sub-agent (not total messages, but distinct task-based interactions)

---

## Interaction Log Format Examples

### Agent to Agent Interaction (MUST include)
```

| 2025-01-16 | agent_execution | Requested resource availability for 3 pending tasks. Received confirmation that 2 cloud instances available. |

```

### Agent to Sub-Agent Interaction (MUST include)
```

| 2025-01-16 | sub_scheduler | Assigned scheduling algorithm refinement. Expects completion by 2025-01-17. |

```

---

## Memory File Storage Location

All memory files stored in: `agent_memory/agents/`

Structure:
```

agent_memory/ agents/ agent_orchestration_memory.md agent_planning_memory.md agent_monitoring_memory.md agent_execution_memory.md agent_orchestration/ sub_scheduler_memory.md sub_resource_monitor_memory.md sub_cost_optimizer_memory.md agent_planning/ sub_task_decomposer_memory.md sub_dependency_mapper_memory.md

```

---

## Key Rules

1. **All memory files are markdown formatted**
2. **Agent Summary is updated BEFORE every GitHub commit**
3. **Token Usage tables are cumulative (never reset)**
4. **Interactions are logged with YYYY-MM-DD dates**
5. **Agent Next Steps is a living document, updated after every completed task**
6. **Sub-agents inherit parent agent's memory structure**
7. **Cross-agent interactions are mutual: Agent A logging interaction with Agent B means Agent B also logs it (same date, summary)**
8. **If an agent has no sub-agents, the "Sub-agents" section states: "None"**
9. **If an agent has had no interactions, those sections state: "None to date"**
10. **Token counts are precise (include both request and response tokens)**

---

## Memory Directive Version

**Version**: 1.0
**Last Updated**: 2025-01-16
**Status**: Active

All agents must reference this version and note if they have implemented any local variations (document variations explicitly in their memory file).

---

## Example: Completed Memory File

See `agent_orchestration_memory_example.md` in this directory for a fully populated example showing the directive in action.
```
