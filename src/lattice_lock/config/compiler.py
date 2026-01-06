import datetime
import os
from typing import Any

from lattice_lock.config.frontmatter import FrontmatterParser
from lattice_lock.config.inheritance import InheritanceResolver
from lattice_lock.config.normalizer import JSONNormalizer


class YAMLCompiler:
    """Compiles YAML configurations with inheritance, mixins, and variable resolution."""

    def __init__(self, base_path: str = None):
        self.parser = FrontmatterParser()
        self.resolver = InheritanceResolver()
        self.normalizer = JSONNormalizer()
        self.base_path = base_path or os.getcwd()

    def compile(self, file_path: str) -> dict[str, Any]:
        """Compiles a single YAML file."""
        abs_path = self._resolve_path(file_path)

        frontmatter, content = self.parser.parse(abs_path)

        base_config = {}
        if 'extends' in frontmatter:
            parent_path = frontmatter['extends']
            base_config = self.compile(parent_path)
            if '_meta' in base_config:
                del base_config['_meta']

        if 'mixins' in frontmatter:
            for mixin_path in frontmatter['mixins']:
                mixin_config = self.compile(mixin_path)
                if '_meta' in mixin_config:
                    del mixin_config['_meta']
                base_config = self.resolver.deep_merge(base_config, mixin_config)

        final_config = self.resolver.deep_merge(base_config, content)

        if frontmatter.get('compile', {}).get('normalize'):
            final_config = self.normalizer.normalize(final_config)

        final_config['_meta'] = {
            'source': abs_path,
            'compiled_at': datetime.datetime.utcnow().isoformat(),
            'frontmatter': frontmatter,
            'version': frontmatter.get('vars', {}).get('version', 'unknown')
        }

        return final_config

    def _resolve_path(self, path: str) -> str:
        """Resolves config paths relative to base_path if not absolute."""
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)
