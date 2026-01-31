# Financial Agent Statements Duplicate Charge Detector

## Metadata

- **Name**: `financial_agent_statements_duplicate_charge_detector`
- **Role**: Duplicate Charge Detector
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent
- **Inherits From**: `base_subagent_v2.1.yaml`

## Description

Specializes in identifying duplicate or erroneous charges across statements.

## Directive

**Primary Goal**: Flag potential double-billing or erroneous transactions for review.

## Scope

### Can Access

- `/data/financial/statements/parsed`

### Can Modify

- `/data/financial/statements/disputes`

---

*This documentation was auto-generated from YAML agent definitions.*
