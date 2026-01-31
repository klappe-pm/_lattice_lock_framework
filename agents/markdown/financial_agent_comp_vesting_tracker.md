# Financial Agent Comp Vesting Tracker

## Metadata

- **Name**: `financial_agent_comp_vesting_tracker`
- **Role**: Vesting Tracker
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Subagent
- **Inherits From**: `operational_subagent_v2.1.yaml`

## Description

Vesting tracker monitoring upcoming RSU and stock option vesting dates and amounts.

## Directive

**Primary Goal**: Track and forecast all equity vesting events and their values.

## Scope

### Can Access

- `/financial/compensation/rsu`
- `/financial/compensation/options`

### Can Modify

- `/financial/compensation/vesting-calendar`

---

*This documentation was auto-generated from YAML agent definitions.*
