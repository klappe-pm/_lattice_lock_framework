"""
TrackerClient - Interface for interacting with the prompt tracker system.

This module provides a Python API for the prompt tracker, allowing the
Prompt Architect Agent to programmatically add and manage prompts.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PromptEntry:
    """Represents a prompt entry in the tracker state."""
    id: str
    phase: str
    epic: str
    title: str
    tool: str
    file: str
    picked_up: bool = False
    done: bool = False
    merged: bool = False
    model_used: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    pr_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "phase": self.phase,
            "epic": self.epic,
            "title": self.title,
            "tool": self.tool,
            "file": self.file,
            "picked_up": self.picked_up,
            "done": self.done,
            "merged": self.merged,
            "model_used": self.model_used,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "pr_url": self.pr_url
        }


class TrackerClient:
    """
    Client for interacting with the prompt tracker system.

    Provides methods to add, update, and query prompts in the tracking system.
    Can operate in two modes:
    - CLI mode: Uses subprocess calls to prompt_tracker.py
    - Direct mode: Directly reads/writes the JSON state file
    """

    VALID_TOOLS = ["devin", "gemini", "codex", "claude_cli", "claude_app", "claude_docs"]

    def __init__(self, repo_root: Optional[Path] = None, use_cli: bool = False):
        """
        Initialize the TrackerClient.

        Args:
            repo_root: Path to the repository root. If None, auto-detected.
            use_cli: If True, use CLI subprocess calls. If False, direct file access.
        """
        if repo_root is None:
            # Auto-detect repo root by looking for project_prompts directory
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "project_prompts").exists():
                    repo_root = parent
                    break
            if repo_root is None:
                repo_root = Path.cwd()

        self.repo_root = repo_root
        self.prompts_dir = repo_root / "project_prompts"
        self.state_file = self.prompts_dir / "project_prompts_state.json"
        self.tracker_script = repo_root / "scripts" / "prompt_tracker.py"
        self.use_cli = use_cli

    def _load_state(self) -> Dict[str, Any]:
        """Load the JSON state file."""
        if not self.state_file.exists():
            raise FileNotFoundError(f"State file not found at {self.state_file}")
        with open(self.state_file, "r") as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save the JSON state file and regenerate markdown."""
        state["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
        # Regenerate markdown tracker
        self.regenerate()

    def _run_cli(self, command: List[str]) -> Dict[str, Any]:
        """Run a tracker CLI command and return the parsed JSON output."""
        full_cmd = [sys.executable, str(self.tracker_script)] + command
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            cwd=str(self.repo_root)
        )
        if result.returncode != 0:
            error_output = result.stderr or result.stdout
            raise RuntimeError(f"Tracker command failed: {error_output}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw_output": result.stdout}

    def add_prompt(
        self,
        prompt_id: str,
        title: str,
        tool: str,
        file_path: str,
        phase: Optional[str] = None,
        epic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a newly generated prompt to the tracker state.

        Args:
            prompt_id: The prompt ID (e.g., "5.4.1")
            title: Human-readable title
            tool: Tool identifier (must be in VALID_TOOLS)
            file_path: Relative file path within project_prompts/
            phase: Phase number (auto-extracted from ID if not provided)
            epic: Epic ID (auto-extracted from ID if not provided)

        Returns:
            Dict with status and added prompt info.

        Raises:
            ValueError: If tool is invalid or prompt already exists.
        """
        if tool not in self.VALID_TOOLS:
            raise ValueError(f"Invalid tool '{tool}'. Must be one of: {self.VALID_TOOLS}")

        if self.use_cli:
            return self._run_cli([
                "add-prompt",
                "--id", prompt_id,
                "--title", title,
                "--tool", tool,
                "--file", file_path
            ])

        # Direct mode
        state = self._load_state()
        prompts = state["prompts"]

        # Check if already exists
        for p in prompts:
            if p["id"] == prompt_id:
                raise ValueError(f"Prompt '{prompt_id}' already exists")

        # Parse ID if phase/epic not provided
        parts = prompt_id.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid prompt ID format: {prompt_id}. Expected X.X.X")

        if phase is None:
            phase = parts[0]
        if epic is None:
            epic = f"{parts[0]}.{parts[1]}"

        new_prompt = PromptEntry(
            id=prompt_id,
            phase=phase,
            epic=epic,
            title=title,
            tool=tool,
            file=file_path
        )

        # Insert in sorted order
        prompts.append(new_prompt.to_dict())
        prompts.sort(key=lambda p: [int(x) for x in p["id"].split(".")])
        state["prompts"] = prompts
        state["metadata"]["total_prompts"] = len(prompts)

        self._save_state(state)

        return {
            "status": "added",
            "id": prompt_id,
            "title": title,
            "tool": tool,
            "file": file_path
        }

    def update_prompt(
        self,
        prompt_id: str,
        done: Optional[bool] = None,
        merged: Optional[bool] = None,
        pr_url: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a prompt's status.

        Args:
            prompt_id: The prompt ID to update
            done: Mark as done
            merged: Mark as merged
            pr_url: PR URL
            model: Model used

        Returns:
            Dict with update status.
        """
        if self.use_cli:
            cmd = ["update", "--id", prompt_id]
            if done:
                cmd.append("--done")
            if merged:
                cmd.append("--merged")
            if pr_url:
                cmd.extend(["--pr", pr_url])
            if model:
                cmd.extend(["--model", model])
            return self._run_cli(cmd)

        # Direct mode
        state = self._load_state()
        prompts = state["prompts"]

        prompt = None
        for p in prompts:
            if p["id"] == prompt_id:
                prompt = p
                break

        if prompt is None:
            raise ValueError(f"Prompt '{prompt_id}' not found")

        if done is not None:
            prompt["done"] = done
        if merged is not None:
            prompt["merged"] = merged
            if merged and not prompt["end_time"]:
                prompt["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if prompt["start_time"]:
                    start = datetime.strptime(prompt["start_time"], "%Y-%m-%d %H:%M:%S")
                    end = datetime.strptime(prompt["end_time"], "%Y-%m-%d %H:%M:%S")
                    prompt["duration_minutes"] = round((end - start).total_seconds() / 60)
        if pr_url is not None:
            prompt["pr_url"] = pr_url
        if model is not None:
            prompt["model_used"] = model

        self._save_state(state)

        return {
            "status": "updated",
            "id": prompt_id,
            "done": prompt["done"],
            "merged": prompt["merged"]
        }

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a prompt by ID.

        Args:
            prompt_id: The prompt ID to retrieve.

        Returns:
            Prompt dict or None if not found.
        """
        state = self._load_state()
        for p in state["prompts"]:
            if p["id"] == prompt_id:
                return p
        return None

    def get_next_prompt(self, tool: str) -> Optional[Dict[str, Any]]:
        """
        Get the next available prompt for a tool.

        Args:
            tool: Tool identifier

        Returns:
            Prompt dict or None if no prompts available.
        """
        if tool not in self.VALID_TOOLS:
            raise ValueError(f"Invalid tool '{tool}'. Must be one of: {self.VALID_TOOLS}")

        state = self._load_state()
        for p in state["prompts"]:
            if p["tool"] == tool and not p["picked_up"] and not p["done"] and not p["merged"]:
                return p
        return None

    def list_prompts(
        self,
        tool: Optional[str] = None,
        phase: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List prompts with optional filters.

        Args:
            tool: Filter by tool
            phase: Filter by phase
            status: Filter by status (pending, in_progress, done, merged)

        Returns:
            List of matching prompts.
        """
        state = self._load_state()
        prompts = state["prompts"]

        if tool:
            prompts = [p for p in prompts if p["tool"] == tool]
        if phase:
            prompts = [p for p in prompts if p["phase"] == phase]
        if status:
            if status == "pending":
                prompts = [p for p in prompts if not p["picked_up"]]
            elif status == "in_progress":
                prompts = [p for p in prompts if p["picked_up"] and not p["done"]]
            elif status == "done":
                prompts = [p for p in prompts if p["done"] and not p["merged"]]
            elif status == "merged":
                prompts = [p for p in prompts if p["merged"]]

        return prompts

    def regenerate(self) -> None:
        """Regenerate the markdown tracker from JSON state."""
        if self.use_cli:
            self._run_cli(["regenerate"])
        else:
            # Import and call the generate_markdown function
            # We need to generate the markdown directly
            state = self._load_state()
            self._generate_markdown(state)

    def _generate_markdown(self, state: Dict[str, Any]) -> None:
        """Generate the markdown tracker from JSON state."""
        tracker_file = self.prompts_dir / "project_prompts_tracker.md"
        prompts = state["prompts"]
        tool_defs = state["tool_definitions"]
        phase_defs = state["phase_definitions"]

        # Calculate summary stats
        total = len(prompts)
        delivered = sum(1 for p in prompts if p["merged"])
        in_progress = sum(1 for p in prompts if p["picked_up"] and not p["done"])
        pending = sum(1 for p in prompts if not p["picked_up"])

        # Group by phase
        phases: Dict[str, List[Dict[str, Any]]] = {}
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

        with open(tracker_file, "w") as f:
            f.write("\n".join(lines))

    def validate_state(self, check_orphans: bool = False) -> Dict[str, Any]:
        """
        Validate that state matches actual prompt files.

        Args:
            check_orphans: Also check for orphan files not in state.

        Returns:
            Validation result dict.
        """
        if self.use_cli:
            cmd = ["validate-state"]
            if check_orphans:
                cmd.append("--check-orphans")
            return self._run_cli(cmd)

        # Direct mode
        state = self._load_state()
        prompts = state["prompts"]

        issues = []
        valid = []

        for p in prompts:
            file_path = self.prompts_dir / p["file"]
            if file_path.exists():
                valid.append(p["id"])
            else:
                issues.append({
                    "id": p["id"],
                    "file": p["file"],
                    "issue": "file_not_found"
                })

        # Check for orphan files
        if check_orphans:
            tracked_files = {p["file"] for p in prompts}
            for phase_dir in self.prompts_dir.iterdir():
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

        return result

    def batch_add(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple prompts at once.

        Args:
            prompts: List of prompt dicts with id, title, tool, file.

        Returns:
            Dict with added and skipped counts.
        """
        added = []
        skipped = []

        state = self._load_state()
        existing_ids = {p["id"] for p in state["prompts"]}

        for entry in prompts:
            prompt_id = entry.get("id")
            if not prompt_id:
                skipped.append({"entry": entry, "reason": "missing id"})
                continue

            if prompt_id in existing_ids:
                skipped.append({"id": prompt_id, "reason": "already exists"})
                continue

            parts = prompt_id.split(".")
            if len(parts) < 2:
                skipped.append({"id": prompt_id, "reason": "invalid id format"})
                continue

            try:
                self.add_prompt(
                    prompt_id=prompt_id,
                    title=entry.get("title", "Untitled"),
                    tool=entry.get("tool", "unknown"),
                    file_path=entry.get("file", "")
                )
                added.append(prompt_id)
                existing_ids.add(prompt_id)
            except Exception as e:
                skipped.append({"id": prompt_id, "reason": str(e)})

        return {
            "status": "batch_complete",
            "added": added,
            "added_count": len(added),
            "skipped": skipped,
            "skipped_count": len(skipped)
        }
