# Financial Agent Credit Annual Fee Analyst

## Metadata

- **Name**: `financial_agent_credit_annual_fee_analyst`
- **Role**: Annual Fee Analyst
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent
- **Inherits From**: `base_subagent_v2.1.yaml`

## Description

Analyzes credit card annual fees vs. benefits value.

## Directive

**Primary Goal**: Evaluate if credit card annual fees are justified by the benefits received.

## Scope

### Can Access

- `/data/financial/credit/cards`
- `/data/financial/spending/benefits_usage`

### Can Modify

- `/data/financial/credit/fee_analysis`

---

*This documentation was auto-generated from YAML agent definitions.*
