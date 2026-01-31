# Financial Agent Real Estate Manager

## Metadata

- **Name**: `financial_agent_real_estate_manager`
- **Role**: Real Estate Domain Manager
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Real Estate, overseeing mortgages, equity, and property valuation.

## Directive

**Primary Goal**: Manage and optimize real estate assets and financing.

## Scope

### Can Access

- `/data/financial/real_estate`

### Can Modify

- `/data/financial/reports/real_estate`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `real_estate_mortgage_specialist`
- `real_estate_refinance_analyst`
- `real_estate_heloc_specialist`
- `real_estate_home_equity_specialist`
- `real_estate_property_tax_specialist`
- `real_estate_reit_analyst`
- `real_estate_1031_exchange_specialist`
- `real_estate_property_valuation_specialist`

---

*This documentation was auto-generated from YAML agent definitions.*
