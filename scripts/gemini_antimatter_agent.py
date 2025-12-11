#!/usr/bin/env python3
"""
Lattice Lock Framework - Gemini Antimatter Agent Script

This script generates prompts for Gemini in Antimatter (design docs and specifications).
Copy the output and paste it into your Gemini/Antimatter workspace.

Usage:
    python scripts/gemini_antimatter_agent.py 2.2.1   # Get prompt for task 2.2.1
    python scripts/gemini_antimatter_agent.py list    # List all available tasks
    python scripts/gemini_antimatter_agent.py --help  # Show help
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_prompts import get_prompt, list_tasks


def cmd_get_prompt(task_id: str) -> None:
    """Get and display the Gemini Antimatter prompt for a task."""
    prompt = get_prompt("gemini_antimatter", task_id)

    if not prompt:
        print(f"Error: No Gemini Antimatter prompt found for task '{task_id}'", file=sys.stderr)
        print("\nAvailable tasks:", file=sys.stderr)
        for tid in list_tasks("gemini_antimatter"):
            print(f"  - {tid}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"GEMINI ANTIMATTER PROMPT - Task {task_id}")
    print("=" * 70)
    print("\nCopy everything below this line and paste into Gemini/Antimatter:")
    print("-" * 70 + "\n")
    print(prompt)
    print("\n" + "-" * 70)
    print("\nInstructions:")
    print("1. Open your Gemini workspace in Antimatter")
    print("2. Paste the prompt above")
    print("3. Review the generated design document")
    print("4. Save the output to the appropriate location in the repo")
    print("=" * 70 + "\n")


def cmd_list() -> None:
    """List all available Gemini Antimatter tasks."""
    tasks = list_tasks("gemini_antimatter")

    print("\n" + "=" * 60)
    print("GEMINI ANTIMATTER AGENT - Available Tasks")
    print("=" * 60 + "\n")

    if not tasks:
        print("No Gemini Antimatter tasks available.")
        return

    task_descriptions = {
        "2.2.1": "AWS CodePipeline design document",
        "2.3.1": "GCP Cloud Build design document",
        "3.1.1": "Error classification system design",
        "3.1.2": "Error handling middleware design",
        "4.3.1": "Pilot Project 1 design (API Service)",
        "4.3.2": "Pilot Project 2 design (CLI Tool)",
        "5.1.1": "Prompt Architect Agent specification",
        "5.1.2": "Prompt Architect integration specification",
        "6.1.1": "Orchestrator Capabilities Contract Design",
        "6.1.3": "Provider Client and Fallback Strategy Design",
    }

    print(f"{'Task ID':<10} {'Description':<50}")
    print("-" * 60)

    for task_id in tasks:
        desc = task_descriptions.get(task_id, "No description")
        print(f"{task_id:<10} {desc:<50}")

    print("\n" + "-" * 60)
    print(f"Total: {len(tasks)} tasks")
    print("\nUsage: python scripts/gemini_antimatter_agent.py <task_id>")
    print("-" * 60 + "\n")


def main():
    """Entry point for the Gemini Antimatter agent script."""
    parser = argparse.ArgumentParser(
        description="Gemini Antimatter Agent - Generate prompts for design docs and specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/gemini_antimatter_agent.py 2.2.1    # Get AWS CodePipeline design doc prompt
  python scripts/gemini_antimatter_agent.py 3.1.1    # Get error classification design prompt
  python scripts/gemini_antimatter_agent.py list     # List all available tasks

Workflow:
  1. Run this script with a task ID
  2. Copy the generated prompt
  3. Open Gemini in your Antimatter workspace
  4. Paste the prompt and review the output
  5. Save the design document to the repo
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
