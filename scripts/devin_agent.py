#!/usr/bin/env python3
"""
Lattice Lock Framework - Devin Agent Script

This script helps manage Devin AI tasks by interfacing with the prompt tracker.
It shows the next task, displays prompt contents, and tracks progress.

Usage:
    python scripts/devin_agent.py next              # Get next Devin task
    python scripts/devin_agent.py show 2.2.1        # Show prompt for task 2.2.1
    python scripts/devin_agent.py list              # List all Devin tasks
    python scripts/devin_agent.py status            # Show Devin task status
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = REPO_ROOT / "project_prompts"
TRACKER_SCRIPT = REPO_ROOT / "scripts" / "prompt_tracker.py"


def run_tracker_command(args: list[str]) -> dict:
    """Run a prompt_tracker.py command and return parsed JSON output."""
    cmd = [sys.executable, str(TRACKER_SCRIPT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


def load_state() -> dict:
    """Load the prompt tracker state."""
    state_file = PROMPTS_DIR / "project_prompts_state.json"
    with open(state_file) as f:
        return json.load(f)


def cmd_next(args) -> None:
    """Get the next available Devin task."""
    print("\n" + "=" * 60)
    print("DEVIN AGENT - Next Task")
    print("=" * 60 + "\n")
    
    result = run_tracker_command(["next", "--tool", "devin"])
    
    if result.get("status") == "none_available":
        print("No pending Devin tasks available.")
        print("\nAll Devin tasks may be complete or in progress.")
        return
    
    status = result.get("status", "unknown")
    task_id = result.get("id", "unknown")
    title = result.get("title", "unknown")
    file_path = result.get("file", "")
    
    print(f"Status: {status.upper()}")
    print(f"Task ID: {task_id}")
    print(f"Title: {title}")
    print(f"Prompt file: {file_path}")
    
    if file_path and Path(file_path).exists():
        print("\n" + "-" * 60)
        print("PROMPT CONTENTS:")
        print("-" * 60 + "\n")
        with open(file_path) as f:
            print(f.read())
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Read the prompt above and implement the task")
    print("2. When done, run: python scripts/prompt_tracker.py update --id {} --done".format(task_id))
    print("3. After PR merged: python scripts/prompt_tracker.py update --id {} --merged --pr <url>".format(task_id))
    print("=" * 60 + "\n")


def cmd_show(args) -> None:
    """Show the prompt for a specific task ID."""
    task_id = args.task_id
    state = load_state()
    
    prompt = None
    for p in state["prompts"]:
        if p["id"] == task_id and p["tool"] == "devin":
            prompt = p
            break
    
    if not prompt:
        print(f"Error: No Devin task found with ID '{task_id}'", file=sys.stderr)
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"DEVIN TASK: {task_id} - {prompt['title']}")
    print("=" * 60 + "\n")
    
    file_path = PROMPTS_DIR / prompt["file"]
    if file_path.exists():
        with open(file_path) as f:
            print(f.read())
    else:
        print(f"Warning: Prompt file not found at {file_path}")
    
    print("\n" + "-" * 60)
    print("Task Status:")
    print(f"  Picked up: {'Yes' if prompt['picked_up'] else 'No'}")
    print(f"  Done: {'Yes' if prompt['done'] else 'No'}")
    print(f"  Merged: {'Yes' if prompt['merged'] else 'No'}")
    if prompt.get("pr_url"):
        print(f"  PR: {prompt['pr_url']}")
    print("-" * 60 + "\n")


def cmd_list(args) -> None:
    """List all Devin tasks."""
    state = load_state()
    
    print("\n" + "=" * 60)
    print("DEVIN AGENT - All Tasks")
    print("=" * 60 + "\n")
    
    devin_tasks = [p for p in state["prompts"] if p["tool"] == "devin"]
    
    if not devin_tasks:
        print("No Devin tasks found.")
        return
    
    print(f"{'ID':<8} {'Title':<40} {'Status':<12}")
    print("-" * 60)
    
    for task in devin_tasks:
        if task["merged"]:
            status = "MERGED"
        elif task["done"]:
            status = "DONE"
        elif task["picked_up"]:
            status = "IN PROGRESS"
        else:
            status = "PENDING"
        
        title = task["title"][:38] + ".." if len(task["title"]) > 40 else task["title"]
        print(f"{task['id']:<8} {title:<40} {status:<12}")
    
    print("\n" + "-" * 60)
    print(f"Total: {len(devin_tasks)} tasks")
    
    pending = sum(1 for t in devin_tasks if not t["picked_up"])
    in_progress = sum(1 for t in devin_tasks if t["picked_up"] and not t["done"])
    done = sum(1 for t in devin_tasks if t["done"] and not t["merged"])
    merged = sum(1 for t in devin_tasks if t["merged"])
    
    print(f"Pending: {pending} | In Progress: {in_progress} | Done: {done} | Merged: {merged}")
    print("-" * 60 + "\n")


def cmd_status(args) -> None:
    """Show overall Devin task status."""
    state = load_state()
    devin_tasks = [p for p in state["prompts"] if p["tool"] == "devin"]
    
    print("\n" + "=" * 60)
    print("DEVIN AGENT - Status Summary")
    print("=" * 60 + "\n")
    
    total = len(devin_tasks)
    pending = sum(1 for t in devin_tasks if not t["picked_up"])
    in_progress = sum(1 for t in devin_tasks if t["picked_up"] and not t["done"])
    done = sum(1 for t in devin_tasks if t["done"] and not t["merged"])
    merged = sum(1 for t in devin_tasks if t["merged"])
    
    print(f"Total Devin tasks: {total}")
    print(f"  Pending:     {pending} ({100*pending//total if total else 0}%)")
    print(f"  In Progress: {in_progress}")
    print(f"  Done:        {done}")
    print(f"  Merged:      {merged} ({100*merged//total if total else 0}%)")
    
    # Show current in-progress task
    current = [t for t in devin_tasks if t["picked_up"] and not t["done"]]
    if current:
        print("\nCurrently in progress:")
        for t in current:
            print(f"  - {t['id']}: {t['title']}")
    
    # Show next pending task
    next_pending = [t for t in devin_tasks if not t["picked_up"]]
    if next_pending:
        print(f"\nNext pending task: {next_pending[0]['id']} - {next_pending[0]['title']}")
    
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Devin Agent - Manage Devin AI tasks for Lattice Lock Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/devin_agent.py next           # Get next task
  python scripts/devin_agent.py show 2.2.1     # Show task 2.2.1
  python scripts/devin_agent.py list           # List all tasks
  python scripts/devin_agent.py status         # Show status summary
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # next command
    subparsers.add_parser("next", help="Get the next available Devin task")
    
    # show command
    show_parser = subparsers.add_parser("show", help="Show prompt for a specific task")
    show_parser.add_argument("task_id", help="Task ID (e.g., 2.2.1)")
    
    # list command
    subparsers.add_parser("list", help="List all Devin tasks")
    
    # status command
    subparsers.add_parser("status", help="Show Devin task status summary")
    
    args = parser.parse_args()
    
    if args.command == "next":
        cmd_next(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
