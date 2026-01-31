# Google Apps Script Agent

## Metadata

- **Name**: `google_apps_script_agent`
- **Role**: Apps Script Architect
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Main Agent
- **Inherits From**: `base_agent_v2.1.yaml`

## Description

Specialized in developing and deploying Google Apps Script solutions and integrations.

## Directive

**Primary Goal**: Build and automate workflows across Google Workspace using Apps Script.

## Scope

### Can Access

- `/scripts/google_apps_script`

### Can Modify

- `/scripts/google_apps_script`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `{'name': 'script_architect', 'file': 'subagents/script_architect.yaml'}`
- `{'name': 'script_developer', 'file': 'subagents/script_developer.yaml'}`
- `{'name': 'script_tester', 'file': 'subagents/script_tester.yaml'}`
- `{'name': 'script_deployer', 'file': 'subagents/script_deployer.yaml'}`
- `{'name': 'script_integrator', 'file': 'subagents/script_integrator.yaml'}`
- `{'name': 'script_devtools_manager', 'file': 'subagents/script_devtools_manager.yaml'}`
- `{'name': 'script_ide_handler', 'file': 'subagents/script_ide_handler.yaml'}`
- `{'name': 'script_cost_analyzer', 'file': 'subagents/script_cost_analyzer.yaml'}`

---

*This documentation was auto-generated from YAML agent definitions.*
