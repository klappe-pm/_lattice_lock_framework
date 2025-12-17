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

# Add src to sys.path to allow importing lattice_lock
sys.path.append(str(REPO_ROOT / "src"))
try:
    from lattice_lock.utils.safe_path import resolve_under_root
except ImportError:
    print("Error: Could not import lattice_lock.utils.safe_path. Ensure you are running from the project root or src is in PYTHONPATH.", file=sys.stderr)
    sys.exit(1)


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


def cmd_add_prompt(args) -> None:
    """Add a newly generated prompt to state."""
    state = load_state()
    prompts = state["prompts"]

    # Check if prompt ID already exists
    for p in prompts:
        if p["id"] == args.id:
            print(json.dumps({
                "status": "error",
                "message": f"Prompt '{args.id}' already exists"
            }, indent=2), file=sys.stderr)
            sys.exit(1)

    # Parse ID to extract phase and epic
    parts = args.id.split(".")
    if len(parts) < 2:
        print(json.dumps({
            "status": "error",
            "message": f"Invalid prompt ID format: {args.id}. Expected X.X.X"
        }, indent=2), file=sys.stderr)
        sys.exit(1)

    phase = parts[0]
    epic = f"{parts[0]}.{parts[1]}"

    # Create new prompt entry
    new_prompt = {
        "id": args.id,
        "phase": phase,
        "epic": epic,
        "title": args.title,
        "tool": args.tool,
        "file": args.file,
        "picked_up": False,
        "done": False,
        "merged": False,
        "model_used": None,
        "start_time": None,
        "end_time": None,
        "duration_minutes": None,
        "pr_url": None
    }

    # Find the right position to insert (maintain order by ID)
    insert_index = len(prompts)
    for i, p in enumerate(prompts):
        if _compare_ids(args.id, p["id"]) < 0:
            insert_index = i
            break

    prompts.insert(insert_index, new_prompt)
    state["metadata"]["total_prompts"] = len(prompts)

    save_state(state)

    print(json.dumps({
        "status": "added",
        "id": args.id,
        "title": args.title,
        "tool": args.tool,
        "file": args.file
    }, indent=2))


def cmd_batch_add(args) -> None:
    """Add multiple prompts at once from a JSON file."""
    state = load_state()
    prompts = state["prompts"]

    # Read prompts from file
    try:
        # Add src to sys.path to import safe_path
        sys.path.append(str(REPO_ROOT / "src"))
        from lattice_lock.utils.safe_path import resolve_under_root
        batch_file = resolve_under_root(args.file)
    except (ImportError, ValueError) as e:
        print(f"Error validating path: {e}", file=sys.stderr)
        sys.exit(1)
    if not batch_file.exists():
        print(f"Error: Batch file not found at {batch_file}", file=sys.stderr)
        sys.exit(1)

    with open(batch_file, "r") as f:
        new_prompts = json.load(f)

    if not isinstance(new_prompts, list):
        print("Error: Batch file must contain a JSON array of prompts", file=sys.stderr)
        sys.exit(1)

    # Track existing IDs
    existing_ids = {p["id"] for p in prompts}
    added = []
    skipped = []

    for entry in new_prompts:
        prompt_id = entry.get("id")
        if not prompt_id:
            skipped.append({"entry": entry, "reason": "missing id"})
            continue

        if prompt_id in existing_ids:
            skipped.append({"id": prompt_id, "reason": "already exists"})
            continue

        # Parse ID to extract phase and epic
        parts = prompt_id.split(".")
        if len(parts) < 2:
            skipped.append({"id": prompt_id, "reason": "invalid id format"})
            continue

        phase = parts[0]
        epic = f"{parts[0]}.{parts[1]}"

        new_prompt = {
            "id": prompt_id,
            "phase": phase,
            "epic": epic,
            "title": entry.get("title", "Untitled"),
            "tool": entry.get("tool", "unknown"),
            "file": entry.get("file", ""),
            "picked_up": False,
            "done": False,
            "merged": False,
            "model_used": None,
            "start_time": None,
            "end_time": None,
            "duration_minutes": None,
            "pr_url": None
        }

        prompts.append(new_prompt)
        existing_ids.add(prompt_id)
        added.append(prompt_id)

    # Sort prompts by ID
    prompts.sort(key=lambda p: [int(x) for x in p["id"].split(".")])
    state["prompts"] = prompts
    state["metadata"]["total_prompts"] = len(prompts)

    save_state(state)

    print(json.dumps({
        "status": "batch_complete",
        "added": added,
        "added_count": len(added),
        "skipped": skipped,
        "skipped_count": len(skipped)
    }, indent=2))


