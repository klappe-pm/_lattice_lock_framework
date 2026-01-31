# Financial Agent Statements Data Extractor

## Metadata

- **Name**: `financial_agent_statements_data_extractor`
- **Role**: Statement Data Extractor
- **Version**: 1.0.0
- **Status**: active
- **Type**: Subagent
- **Inherits From**: `base_subagent_v2.1.yaml`

## Description

Specializes in extracting specific data points (dates, amounts, account info) from statements.

## Directive

**Primary Goal**: Identify and extract high-value data fields from diverse statement formats.

## Scope

### Can Access

- `/data/financial/statements/parsed`

### Can Modify

- `/data/financial/statements/extracted`

---

*This documentation was auto-generated from YAML agent definitions.*
