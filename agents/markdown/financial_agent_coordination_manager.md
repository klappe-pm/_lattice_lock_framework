# Financial Agent Coordination Manager

## Metadata

- **Name**: `financial_agent_coordination_manager`
- **Role**: Coordination Domain Manager
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Cross-Domain Coordination, overseeing holistic financial lifecycle and planning.

## Directive

**Primary Goal**: Synchronize actions and strategies across all financial domains.

## Scope

### Can Access

- `/data/financial/coordination`

### Can Modify

- `/data/financial/reports/holistic`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `coordination_holistic_monitor`
- `coordination_life_event_coordinator`
- `coordination_risk_coordinator`
- `coordination_compliance_monitor`
- `coordination_short_term_planner`
- `coordination_medium_term_planner`
- `coordination_long_term_planner`
- `coordination_tax_investment_coordinator`
- `coordination_retirement_tax_coordinator`
- `coordination_credit_rewards_coordinator`
- `coordination_real_estate_tax_coordinator`

---

*This documentation was auto-generated from YAML agent definitions.*
