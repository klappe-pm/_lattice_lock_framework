# Documentation Directory Structure Map

## Goal
Transform the existing flat/scattered structure into a user-centric hierarchy.

## Target Hierarchy

### 1. `00-getting-started/`
*   **Purpose**: Onboarding, installation, quick starts.
*   **Source**: Parts of `README.md`, `guides/setup`.

### 2. `01-concepts/`
*   **Purpose**: High-level explanation of how things work.
*   **Source**:
    *   `architecture/` -> `01-concepts/architecture/`
    *   `design/` -> `01-concepts/design/`
    *   `features/` -> `01-concepts/features/`
    *   `AGENTS.md` -> `01-concepts/agents.md`
    *   `MODELS.md` -> `01-concepts/models.md`

### 3. `02-guides/`
*   **Purpose**: Practical, step-by-step instructions.
*   **Source**: `guides/`, `tutorials/`, `examples/`.

### 4. `03-reference/`
*   **Purpose**: Technical specs, API docs, database schemas.
*   **Source**:
    *   `reference/` -> `03-reference/api/`
    *   `database/` -> `03-reference/database/`
    *   `modules/` -> `03-reference/modules/`
    *   `testing/` -> `03-reference/testing/`

### 5. `04-meta/`
*   **Purpose**: Project governance and maintenance.
*   **Source**: `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `USER_FACING_FILE_MAP.md`.

### 6. `assets/`
*   **Purpose**: Static assets.
*   **Source**: `diagrams/` -> `assets/diagrams/`, images.

## Migration Rules
1.  Create new numbered folders.
2.  git mv existing folders into new locations.
3.  Update internal links (Phase 8).
