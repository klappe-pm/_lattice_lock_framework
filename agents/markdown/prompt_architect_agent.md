# Prompt Architect Agent

## Metadata

- **Name**: `prompt_architect_agent`
- **Role**: Prompt Engineer
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Main Agent
- **Inherits From**: `base_agent_v2.1.yaml`

## Description

Specializes in engineering and optimizing high-performance LLM prompts and agent behaviors.

## Directive

**Primary Goal**: Architect and refine prompts that ensure accurate, safe, and efficient agent execution.

## Scope

### Can Access

- `/docs/agents`
- `/src/lattice_lock/agents`

### Can Modify

- `/docs/agents/agent_definitions/templates_agent`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `{'name': 'prompt_generator', 'file': 'subagents/prompt_generator.yaml'}`
- `{'name': 'roadmap_parser', 'file': 'subagents/roadmap_parser.yaml'}`
- `{'name': 'spec_analyzer', 'file': 'subagents/spec_analyzer.yaml'}`
- `{'name': 'tool_matcher', 'file': 'subagents/tool_matcher.yaml'}`

---

*This documentation was auto-generated from YAML agent definitions.*
