# Universal Memory Directive

**Version**: 1.0.0
**Status**: Active

## Purpose
This document defines the universal standard for how agents must interact with their persistent memory files. All agents must follow this protocol to ensure state continuity across sessions.

## Memory File Location
- **Directory**: `agent_memory/agents/`
- **Filename convention**:
  - Primary Agents: `agent_{agent_name}_memory.md`
  - Sub-Agents: `sub_{sub_agent_name}_memory.md`

## Memory File Structure
Each memory file must adhere to the following Markdown structure:

```markdown
# Agent Memory: [Agent Name]
Last Updated: [ISO 8601 Timestamp]

## Agent Summary
[High-level summary of the agent's purpose, recent achievements, and current state.]

## Key Context
[Persistent information, credentials reference (safe pointers), or strict constraints.]

## Agent Next Steps
[Detailed list of next planned actions. This acts as the "todo" list across sessions.]

## Interactions Log
[Chronological log of significant interactions, decisions, or handoffs.]
- [Timestamp]: [Interaction description]
```

## Operational Protocol

### 1. Initialization Phase
At the start of ANY task or session:
1. **Locate** your memory file.
2. **Read** the "Agent Summary" and "Agent Next Steps".
3. **Load** "Key Context" into your working context.

### 2. Execution Phase
- Use "Agent Next Steps" to guide your immediate planning.
- If you discover new constraints or context, **append** them to "Interactions Log" in memory (in-memory buffer) for later write.

### 3. Termination Phase
Before finishing your session:
1. **Update** "Agent Summary" with new accomplishments.
2. **Update** "Agent Next Steps": Remove completed items, add new ones.
3. **Append** to "Interactions Log": Record the session outcome.
4. **Write** the file back to disk.

## Safety & Security
- **NO SECRETS**: Never write API keys, passwords, or PII to memory files.
- **Git Ignore**: Ensure `agent_memory/` is added to `.gitignore`.
