from typing import List, Dict, Set
import os
from .tool_profiles import ToolProfile, Task, ToolAssignment, load_tool_profiles

class ToolMatcher:
    def __init__(self, config_path: str):
        self.profiles = load_tool_profiles(config_path)
        self.file_ownership_map: Dict[str, str] = {} # file_path -> tool_id
        self._build_ownership_map()

    def _build_ownership_map(self):
        """Builds a map of file patterns to their owner tools."""
        for tool_id, profile in self.profiles.items():
            for pattern in profile.preferred_files:
                self.file_ownership_map[pattern] = tool_id

    def get_do_not_touch_list(self, tool_id: str) -> List[str]:
        """Generates a list of files that the given tool should NOT touch."""
        do_not_touch = []
        for owner_id, profile in self.profiles.items():
            if owner_id != tool_id:
                do_not_touch.extend(profile.preferred_files)
        return do_not_touch

    def _resolve_ownership(self, file_path: str) -> str:
        """Determines the owner of a file based on the ownership map."""
        # Check for exact match or directory match
        best_match_owner = None
        best_match_len = 0

        for pattern, owner_id in self.file_ownership_map.items():
            if pattern.endswith('/'):
                if file_path.startswith(pattern):
                    if len(pattern) > best_match_len:
                        best_match_len = len(pattern)
                        best_match_owner = owner_id
            elif file_path == pattern or file_path.endswith(pattern): # Simple suffix match for now
                 # Exact or suffix match takes precedence over directory
                 return owner_id

        return best_match_owner

    def match(self, tasks: List[Task]) -> List[ToolAssignment]:
        assignments = []

        for task in tasks:
            best_tool = None
            max_score = -1.0
            conflict_files = []

            # First pass: Check for hard ownership constraints
            forced_owner = None
            for file in task.files:
                owner = self._resolve_ownership(file)
                if owner:
                    if forced_owner and forced_owner != owner:
                        # Conflict: Task involves files owned by different tools
                        # Strategy: Split or assign to primary owner (simplification: assign to first owner found)
                        # In a real scenario, we might split the task.
                        # For now, we'll note the conflict but stick to the first owner.
                        pass
                    else:
                        forced_owner = owner

            if forced_owner:
                best_tool = forced_owner
                max_score = 1.0 # Forced assignment
                reason = f"Owned files detected for {forced_owner}"
            else:
                # Second pass: Capability matching if no hard ownership
                for tool_id, profile in self.profiles.items():
                    score = profile.calculate_affinity(task.description, task.files)
                    if score > max_score:
                        max_score = score
                        best_tool = tool_id
                reason = f"Best capability match ({max_score:.2f})"

            if best_tool:
                assignments.append(ToolAssignment(
                    task_id=task.id,
                    tool=best_tool,
                    confidence=max_score,
                    files_owned=[f for f in task.files if self._resolve_ownership(f) == best_tool],
                    reasoning=reason
                ))
            else:
                # Fallback or unassigned
                assignments.append(ToolAssignment(
                    task_id=task.id,
                    tool="unassigned",
                    confidence=0.0,
                    reasoning="No suitable tool found"
                ))

        return assignments
