#!/usr/bin/env python3
"""
Lattice Lock Framework - Gemini CLI Agent Script

This script generates prompts for Gemini CLI (terminal commands and scripts).
Copy the output and paste it into your Gemini CLI terminal session.

Usage:
    python scripts/gemini_cli_agent.py 2.2.1       # Get prompt for task 2.2.1
    python scripts/gemini_cli_agent.py list        # List all available tasks
    python scripts/gemini_cli_agent.py --help      # Show help
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_prompts import get_prompt, list_tasks


def cmd_get_prompt(task_id: str) -> None:
    """Get and display the Gemini CLI prompt for a task."""
    prompt = get_prompt("gemini_cli", task_id)

    if not prompt:
        print(f"Error: No Gemini CLI prompt found for task '{task_id}'", file=sys.stderr)
        print("\nAvailable tasks:", file=sys.stderr)
        for tid in list_tasks("gemini_cli"):
            print(f"  - {tid}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"GEMINI CLI PROMPT - Task {task_id}")
    print("=" * 70)
    print("\nCopy everything below this line and paste into Gemini CLI:")
    print("-" * 70 + "\n")
    print(prompt)
    print("\n" + "-" * 70)
    print("\nInstructions:")
    print("1. Open your Gemini CLI terminal session")
    print("2. Paste the prompt above")
    print("3. Review the generated commands BEFORE executing")
    print("4. Replace any placeholders (ACCOUNT_ID, REGION, etc.) with actual values")
    print("5. Execute commands selectively - do NOT run destructive commands blindly")
    print("=" * 70 + "\n")


def cmd_list() -> None:
    """List all available Gemini CLI tasks."""
    tasks = list_tasks("gemini_cli")

    print("\n" + "=" * 60)
    print("GEMINI CLI AGENT - Available Tasks")
    print("=" * 60 + "\n")

    if not tasks:
        print("No Gemini CLI tasks available.")
        return

    task_descriptions = {
        "2.2.1": "AWS CodePipeline bootstrap commands",
        "2.3.1": "GCP Cloud Build bootstrap commands",
        "3.1.1": "Error classification testing commands",
        "3.1.2": "Error middleware testing commands",
        "4.3.1": "Pilot Project 1 setup commands",
        "4.3.2": "Pilot Project 2 setup commands",
        "5.1.1": "Prompt Architect Agent setup commands",
        "5.1.2": "Prompt Architect integration commands",
    }

    print(f"{'Task ID':<10} {'Description':<50}")
    print("-" * 60)

    for task_id in tasks:
        desc = task_descriptions.get(task_id, "No description")
        print(f"{task_id:<10} {desc:<50}")

    print("\n" + "-" * 60)
    print(f"Total: {len(tasks)} tasks")
    print("\nUsage: python scripts/gemini_cli_agent.py <task_id>")
    print("-" * 60 + "\n")


def main():
    """Entry point for the Gemini CLI agent script."""
    parser = argparse.ArgumentParser(
        description="Gemini CLI Agent - Generate prompts for terminal commands and scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/gemini_cli_agent.py 2.2.1    # Get AWS CodePipeline commands
  python scripts/gemini_cli_agent.py 3.1.1    # Get error classification test commands
  python scripts/gemini_cli_agent.py list     # List all available tasks

Workflow:
  1. Run this script with a task ID
  2. Copy the generated prompt
  3. Open Gemini CLI in your terminal
  4. Paste the prompt and review the output
  5. IMPORTANT: Review all commands before executing
  6. Replace placeholders with actual values
  7. Execute commands selectively

WARNING:
  Some commands may be destructive (delete-stack, etc.).
  Always review before executing!
        """
    )

    parser.add_argument(
        "task_id",
        nargs="?",
        help="Task ID (e.g., 2.2.1) or 'list' to show all tasks"
    )

    args = parser.parse_args()

    if not args.task_id:
        parser.print_help()
        sys.exit(1)

    if args.task_id == "list":
        cmd_list()
    else:
        cmd_get_prompt(args.task_id)


if __name__ == "__main__":
    main()
