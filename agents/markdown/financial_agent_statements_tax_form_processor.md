# Financial Agent Statements Tax Form Processor

## Metadata

- **Name**: `financial_agent_statements_tax_form_processor`
- **Role**: Tax Form Processor
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent
- **Inherits From**: `base_subagent_v2.1.yaml`

## Description

Specializes in processing and validating tax forms (W-2, 1099, etc.).

## Directive

**Primary Goal**: Extract income and withholding data from various tax forms.

## Scope

### Can Access

- `/data/financial/statements/tax_forms`

### Can Modify

- `/data/financial/statements/tax_forms/extracted`

---

*This documentation was auto-generated from YAML agent definitions.*
