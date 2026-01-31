# Financial Agent Banking Manager

## Metadata

- **Name**: `financial_agent_banking_manager`
- **Role**: Domain Manager - Banking
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Bank accounts and liquid assets.

## Directive

**Primary Goal**: Manage checking, savings, and other bank accounts.

## Scope

### Can Access

- `/data/financial/bank_accounts`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `banking_checking_specialist`
- `banking_savings_specialist`
- `banking_cd_specialist`
- `banking_wire_transfer_specialist`

---

*This documentation was auto-generated from YAML agent definitions.*
