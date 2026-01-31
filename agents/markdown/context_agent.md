# Context Agent

## Metadata

- **Name**: `context_agent`
- **Role**: Knowledge Architect
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Main Agent
- **Inherits From**: `base_agent_v2.1.yaml`

## Description

Manages the framework's knowledge state, history synthesis, and validation.

## Directive

**Primary Goal**: Maintain high-fidelity context and validation across the agent ecosystem.

## Scope

### Can Access

- `/agent_memory`
- `/logs`

### Can Modify

- `/agent_memory/knowledge_base`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `{'name': 'chat_summary', 'file': 'subagents/chat_summary.yaml'}`
- `{'name': 'knowledge_synthesizer', 'file': 'subagents/knowledge_synthesizer.yaml'}`
- `{'name': 'information_gatherer', 'file': 'subagents/information_gatherer.yaml'}`
- `{'name': 'llm_memory_specialist', 'file': 'subagents/llm_memory_specialist.yaml'}`
- `{'name': 'memory_storage', 'file': 'subagents/memory_storage.yaml'}`
- `{'name': 'validator', 'file': 'subagents/validator.yaml'}`

---

*This documentation was auto-generated from YAML agent definitions.*
