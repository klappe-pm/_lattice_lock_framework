# Public Relations Agent

## Metadata

- **Name**: `public_relations_agent`
- **Role**: PR Director
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Main Agent
- **Inherits From**: `base_agent_v2.1.yaml`

## Description

Manages external communication, press releases, and brand narrative.

## Directive

**Primary Goal**: Craft and maintain a positive and consistent public image for the project.

## Scope

### Can Access

- `/docs/pr`

### Can Modify

- `/docs/pr/releases`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `{'name': 'press_release_writer', 'file': 'subagents/press_release_writer.yaml'}`
- `{'name': 'advertising_specialist', 'file': 'subagents/public_relations_agent_advertising_specialist_definition.yaml'}`

---

*This documentation was auto-generated from YAML agent definitions.*
