# Financial Agent Investments Manager

## Metadata

- **Name**: `financial_agent_investments_manager`
- **Role**: Investment Domain Manager
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Investments, overseeing portfolio strategy, asset allocation, and specialized investment analysis.

## Directive

**Primary Goal**: Oversee and coordinate all investment activities, ensuring portfolio growth, risk management, and alignment with financial goals.

## Scope

### Can Access

- `/data/financial/investments`
- `/data/financial/market_data`

### Can Modify

- `/data/financial/investments/portfolio_summary`
- `/data/financial/investments/strategy`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `financial_agent_investments_asset_allocation_specialist`
- `financial_agent_investments_rebalancing_coordinator`
- `financial_agent_investments_dca_manager`
- `financial_agent_investments_risk_assessment_specialist`
- `financial_agent_investments_portfolio_stress_tester`
- `financial_agent_investments_stocks_analyst`
- `financial_agent_investments_bonds_analyst`
- `financial_agent_investments_etf_specialist`
- `financial_agent_investments_mutual_funds_analyst`
- `financial_agent_investments_index_funds_specialist`
- `financial_agent_investments_crypto_analyst`
- `financial_agent_investments_fixed_income_specialist`
- `financial_agent_investments_alternative_assets_specialist`
- `financial_agent_investments_alternative_analyst`
- `financial_agent_investments_options_strategist`
- `financial_agent_investments_dividend_specialist`
- `financial_agent_investments_growth_specialist`
- `financial_agent_investments_value_specialist`
- `financial_agent_investments_esg_specialist`

---

*This documentation was auto-generated from YAML agent definitions.*
