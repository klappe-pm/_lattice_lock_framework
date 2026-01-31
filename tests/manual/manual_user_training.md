# Lattice Lock Framework Manual User Training

This document serves as a comprehensive training manual to take a user from zero to full usage of the Lattice Lock Framework. We will use the existing project at `/Users/kevinlappe/Documents/Obsidian Vaults/another_google_automation_agar` as our real-world test bed.

**Objective:**
Learn to install, configure, and use Lattice Lock to govern and orchestrate AI workflows within the `another_google_automation_agar` project.

---

## Part 1: Prerequisites & Setup

Before integrating, ensure your environment is ready.

1.  **System Requirements**
    *   Python 3.10, 3.11, or 3.12 installed.
    *   Git installed and configured.
    *   Access to terminal/command line.

2.  **API Keys**
    *   You will need at least one valid API key from the following providers to test Orchestration:
        *   OpenAI (`OPENAI_API_KEY`)
        *   Anthropic (`ANTHROPIC_API_KEY`)
        *   Google (`GOOGLE_API_KEY`)

3.  **Target Repository**
    *   Ensure `another_google_automation_agar` is cloned locally:
        ```bash
        ls -d "/Users/kevinlappe/Documents/Obsidian Vaults/another_google_automation_agar"
        ```

---

## Part 2: Installation

We will install Lattice Lock directly from the local source (since we are in the framework repo) or via pip if it were published. For this training, we assume you are working with the local framework build.

1.  **Navigate to Framework Directory**
    ```bash
    cd /Users/kevinlappe/Documents/lattice-lock-framework
    ```

2.  **Install in Editable Mode**
    This allows us to test the latest changes immediately.
    ```bash
    pip install -e .
    ```

3.  **Verify Installation**
    ```bash
    lattice-lock --version
    ```
    *Success Criteria:* You should see version `2.1.0` (or current version).

---

## Part 3: Integration with Target Project

Now we will add Lattice Lock to your Google Automation project.

1.  **Navigate to Target Project**
    ```bash
    cd "/Users/kevinlappe/Documents/Obsidian Vaults/another_google_automation_agar"
    ```

2.  **Initialize Lattice Lock**
    Run the init command to create the default governance configuration.
    ```bash
    lattice-lock init
    ```
    *Output:* This creates a `lattice.yaml` file in the root of the project.

3.  **Configure Environment**
    Create or update your `.env` file in the target project root to include your AI provider keys.
    ```bash
    # Example .env content
    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...
    GOOGLE_API_KEY=...
    LATTICE_LOG_LEVEL=INFO
    ```

4.  **Validate Configuration (The "Doctor" Check)**
    Run the doctor command to ensure keys are loaded and the environment is healthy.
    ```bash
    lattice-lock doctor
    ```
    *Success Criteria:* All checks pass, especially "AI Providers" and "Config".

---

## Part 4: Cloud Model Connectivity Testing

Before running complex flows, we must verify that the Orchestrator can talk to the cloud.

1.  **List Available Models**
    See which models Lattice Lock sees based on your API keys.
    ```bash
    lattice-lock orchestrator list
    ```
    *Success Criteria:* A table listing models (e.g., `gpt-4`, `claude-3-opus`, `gemini-1.5-pro`) connects successfully.

2.  **Test Connectivity Routing**
    Send a simple test prompt to verify the pipes are clear.
    ```bash
    lattice-lock orchestrator route "Say 'Hello, Lattice Lock!' and nothing else."
    ```
    *Success Criteria:* The model responds with "Hello, Lattice Lock!".

---

## Part 5: Example Project A - AI-Assisted Google Apps Script

**Scenario:** You need to create a new Google Apps Script utility for Gmail but aren't sure of the best approach. We will use the Orchestrator to design it.

1.  **Draft the Request**
    We want a script that labels emails from "no-reply" addresses as "Automated".

2.  **Use the Orchestrator CLI**
    We will ask Lattice Lock to write the code, specifying the context of our project structure (Apps Script).

    ```bash
    lattice-lock orchestrator route \
      "Write a Google Apps Script function for 'apps/gmail/src/label_automation.gs'. \
       It should search for threads from 'no-reply', create an label 'Automated' if missing, \
       and apply it. Follow standard GAS practices."
    ```

3.  **Review & Save**
    *   Copy the output code.
    *   Create the file: `apps/gmail/src/label_automation.gs`
    *   Paste the code.

4.  **Verify (Mental Check)**
    Does the code look like valid JavaScript/Apps Script? The Orchestrator should have handled the syntax correctly.

---

## Part 6: Example Project B - Policy Enforcement (Governance)

**Scenario:** You want to ensure that no one commits Python automation scripts with `print()` statements, enforcing the use of logging instead.

1.  **Define the Rule**
    Edit `lattice.yaml` in the target project root to add a strict rule.

    ```yaml
    rules:
      - id: "no-print-in-automation"
        description: "Automation scripts must use proper logging, not print()."
        severity: "error"
        scope: "automation/**/*.py"
        forbids: "node.is_call_to('print')"
    ```

2.  **Create a Violating File**
    Create a test file `automation/bad_script.py`:

    ```python
    def sync_files():
        print("Starting sync...")  # Violation!
        # logic here
    ```

3.  **Run Validation**
    Execute Sheriff to catch the violation.

    ```bash
    lattice-lock validate
    ```

4.  **Observe Failure**
    *Success Criteria:* The command should fail (exit code 1) and report:
    `[ERROR] no-print-in-automation: Automation scripts must use proper logging... (automation/bad_script.py:2)`

5.  **Fix and Re-Verify**
    Edit `automation/bad_script.py`:
    ```python
    import logging
    
    def sync_files():
        logging.info("Starting sync...")
    ```
    Run `lattice-lock validate` again. It should pass.

---

## Summary of Training

You have successfully:
1.  **Installed** Lattice Lock.
2.  **Initialized** it in a real project (`another_google_automation_agar`).
3.  **Connected** to AI Cloud Providers.
4.  **Generated Code** using the Orchestrator.
5.  **Enforced Quality** using Sheriff policy rules.

This workflow ensures that your automation projects are both accelerated by AI and protected by rigid governance standards.
