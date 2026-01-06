# Implementation Plan: Documentation Standardization & Diagram System

> **Goal**: Establish a self-maintaining documentation ecosystem where diagrams are visually consistent, renderable, and tightly coupled to the codebase via metadata.

## Phase 1: Diagram Infrastructure & Styling
- [ ] **Standardize File Types**
    - Convert raw `.mmd` files in `docs/assets/diagrams/` to Markdown (`.md`) files with embedded mermaid blocks.
    - **Why**: Ensures native rendering in GitHub, obsidian, and IDE previews without specialized plugins.
- [ ] **Create Mermaid Style Guide**
    - Create `docs/04-meta/DIAGRAM_STYLE_GUIDE.md`.
    - Define CSS class definitions (`classDef`) for standard component types:
        - `core`: Core infrastructure (Blue/Purple)
        - `agent`: AI Agents (Green/Teal)
        - `cli`: User Interfaces (Orange)
        - `external`: 3rd Party APIs (Grey)
        - `error`: Failure paths (Red)
    - Define standard directionality (LR vs TD) for diagram types.

## Phase 2: Metadata-Driven Mapping
- [ ] **Link Diagrams to Metadata**
    - Update all nodes in diagrams to use the `file_ids` found in document frontmatter (e.g., `graph TD; nodeA["Installation[guide-install-001]"]`).
    - This prepares for future automation where changing a file's title or status automatically updates the node in the diagram.
- [ ] **Comprehensive Audit Strategy**
    - Scan all project files (source and docs).
    - Ensure EVERY user-facing component has a corresponding documentation file with valid YAML frontmatter.
    - Create a "Shadow Map" report listing files *missing* standard metadata.

## Phase 3: The "Living Documentation" System
- [ ] **Automation Plan (Future)**
    - Design a `lattice doc-gen` script concept.
    - Input: Source files + Frontmatter.
    - Output: Updated diagram links and status dashboards.

## Immediate Action Items for Next Session
1. Rename/Refactor `.mmd` files to `.md` files with fenced code blocks.
2. Apply the new color palette variables to all 4 existing diagrams.
3. Verify that the `file_ids` in `docs/` match the node IDs in the diagrams.
