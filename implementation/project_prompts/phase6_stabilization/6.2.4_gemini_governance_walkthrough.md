# Task 6.2.4: End-to-End Governance Core Documentation

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** (Self - Documentation)

---

## 1. Overview

This document defines the "Golden Path" for the Lattice Lock Governance Core. It serves as both a design specification for the documentation to be written and a test plan for the `walkthrough.md`.

**Objective:** A user should be able to go from zero to a fully governed project in <5 minutes.

## 2. Walkthrough Structure

The documentation `docs/guides/governance_walkthrough.md` will cover:

### Part 1: Defining Rules (The "Contract")
*   **Concept:** Explain `lattice.yaml` as the constitution of the project.
*   **Action:** Create a file `lattice.yaml` with a simple rule: "All API routes must returns typed responses."
*   **Snippet:**
    ```yaml
    version: "2.1"
    rules:
      - id: "api-typed-responses"
        severity: "error"
        description: "API routes must return Pydantic models"
        scope: "src/api/**/*.py"
        ensures: "return_type.is_subclass_of(BaseModel)"
    ```

### Part 2: Compiling Policies
*   **Concept:** `lattice.yaml` is compiled into Python AST checkers (Sheriff) and Runtime tests (Gauntlet).
*   **Action:**
    ```bash
    lattice-lock compile
    ```
*   **Result:** Inspect `build/lattice_rules.py` and `tests/gauntlet/test_generated.py`.

### Part 3: Verification (The "Sheriff")
*   **Concept:** Static analysis catches violations before commit.
*   **Action:** Write a bad function.
    ```bash
    lattice-lock validate
    ```
*   **Result:** See failure. Fix code. See pass.

### Part 4: Runtime Enforcement (The "Gauntlet")
*   **Concept:** Semantic properties that can't be checked statically.
*   **Action:** Run tests.
    ```bash
    lattice-lock test
    ```

## 3. Canonical Example

The "Hello World" of governance shall be **"No Print Statements in Production"**.

**lattice.yaml Strategy:**
```yaml
rules:
  - id: "no-print"
    description: "Use logger instead of print"
    scope: "**/*.py"
    excludes: ["scripts/*"]
    forbids: "node.is_call_to('print')"
```

## 4. Implementation Tasks (For Documentation Team)

1.  **[ ] Create `examples/governance_demo/`:**
    *   Initialize a dummy project.
    *   Add the canonical `lattice.yaml`.
2.  **[ ] Write `docs/guides/governance.md`:**
    *   Follow the structure above.
    *   Include screenshot/CLI output recordings.
3.  **[ ] Update `README.md`:**
    *   Link to the new guide in the "Getting Started" section.
