# Manual Test Plan Steps

This document outlines the step-by-step execution plan for the manual user training verification of the Lattice Lock Framework.

**Target Directory:** `/Users/kevinlappe/Documents/Obsidian Vaults/another_google_automation_agar`

## Phase 1: Preparation
1.  **Environment Check:** Ensure Python 3.10+ is active.
2.  **Installation:** Install `lattice-lock` in editable mode from the framework root (`pip install -e .`).
3.  **Clean State:** Ensure the target directory does not have an old `lattice.yaml` (if it does, back it up).

## Phase 2: Integration
4.  **Init:** Run `lattice-lock init` in the target directory.
5.  **Config:** Setup `.env` with at least one valid API key (OpenAI/Anthropic/Google).
6.  **Validation:** Run `lattice-lock doctor` to confirm the system is ready.

## Phase 3: Cloud Verification
7.  **List Models:** Run `lattice-lock orchestrator list` to verify API access.
8.  **Test Route:** Run a simple routing command (`lattice-lock orchestrator route "Hello"`) to prove E2E connectivity.

## Phase 4: Use Case Execution
9.  **Generative Request:**
    *   Command: Ask for a Google Apps Script helper.
    *   Verification: Check if valid code is returned.
    *   Action: Save it to `apps/gmail/src/label_automation.gs` (or similar).
10. **Governance Enforcement:**
    *   Setup: Add a "no-print" rule to `lattice.yaml`.
    *   Action: Create a Python file with a `print()` statement in `automation/`.
    *   Validation: Run `lattice-lock validate`.
    *   Success: Identify the error report.
    *   Fix: Change to logging and verify it passes.

## Phase 5: Completion
11. **Cleanup:** Revert any test files or git changes in the target repo.
