# Documentation Metadata & Frontmatter Standard

## Overview
All documentation files (especially diagrams) must include YAML frontmatter to support indexing, search, and knowledge management agents.

## Standard Frontmatter Fields

```yaml
---
# REQUIRED
title: "Human Readable Title"
type: [concept | guide | reference | diagram | meta]
status: [draft | review | stable | deprecated]

# CONTEXT
categories: [Architecture | Database | UserFlow | API | Security]
sub_categories: [Core | Auth | Agents | Tools | Frontend]

# LIFECYCLE
date_created: YYYY-MM-DD
date_revised: YYYY-MM-DD
author: [Agent Name or User]

# INDEXING
file_ids: [unique-uuid-v4] # Optional for human docs, required for generated assets
aliases: [alternate-title]
tags: [keywords, comma, separated]

# DIAGRAM SPECIFIC (Required for .md files containing Mermaid)
diagram_type: [erd | sequence | flow | class | state]
---
```

## Mermaid.js Standards
*   Use `mermaid` code blocks.
*   Prefer `graph TD` or `flowchart LR` for flows.
*   Use `classDiagram` for code structure.
*   Use `erDiagram` for database schemas.
*   Keep logic localized; avoid massive monolithic diagrams.

## File Naming Convention
*   **Documentation**: `kebab-case.md` (e.g., `user-authentication.md`)
*   **Diagrams**: `[type]_[name].md` (e.g., `seq_auth_flow.md`, `erd_users.md`)
