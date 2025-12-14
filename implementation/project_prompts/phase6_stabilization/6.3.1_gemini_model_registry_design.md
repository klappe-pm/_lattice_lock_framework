# Task 6.3.1: Model Registry Source-of-Truth Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.3.2 (Devin AI)

---

## 1. Problem Statement

Currently, `ModelRegistry` has hardcoded models (`o1-pro`, etc.) in Python code. This violates the "Configuration over Code" principle and makes it impossible for users to add new models or adjust pricing without forking the repo.

**Goal:** Make `lattice.yaml` (or a dedicated `models.yaml`) the single source of truth for available models and their capabilities.

## 2. Design Strategy

We will introduce a **Layered Registry System**:

1.  **Layer 1: System Defaults (Hardcoded Fallback)**
    *   Minimal set of critical models (e.g., `o1-mini`, `gpt-4o`) to ensure the CLI works out-of-the-box.
2.  **Layer 2: User Configuration (`lattice.yaml`)**
    *   Users can define `models:` section to add custom local models (Ollama) or override costs.
3.  **Layer 3: Runtime Dynamic (Optional)**
    *   Future: Fetch valid models from a remote URL.

## 3. Configuration Schema

New section in `lattice.yaml`:

```yaml
models:
  - id: "my-custom-model"
    provider: "ollama"
    family: "llama3"
    context_window: 8192
    capabilities: ["code", "chat"]
    cost:
      input: 0.0
      output: 0.0
  - id: "gpt-4o"
    # Override default cost
    cost:
      input: 2.50
```

## 4. Architecture Changes

**`src/lattice_lock_orchestrator/registry.py`**

*   **`ModelRegistry` Class:**
    *   **Old:** `__init__` loads dict literals.
    *   **New:** `__init__` performs:
        1.  Load internal defaults.
        2.  Check for `lattice.yaml` or `~/.lattice/config.yaml`.
        3.  Merge configurations (User config > System defaults).
        4.  Validate schemas.

*   **Validation:**
    *   Ensure required fields (id, provider) exist.
    *   Warn on unknown providers.

## 5. Migration Plan

1.  Extract current hardcoded dictionary to `src/lattice_lock_orchestrator/defaults/models.json` (or keep as dict constant).
2.  Implement `ConfigLoader` to parse YAML model definitions.
3.  Update `ModelRegistry` to use `ConfigLoader`.

## 6. Implementation Tasks (For Devin AI)

1.  **[ ] Update `lattice_lock_orchestrator/types.py`:**
    *   Ensure `ModelCapabilities` is serializable/deserializable from dict.
2.  **[ ] Modify `ModelRegistry`:**
    *   Implement merging logic.
    *   Add `load_from_file(path)` method.
3.  **[ ] Create Default Registry File:**
    *   Move hardcoded models to `src/lattice_lock/resources/default_models.yaml` (package_data).
4.  **[ ] Test Coverage:**
    *   Test overriding a default model.
    *   Test adding a new model.
    *   Test malformed YAML handling.
