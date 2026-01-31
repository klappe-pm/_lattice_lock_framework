# Financial Agent Credit Manager

## Metadata

- **Name**: `financial_agent_credit_manager`
- **Role**: Domain Manager - Credit
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Credit cards and credit score management.

## Directive

**Primary Goal**: Optimize credit score, manage credit cards, and monitor credit health.

## Scope

### Can Access

- `/data/financial/credit_reports`
- `/data/financial/credit_cards`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `credit_score_analyst`
- `credit_chase_specialist`
- `credit_amex_specialist`
- `credit_utilization_optimizer`

---

*This documentation was auto-generated from YAML agent definitions.*
