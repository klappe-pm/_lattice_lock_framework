import os
import datetime
from typing import Dict, Any, Optional

from lattice_lock.config.frontmatter import FrontmatterParser
from lattice_lock.config.inheritance import InheritanceResolver
from lattice_lock.config.normalizer import JSONNormalizer

class YAMLCompiler:
    """
    Compiles YAML configurations with inheritance, mixins, and variable resolution.
    Produces resolved and optionally normalized JSON-compatible dictionaries.
    """

    def __init__(self, base_path: str = None):
        self.parser = FrontmatterParser()
        self.resolver = InheritanceResolver()
        self.normalizer = JSONNormalizer()
        # Allows resolving relative paths from a base config directory
        self.base_path = base_path or os.getcwd()

    def compile(self, file_path: str) -> Dict[str, Any]:
        """
        Compiles a single YAML file.
        
        Args:
            file_path: Path to the YAML file.
            
        Returns:
            Compiled configuration dictionary.
        """
        abs_path = self._resolve_path(file_path)
        
        # 1. Parse frontmatter
        frontmatter, content = self.parser.parse(abs_path)
        
        # 2. Variable resolution is handled by parser for local vars. 
        
        # 3. Load Inheritance Chain (Extends)
        base_config = {}
        if 'extends' in frontmatter:
            parent_path = frontmatter['extends']
            # Recursively compile parent
            base_config = self.compile(parent_path)
            
            # Remove metadata from parent related to compilation state if needed
            if '_meta' in base_config:
                del base_config['_meta']

        # 4. Apply Mixins
        if 'mixins' in frontmatter:
            for mixin_path in frontmatter['mixins']:
                mixin_config = self.compile(mixin_path)
                if '_meta' in mixin_config:
                    del mixin_config['_meta']
                
                # Merge mixin into base
                base_config = self.resolver.deep_merge(base_config, mixin_config)

        # 5. Merge Current Content
        # Content overrides base (which includes parents and mixins)
        final_config = self.resolver.deep_merge(base_config, content)
        
        # 6. Normalize if requested
        if frontmatter.get('compile', {}).get('normalize'):
            final_config = self.normalizer.normalize(final_config)
            
        # 7. Add Metadata
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
