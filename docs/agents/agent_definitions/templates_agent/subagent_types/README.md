# Subagent Type Templates (v2.1)

This directory contains standardized templates for various subagent roles. These templates inherit from the `base_agent_v2.1.yaml` and provide domain-specific defaults.

## Available Templates

| Template | Purpose | Key Differentiators |
|----------|---------|----------------------|
| [analytics_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/analytics_subagent_v2.1.yaml) | Data analysis & reporting | High reasoning (Deepseek-R1), verbosity: detailed. |
| [intelligence_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/intelligence_subagent_v2.1.yaml) | Research & competitive intel | Large context, discovery-focused (70 max steps). |
| [technical_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/technical_subagent_v2.1.yaml) | Coding & engineering | Devin access, modify /src privileges. |
| [planning_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/planning_subagent_v2.1.yaml) | Strategy & architecture | Linear planning, overview verbosity. |
| [operational_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/operational_subagent_v2.1.yaml) | Coordination & task tracking | Brief response style, long timeouts. |
| [creative_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/creative_subagent_v2.1.yaml) | Content & writing | Claude-optimized, empathetic tone. |
| [infrastructure_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/infrastructure_subagent_v2.1.yaml) | Cloud ops & deployments | Modify /infrastructure privileges, strict guardrails. |
| [automation_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/automation_subagent_v2.1.yaml) | Scripting & CI/CD | 100 max steps, GPT-4o-mini optimized. |
| [memory_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/memory_subagent_v2.1.yaml) | Context & state management | Knowledge base storage focus. |
| [specialized_subagent](file:///Users/kevinlappe/Documents/Lattice Lock Framework/docs/agents/agent_definitions/templates_agent/subagent_types/specialized_subagent_v2.1.yaml) | Misc / unique tasks | Local model defaults, flexible structure. |

## Inheritance Hierarchy

`Agent/Subagent File` > overrides > `Subagent Type Template` > overrides > `Base Agent Template`

## Usage

To create a new subagent, simply reference the appropriate template in your YAML and override only the unique fields (e.g., `name`, `primary_goal`).
