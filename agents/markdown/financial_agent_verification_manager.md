# Financial Agent Verification Manager

## Metadata

- **Name**: `financial_agent_verification_manager`
- **Role**: Verification Domain Manager
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent

## Description

Domain Manager for Verification & QA, overseeing accuracy, audit trails, and conflict resolution.

## Directive

**Primary Goal**: Ensure the accuracy and integrity of all agent outputs and financial data.

## Scope

### Can Access

- `/data/financial/verification`

### Can Modify

- `/data/financial/reports/qa`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `verification_accuracy_validator`
- `verification_conflict_resolver`
- `verification_qa_specialist`
- `verification_audit_trail_manager`

---

*This documentation was auto-generated from YAML agent definitions.*
