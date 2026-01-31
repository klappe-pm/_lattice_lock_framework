# Content Agent

## Metadata

- **Name**: `content_agent`
- **Role**: Editorial Director
- **Version**: 2.1.0
- **Status**: beta
- **Type**: Main Agent
- **Inherits From**: `base_agent_v2.1.yaml`

## Description

Manages full-lifecycle content strategy, creation, and distribution.

## Directive

**Primary Goal**: Produce and distribute high-quality, SEO-optimized content across multiple channels.

## Scope

### Can Access

- `/content`
- `/docs/brand`

### Can Modify

- `/content`
- `/distribution`

## Delegation

**Enabled**: Yes

### Allowed Subagents

- `{'name': 'editorial_manager', 'file': 'subagents/editorial_manager.yaml'}`
- `{'name': 'seo_specialist', 'file': 'subagents/seo_specialist.yaml'}`
- `{'name': 'writer', 'file': 'subagents/writer.yaml'}`
- `{'name': 'social_media_strategist', 'file': 'subagents/social_media_strategist.yaml'}`
- `{'name': 'email_marketing_specialist', 'file': 'subagents/email_marketing_specialist.yaml'}`
- `{'name': 'localization_expert', 'file': 'subagents/localization_expert.yaml'}`
- `{'name': 'operations_specialist', 'file': 'subagents/operations_specialist.yaml'}`
- `{'name': 'analyst', 'file': 'subagents/analyst.yaml'}`
- `{'name': 'technical_writer', 'file': 'subagents/content_agent_technical_writer_definition.yaml'}`
- `{'name': 'copywriter', 'file': 'subagents/content_agent_copywriter_definition.yaml'}`
- `{'name': 'editor', 'file': 'subagents/content_agent_editor_definition.yaml'}`
- `{'name': 'style_guide_reviewer', 'file': 'subagents/content_agent_style_guide_reviewer_definition.yaml'}`
- `{'name': 'content_strategist', 'file': 'subagents/content_agent_content_strategist_definition.yaml'}`

---

*This documentation was auto-generated from YAML agent definitions.*
