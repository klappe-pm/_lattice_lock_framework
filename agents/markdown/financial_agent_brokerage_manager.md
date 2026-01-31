# Financial Agent Brokerage Manager

## Metadata

- **Name**: `financial_agent_brokerage_manager`
- **Role**: Domain Manager - Brokerage
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Brokerage platform-specific guidance and integration.

## Directive

**Primary Goal**: Provide platform-specific guidance for various brokerage and crypto exchange platforms.

## Scope

### Can Access

- `/data/financial/brokerage`
- `/data/financial/accounts`

### Can Modify

- `/data/financial/brokerage/reports`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `brokerage_vanguard_specialist`
- `brokerage_fidelity_specialist`
- `brokerage_schwab_specialist`
- `brokerage_morgan_stanley_specialist`
- `brokerage_stock_plan_connect_specialist`
- `brokerage_etrade_specialist`
- `brokerage_td_ameritrade_specialist`
- `brokerage_interactive_brokers_specialist`
- `brokerage_merrill_edge_specialist`
- `brokerage_ally_invest_specialist`
- `brokerage_robinhood_specialist`
- `brokerage_webull_specialist`
- `brokerage_coinbase_specialist`
- `brokerage_kraken_specialist`
- `brokerage_gemini_specialist`
- `brokerage_binance_us_specialist`

---

*This documentation was auto-generated from YAML agent definitions.*
