# Financial Agent Travel Manager

## Metadata

- **Name**: `financial_agent_travel_manager`
- **Role**: Domain Manager - Travel
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Travel planning, budgeting, and expense management.

## Directive

**Primary Goal**: Plan travel logistics and manage travel-related expenses through specialized subagents.

## Scope

### Can Access

- `/data/financial/travel_plans`
- `/data/financial/loyalty_programs`
- `/data/financial/travel_expenses`

### Can Modify

- `/data/financial/travel_plans`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `travel_budget_analyst`
- `travel_trip_planner`
- `travel_flight_search_specialist`
- `travel_hotel_search_specialist`
- `travel_car_rental_specialist`
- `travel_vacation_rental_specialist`
- `travel_insurance_specialist`
- `travel_expense_tracker`
- `travel_reimbursement_specialist`

---

*This documentation was auto-generated from YAML agent definitions.*
