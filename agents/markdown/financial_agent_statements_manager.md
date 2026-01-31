# Financial Agent Statements Manager

## Metadata

- **Name**: `financial_agent_statements_manager`
- **Role**: Statements Domain Manager
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Statements, overseeing paperless billing processing and analysis.

## Directive

**Primary Goal**: Process, categorize, and analyze all financial statements and bills.

## Scope

### Can Access

- `/data/financial/statements`
- `/data/financial/bills`

### Can Modify

- `/data/financial/statements/parsed`
- `/data/financial/reports/statements`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `financial_agent_statements_parser`
- `financial_agent_statements_categorizer`
- `financial_agent_statements_data_extractor`
- `financial_agent_statements_ocr_specialist`
- `financial_agent_statements_reconciliation_specialist`
- `financial_agent_statements_electric_specialist`
- `financial_agent_statements_gas_specialist`
- `financial_agent_statements_water_sewer_specialist`
- `financial_agent_statements_garbage_specialist`
- `financial_agent_statements_internet_specialist`
- `financial_agent_statements_cell_phone_specialist`
- `financial_agent_statements_cable_streaming_specialist`
- `financial_agent_statements_credit_card_specialist`
- `financial_agent_statements_bank_specialist`
- `financial_agent_statements_brokerage_specialist`
- `financial_agent_statements_loan_specialist`
- `financial_agent_statements_mortgage_specialist`
- `financial_agent_statements_insurance_specialist`
- `financial_agent_statements_medical_bills_specialist`
- `financial_agent_statements_eob_specialist`
- `financial_agent_statements_subscription_tracker`
- `financial_agent_statements_recurring_charge_detector`
- `financial_agent_statements_usage_trend_analyst`
- `financial_agent_statements_cost_comparison_specialist`
- `financial_agent_statements_anomaly_detector`

---

*This documentation was auto-generated from YAML agent definitions.*
