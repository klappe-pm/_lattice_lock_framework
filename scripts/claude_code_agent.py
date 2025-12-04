#!/usr/bin/env python3
"""
Lattice Lock Framework - Claude Code Agent Script

This script generates prompts for Claude Code (IDE-based AI assistant).
Copy the output and paste it into Claude Code with the repo open.

Usage:
    python scripts/claude_code_agent.py 2.2.1       # Get prompt for task 2.2.1
    python scripts/claude_code_agent.py list        # List all available tasks
    python scripts/claude_code_agent.py --help      # Show help
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_prompts import get_prompt, list_tasks


def cmd_get_prompt(task_id: str) -> None:
    """Get and display the Claude Code prompt for a task."""
    prompt = get_prompt("claude_code", task_id)

    if not prompt:
        print(f"Error: No Claude Code prompt found for task '{task_id}'", file=sys.stderr)
        print("\nAvailable tasks:", file=sys.stderr)
        for tid in list_tasks("claude_code"):
            print(f"  - {tid}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"CLAUDE CODE PROMPT - Task {task_id}")
    print("=" * 70)
    print("\nCopy everything below this line and paste into Claude Code:")
    print("-" * 70 + "\n")
    print(prompt)
    print("\n" + "-" * 70)
    print("\nInstructions:")
    print("1. Open the lattice-lock-framework repo in your IDE")
    print("2. Open Claude Code (or your Claude-powered IDE assistant)")
    print("3. Paste the prompt above")
    print("4. Review and apply the generated code")
    print("=" * 70 + "\n")


def cmd_list() -> None:
    """List all available Claude Code tasks."""
    tasks = list_tasks("claude_code")

    print("\n" + "=" * 60)
    print("CLAUDE CODE AGENT - Available Tasks")
    print("=" * 60 + "\n")

    if not tasks:
        print("No Claude Code tasks available.")
        return

    task_descriptions = {
        "2.2.1": "AWS CodePipeline template design",
        "2.3.1": "GCP Cloud Build template design",
        "3.1.1": "Error classification system implementation",
        "3.1.2": "Error handling middleware implementation",
        "4.3.1": "Pilot Project 1 scaffolding (API Service)",
        "4.3.2": "Pilot Project 2 scaffolding (CLI Tool)",
        "5.1.1": "Prompt Architect Agent core implementation",
        "5.1.2": "Prompt Architect Agent integration",
    }

    print(f"{'Task ID':<10} {'Description':<50}")
    print("-" * 60)

    for task_id in tasks:
        desc = task_descriptions.get(task_id, "No description")
        print(f"{task_id:<10} {desc:<50}")

    print("\n" + "-" * 60)
    print(f"Total: {len(tasks)} tasks")
    print("\nUsage: python scripts/claude_code_agent.py <task_id>")
    print("-" * 60 + "\n")


def main():
    """Entry point for the Claude Code agent script."""
    parser = argparse.ArgumentParser(
        description="Claude Code Agent - Generate prompts for Claude Code IDE assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/claude_code_agent.py 2.2.1    # Get prompt for AWS CodePipeline
  python scripts/claude_code_agent.py 3.1.1    # Get prompt for error classification
  python scripts/claude_code_agent.py list     # List all available tasks

Workflow:
  1. Run this script with a task ID
  2. Copy the generated prompt
  3. Open Claude Code in your IDE with the repo open
  4. Paste the prompt and review the output
  5. Apply the generated code to your project
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
