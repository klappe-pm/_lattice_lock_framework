import copy
from typing import Any


class InheritanceResolver:
    """
    Handles configuration inheritance including mixins and deep merging.
    Uses C3 linearization (conceptually) for resolution order if needed,
    but primarily merges base -> mixins -> child.
    """

    def deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        Deep merges override into base, handling special directives.

        Directives for lists:
        - `key: +append`: Append items to the base list.
        - `key: +remove`: Remove items from the base list.
        - `key: +replace`: Replace the base list entirely (default behavior for lists).

        Args:
            base: The base configuration dictionary.
            override: The override configuration dictionary.

        Returns:
            The merged configuration dictionary.
        """
        merged = copy.deepcopy(base)

        for key, value in override.items():
            if isinstance(value, dict):
                # Check for directives within the value dict
                if "+append" in value or "+remove" in value or "+replace" in value:
                    self._handle_list_directives(merged, key, value)
                elif key in merged and isinstance(merged[key], dict):
                    # Recursive merge for dicts
                    merged[key] = self.deep_merge(merged[key], value)
                else:
                    # Key doesn't exist in base or base isn't a dict -> Overwrite
                    merged[key] = value
            else:
                # Scalar or List (replace strategy)
                merged[key] = value

        return merged

    def _handle_list_directives(self, merged: dict[str, Any], key: str, directives: dict[str, Any]):
        """Helper to process list modification directives."""
        # Ensure base is a list if it exists, else empty list
        current_list = merged.get(key, [])
        if not isinstance(current_list, list):
            current_list = []  # Reset if type mismatch or missing

        # +replace takes precedence
        if "+replace" in directives:
            merged[key] = directives["+replace"]
            return

        # +remove
        if "+remove" in directives:
            to_remove = directives["+remove"]
            # Simple removal based on equality.
            # For objects, this might require matching identity fields (like name).
            current_list = [
                item for item in current_list if not self._is_in_remove_list(item, to_remove)
            ]

        # +append
        if "+append" in directives:
            to_append = directives["+append"]
            if isinstance(to_append, list):
                current_list.extend(to_append)

        merged[key] = current_list

    def _is_in_remove_list(self, item: Any, remove_list: list[Any]) -> bool:
        """
        Checks if item should be removed. Supports by-value and by-name-field matching.
        """
        for r in remove_list:
            if item == r:
                return True
            # Special case for dicts with 'name' (common in this codebase)
            if isinstance(item, dict) and isinstance(r, dict):
                if "name" in item and "name" in r and item["name"] == r["name"]:
                    return True
        return False
