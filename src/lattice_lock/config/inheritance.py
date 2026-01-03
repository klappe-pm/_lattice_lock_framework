import copy
from typing import Any


class InheritanceResolver:
    """Handles configuration inheritance including mixins and deep merging."""

    def deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        Deep merges override into base, handling special directives.
        
        Directives: +append, +remove, +replace
        """
        merged = copy.deepcopy(base)

        for key, value in override.items():
            if isinstance(value, dict):
                if '+append' in value or '+remove' in value or '+replace' in value:
                    self._handle_list_directives(merged, key, value)
                elif key in merged and isinstance(merged[key], dict):
                    merged[key] = self.deep_merge(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value

        return merged

    def _handle_list_directives(self, merged: dict[str, Any], key: str, directives: dict[str, Any]):
        """Helper to process list modification directives."""
        current_list = merged.get(key, [])
        if not isinstance(current_list, list):
            current_list = []

        if '+replace' in directives:
            merged[key] = directives['+replace']
            return

        if '+remove' in directives:
            to_remove = directives['+remove']
            current_list = [item for item in current_list if not self._is_in_remove_list(item, to_remove)]

        if '+append' in directives:
            to_append = directives['+append']
            if isinstance(to_append, list):
                current_list.extend(to_append)

        merged[key] = current_list

    def _is_in_remove_list(self, item: Any, remove_list: list[Any]) -> bool:
        """Checks if item should be removed."""
        for r in remove_list:
            if item == r:
                return True
            if isinstance(item, dict) and isinstance(r, dict):
                if 'name' in item and 'name' in r and item['name'] == r['name']:
                    return True
        return False