def cmd_validate_state(args) -> None:
    """Validate that state matches actual prompt files."""
    state = load_state()
    prompts = state["prompts"]

    issues = []
    valid = []

    for p in prompts:
        try:
            file_path = resolve_under_root(str(PROMPTS_DIR), p["file"])
            path_obj = Path(file_path)
            if path_obj.exists():
                valid.append(p["id"])
            else:
                issues.append({
                    "id": p["id"],
                    "file": p["file"],
                    "issue": "file_not_found"
                })
        except ValueError:
             issues.append({
                "id": p["id"],
                "file": p["file"],
                "issue": "invalid_path_traversal"
            })

    # Check for orphan files (files not in state)
    if args.check_orphans:
        tracked_files = {p["file"] for p in prompts}
        for phase_dir in PROMPTS_DIR.iterdir():
            if phase_dir.is_dir() and phase_dir.name.startswith("phase"):
                for prompt_file in phase_dir.glob("*.md"):
                    relative_path = f"{phase_dir.name}/{prompt_file.name}"
                    if relative_path not in tracked_files:
                        issues.append({
                            "file": relative_path,
                            "issue": "orphan_file"
                        })

    is_valid = len(issues) == 0

    result = {
        "status": "valid" if is_valid else "invalid",
        "total_prompts": len(prompts),
        "valid_count": len(valid),
        "issue_count": len(issues)
    }

    if issues:
        result["issues"] = issues

    print(json.dumps(result, indent=2))

    if not is_valid:
        sys.exit(1)


def _compare_ids(id1: str, id2: str) -> int:
    """Compare two prompt IDs. Returns -1 if id1 < id2, 0 if equal, 1 if id1 > id2."""
    parts1 = [int(x) for x in id1.split(".")]
    parts2 = [int(x) for x in id2.split(".")]

    for p1, p2 in zip(parts1, parts2):
        if p1 < p2:
            return -1
        if p1 > p2:
            return 1

    if len(parts1) < len(parts2):
        return -1
    if len(parts1) > len(parts2):
        return 1

    return 0


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

    # add-prompt command
    add_parser = subparsers.add_parser("add-prompt", help="Add a newly generated prompt to state")
    add_parser.add_argument("--id", required=True, help="Prompt ID (e.g., 1.1.3)")
    add_parser.add_argument("--title", required=True, help="Prompt title")
    add_parser.add_argument("--tool", required=True,
                           choices=["devin", "gemini", "codex", "claude_cli", "claude_app", "claude_docs"],
                           help="Tool identifier")
    add_parser.add_argument("--file", required=True, help="Relative file path within project_prompts/")

    # batch-add command
    batch_parser = subparsers.add_parser("batch-add", help="Add multiple prompts from a JSON file")
    batch_parser.add_argument("--file", required=True, help="Path to JSON file containing prompts array")

    # validate-state command
    validate_parser = subparsers.add_parser("validate-state", help="Validate state matches actual files")
    validate_parser.add_argument("--check-orphans", action="store_true",
                                 help="Also check for orphan files not tracked in state")

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
    elif args.command == "add-prompt":
        cmd_add_prompt(args)
    elif args.command == "batch-add":
        cmd_batch_add(args)
    elif args.command == "validate-state":
        cmd_validate_state(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
