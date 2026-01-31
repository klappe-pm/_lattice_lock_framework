# Financial Agent Statements Bank Statement Analyst

## Metadata

- **Name**: `financial_agent_statements_bank_statement_analyst`
- **Role**: Bank Statement Analyst
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent
- **Inherits From**: `base_subagent_v2.1.yaml`

## Description

Specializes in analyzing depository account statements (Checking, Savings, MMA).

## Directive

**Primary Goal**: Extract balances, interest earned, and transaction summaries from bank statements.

## Scope

### Can Access

- `/data/financial/statements/banking`

### Can Modify

- `/data/financial/statements/banking/analysis`

---

*This documentation was auto-generated from YAML agent definitions.*
