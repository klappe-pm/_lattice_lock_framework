# Financial Agent Linting Dependency Checker

## Metadata

- **Name**: `financial_agent_linting_dependency_checker`
- **Role**: Subagent - Linting - Dependency Checker
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Checks cross-agent dependencies ensuring delegation targets exist and circular dependencies are avoided.

## Directive

**Primary Goal**: Validate inter-agent dependencies ensuring all referenced agents exist and no circular dependencies occur.

## Scope

### Can Access

- `/agents/definitions`
- `/agents/dependency_graph`
- `/validation/dependency_errors`

---

*This documentation was auto-generated from YAML agent definitions.*
