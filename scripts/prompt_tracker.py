#!/usr/bin/env python3
"""
Lattice Lock Framework - Project Prompts Tracker

This script manages the execution tracking of project prompts.
It maintains a JSON state file and generates a markdown tracker.

Usage:
    python scripts/prompt_tracker.py next --tool devin [--model "model-name"]
    python scripts/prompt_tracker.py update --id 1.1.1 --done --merged [--pr "url"]
    python scripts/prompt_tracker.py reset --id 1.1.1
    python scripts/prompt_tracker.py status
    python scripts/prompt_tracker.py regenerate
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Paths relative to repo root
REPO_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = REPO_ROOT / "project_prompts"
STATE_FILE = PROMPTS_DIR / "project_prompts_state.json"
TRACKER_FILE = PROMPTS_DIR / "project_prompts_tracker.md"


def load_state() -> dict:
    """Load the JSON state file."""
    if not STATE_FILE.exists():
        print(f"Error: State file not found at {STATE_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """Save the JSON state file and regenerate markdown."""
    state["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    generate_markdown(state)


def generate_markdown(state: dict) -> None:
    """Generate the markdown tracker from JSON state."""
    prompts = state["prompts"]
    tool_defs = state["tool_definitions"]
    phase_defs = state["phase_definitions"]
    
    # Calculate summary stats
    total = len(prompts)
    delivered = sum(1 for p in prompts if p["merged"])
    in_progress = sum(1 for p in prompts if p["picked_up"] and not p["done"])
    pending = sum(1 for p in prompts if not p["picked_up"])
    
    # Group by phase
    phases = {}
    for p in prompts:
        phase = p["phase"]
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(p)
    
    # Build markdown
    lines = [
        "# Lattice Lock Framework - Project Prompts Tracker",
        "",
        f"**Last Updated:** {state['metadata']['last_updated']}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Prompts | {total} |",
        f"| Delivered (Merged) | {delivered} |",
        f"| In Progress | {in_progress} |",
        f"| Pending | {pending} |",
        "",
        "---",
        "",
    ]
    
    # Generate tables for each phase
    for phase_num in sorted(phases.keys()):
        phase_prompts = phases[phase_num]
        phase_name = phase_defs.get(phase_num, f"Phase {phase_num}")
        
        lines.append(f"## Phase {phase_num}: {phase_name}")
        lines.append("")
        lines.append("| ID | Title | Tool | Picked Up | Done | Merged | Model | Start Time | End Time | Duration (min) | PR |")
        lines.append("|:---|:------|:-----|:----------|:-----|:-------|:------|:-----------|:---------|:---------------|:---|")
        
        for p in phase_prompts:
            tool_name = tool_defs.get(p["tool"], p["tool"])
            picked = "Yes" if p["picked_up"] else "-"
            done = "Yes" if p["done"] else "-"
            merged = "Yes" if p["merged"] else "-"
            model = p["model_used"] or "-"
            start = p["start_time"] or "-"
            end = p["end_time"] or "-"
            duration = str(p["duration_minutes"]) if p["duration_minutes"] is not None else "-"
            pr = f"[PR]({p['pr_url']})" if p["pr_url"] else "-"
            
            lines.append(f"| {p['id']} | {p['title']} | {tool_name} | {picked} | {done} | {merged} | {model} | {start} | {end} | {duration} | {pr} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Add usage instructions
    lines.extend([
        "## Usage",
        "",
        "### Pick Up Next Prompt",
        "",
        "When you receive `cont next`, run:",
        "",
        "```bash",
        'python scripts/prompt_tracker.py next --tool <your-tool> --model "<model-name>"',
        "```",
        "",
        "Tool identifiers: `devin`, `gemini`, `codex`, `claude_cli`, `claude_app`, `claude_docs`",
        "",
        "### Mark Prompt as Done/Merged",
        "",
        "```bash",
        'python scripts/prompt_tracker.py update --id 1.1.1 --done --merged --pr "https://github.com/..."',
        "```",
        "",
        "### Reset a Prompt",
        "",
        "```bash",
        "python scripts/prompt_tracker.py reset --id 1.1.1",
        "```",
        "",
        "### View Status",
        "",
        "```bash",
        "python scripts/prompt_tracker.py status",
        "```",
        "",
        "---",
        "",
        "## Status Legend",
        "",
        "- **Picked Up**: An agent has started working on this prompt",
        "- **Done**: The implementation is complete",
        "- **Merged**: The PR has been merged to the remote repository (DELIVERED)",
        "",
        "A prompt is considered **DELIVERED** only when Merged = Yes",
        "",
    ])
    
    with open(TRACKER_FILE, "w") as f:
        f.write("\n".join(lines))
    
    print(f"Tracker regenerated: {TRACKER_FILE}")


def cmd_next(args) -> None:
    """Find and pick up the next available prompt for a tool."""
    state = load_state()
    prompts = state["prompts"]
    tool = args.tool
    model = args.model
    
    # First, check for in-progress prompt for this tool
    for p in prompts:
        if p["tool"] == tool and p["picked_up"] and not p["done"] and not p["merged"]:
            print(json.dumps({
                "status": "resuming",
                "id": p["id"],
                "title": p["title"],
                "tool": p["tool"],
                "file": str(PROMPTS_DIR / p["file"])
            }, indent=2))
            return
    
    # Find next available prompt for this tool
    for p in prompts:
        if p["tool"] == tool and not p["picked_up"] and not p["done"] and not p["merged"]:
            # Mark as picked up
            p["picked_up"] = True
            p["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if model:
                p["model_used"] = model
            
            save_state(state)
            
            print(json.dumps({
                "status": "assigned",
                "id": p["id"],
                "title": p["title"],
                "tool": p["tool"],
                "file": str(PROMPTS_DIR / p["file"])
            }, indent=2))
            return
    
    # No prompts available
    print(json.dumps({
        "status": "none_available",
        "tool": tool,
        "message": f"No pending prompts for tool '{tool}'"
    }, indent=2))


def cmd_update(args) -> None:
    """Update a prompt's status."""
    state = load_state()
    prompts = state["prompts"]
    
    # Find prompt by ID
    prompt = None
    for p in prompts:
        if p["id"] == args.id:
            prompt = p
            break
    
    if not prompt:
        print(f"Error: Prompt '{args.id}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Update fields
    if args.done:
        prompt["done"] = True
    if args.merged:
        prompt["merged"] = True
        if not prompt["end_time"]:
            prompt["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate duration
        if prompt["start_time"] and prompt["end_time"]:
            start = datetime.strptime(prompt["start_time"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(prompt["end_time"], "%Y-%m-%d %H:%M:%S")
            prompt["duration_minutes"] = round((end - start).total_seconds() / 60)
    
    if args.pr:
        prompt["pr_url"] = args.pr
    
    if args.model:
        prompt["model_used"] = args.model
    
    save_state(state)
    
    print(json.dumps({
        "status": "updated",
        "id": prompt["id"],
        "done": prompt["done"],
        "merged": prompt["merged"],
        "duration_minutes": prompt["duration_minutes"]
    }, indent=2))


def cmd_reset(args) -> None:
    """Reset a prompt to pending state."""
    state = load_state()
    prompts = state["prompts"]
    
    # Find prompt by ID
    prompt = None
    for p in prompts:
        if p["id"] == args.id:
            prompt = p
            break
    
    if not prompt:
        print(f"Error: Prompt '{args.id}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Reset fields
    prompt["picked_up"] = False
    prompt["done"] = False
    prompt["merged"] = False
    prompt["model_used"] = None
    prompt["start_time"] = None
    prompt["end_time"] = None
    prompt["duration_minutes"] = None
    prompt["pr_url"] = None
    
    save_state(state)
    
    print(json.dumps({
        "status": "reset",
        "id": prompt["id"]
    }, indent=2))


def cmd_status(args) -> None:
    """Show overall status summary."""
    state = load_state()
    prompts = state["prompts"]
    tool_defs = state["tool_definitions"]
    
    total = len(prompts)
    delivered = sum(1 for p in prompts if p["merged"])
    in_progress = sum(1 for p in prompts if p["picked_up"] and not p["done"])
    pending = sum(1 for p in prompts if not p["picked_up"])
    
    # Per-tool breakdown
    tool_stats = {}
    for p in prompts:
        tool = p["tool"]
        if tool not in tool_stats:
            tool_stats[tool] = {"total": 0, "delivered": 0, "in_progress": 0, "pending": 0}
        tool_stats[tool]["total"] += 1
        if p["merged"]:
            tool_stats[tool]["delivered"] += 1
        elif p["picked_up"] and not p["done"]:
            tool_stats[tool]["in_progress"] += 1
        elif not p["picked_up"]:
            tool_stats[tool]["pending"] += 1
    
    print(f"\n{'='*60}")
    print("LATTICE LOCK FRAMEWORK - PROMPT TRACKER STATUS")
    print(f"{'='*60}\n")
    print(f"Total Prompts:    {total}")
    print(f"Delivered:        {delivered} ({100*delivered//total}%)")
    print(f"In Progress:      {in_progress}")
    print(f"Pending:          {pending}")
    print(f"\n{'-'*60}")
    print("BY TOOL:")
    print(f"{'-'*60}")
    
    for tool, stats in sorted(tool_stats.items()):
        tool_name = tool_defs.get(tool, tool)
        print(f"  {tool_name:20} | Total: {stats['total']:2} | Done: {stats['delivered']:2} | WIP: {stats['in_progress']:2} | Pending: {stats['pending']:2}")
    
    print(f"\n{'='*60}\n")


def cmd_regenerate(args) -> None:
    """Regenerate the markdown tracker from JSON state."""
    state = load_state()
    generate_markdown(state)


def main():
    parser = argparse.ArgumentParser(
        description="Lattice Lock Framework - Project Prompts Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/prompt_tracker.py next --tool devin --model "gpt-4"
  python scripts/prompt_tracker.py update --id 1.1.1 --done --merged --pr "https://..."
  python scripts/prompt_tracker.py reset --id 1.1.1
  python scripts/prompt_tracker.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # next command
    next_parser = subparsers.add_parser("next", help="Pick up the next available prompt")
    next_parser.add_argument("--tool", required=True, 
                            choices=["devin", "gemini", "codex", "claude_cli", "claude_app", "claude_docs"],
                            help="Tool identifier")
    next_parser.add_argument("--model", help="Model name being used")
    
    # update command
    update_parser = subparsers.add_parser("update", help="Update a prompt's status")
    update_parser.add_argument("--id", required=True, help="Prompt ID (e.g., 1.1.1)")
    update_parser.add_argument("--done", action="store_true", help="Mark as done")
    update_parser.add_argument("--merged", action="store_true", help="Mark as merged")
    update_parser.add_argument("--pr", help="PR URL")
    update_parser.add_argument("--model", help="Model name used")
    
    # reset command
    reset_parser = subparsers.add_parser("reset", help="Reset a prompt to pending state")
    reset_parser.add_argument("--id", required=True, help="Prompt ID (e.g., 1.1.1)")
    
    # status command
    subparsers.add_parser("status", help="Show overall status summary")
    
    # regenerate command
    subparsers.add_parser("regenerate", help="Regenerate markdown tracker from JSON")
    
    args = parser.parse_args()
    
    if args.command == "next":
        cmd_next(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "reset":
        cmd_reset(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "regenerate":
        cmd_regenerate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
