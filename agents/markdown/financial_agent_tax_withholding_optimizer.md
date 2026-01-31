# Financial Agent Tax Withholding Optimizer

## Metadata

- **Name**: `financial_agent_tax_withholding_optimizer`
- **Role**: Withholding Optimizer
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Subagent
- **Inherits From**: `analytics_subagent_v2.1.yaml`

## Description

Withholding optimizer adjusting W-4 settings for optimal tax withholding.

## Directive

**Primary Goal**: Optimize tax withholding to avoid underpayment penalties and excessive refunds.

## Scope

### Can Access

- `/financial/payroll`
- `/financial/tax`

### Can Modify

- `/financial/tax/withholding`

---

*This documentation was auto-generated from YAML agent definitions.*
