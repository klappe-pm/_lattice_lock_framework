import re
import yaml
from typing import Dict, Any, Tuple
import os


class FrontmatterParser:
    """Parses YAML frontmatter and handles variable interpolation."""

    _FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
    _VAR_PATTERN = re.compile(r"\$\{vars\.([a-zA-Z0-9_]+)(?::-([^}]+))?\}")

    def parse(self, file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parses a YAML file with potential frontmatter.

        Returns:
            A tuple containing (frontmatter_dict, content_dict).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        frontmatter: Dict[str, Any] = {}
        content_str: str = raw_content

        match = self._FRONTMATTER_PATTERN.match(raw_content)
        if match:
            frontmatter_str = match.group(1)
            content_str = match.group(2)
            
            try:
                frontmatter = yaml.safe_load(frontmatter_str) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in frontmatter of {file_path}: {e}")

        variables = frontmatter.get('vars', {})
        resolved_content_str = self._resolve_variables(content_str, variables)

        try:
            content = yaml.safe_load(resolved_content_str) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in content of {file_path}: {e}")

        return frontmatter, content

    def _resolve_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """Substitutes variables in the content string."""
        def replace(match):
            var_name = match.group(1)
            default_val = match.group(2)
            
            if var_name in variables:
                return str(variables[var_name])
            elif default_val is not None:
                return default_val
            else:
                return match.group(0)

        return self._VAR_PATTERN.sub(replace, content)
