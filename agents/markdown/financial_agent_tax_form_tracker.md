# Financial Agent Tax Form Tracker

## Metadata

- **Name**: `financial_agent_tax_form_tracker`
- **Role**: Tax Form Tracker
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Subagent
- **Inherits From**: `operational_subagent_v2.1.yaml`

## Description

Tax form tracker monitoring arrival and completeness of all tax forms (W-2, 1099s, K-1s, etc.).

## Directive

**Primary Goal**: Track and ensure receipt of all required tax forms.

## Scope

### Can Access

- `/financial/tax/documents`

### Can Modify

- `/financial/tax/form-tracking`

---

*This documentation was auto-generated from YAML agent definitions.*
