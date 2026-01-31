# Financial Agent Rewards Manager

## Metadata

- **Name**: `financial_agent_rewards_manager`
- **Role**: Domain Manager - Rewards
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Rewards programs including transferable points, airlines, and hotels.

## Directive

**Primary Goal**: Manage and optimize loyalty program portfolios across transferable points, airlines, and hotel programs.

## Scope

### Can Access

- `/data/financial/rewards`
- `/data/financial/travel`

### Can Modify

- `/data/financial/rewards/reports`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `rewards_amex_mr_specialist`
- `rewards_chase_ur_specialist`
- `rewards_citi_thankyou_specialist`
- `rewards_capital_one_miles_specialist`
- `rewards_bilt_specialist`
- `rewards_wells_fargo_specialist`
- `rewards_alaska_specialist`
- `rewards_delta_specialist`
- `rewards_united_specialist`
- `rewards_american_specialist`
- `rewards_southwest_specialist`
- `rewards_jetblue_specialist`
- `rewards_british_airways_specialist`
- `rewards_virgin_atlantic_specialist`
- `rewards_flying_blue_specialist`
- `rewards_aeroplan_specialist`
- `rewards_singapore_specialist`
- `rewards_emirates_specialist`
- `rewards_marriott_specialist`
- `rewards_hilton_specialist`
- `rewards_hyatt_specialist`
- `rewards_ihg_specialist`
- `rewards_wyndham_specialist`
- `rewards_choice_specialist`
- `rewards_radisson_specialist`
- `rewards_points_valuation_specialist`
- `rewards_transfer_optimizer`
- `rewards_redemption_strategist`
- `rewards_sweet_spot_finder`
- `rewards_status_match_specialist`
- `rewards_elite_status_tracker`
- `rewards_expiration_tracker`
- `rewards_earning_optimizer`
- `rewards_award_booking_specialist`
- `rewards_program_researcher`

---

*This documentation was auto-generated from YAML agent definitions.*
