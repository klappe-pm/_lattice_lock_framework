"""
Lattice Lock Compiler - Format Detection and Utilities

This module provides format detection, validation, and utility functions
for working with YAML, TOON, and JSON configuration formats.
"""

from enum import Enum
from pathlib import Path
from typing import Any


class FormatType(str, Enum):
    """Supported configuration formats."""
    
    YAML = "yaml"
    JSON = "json"
    TOON = "toon"
    UNKNOWN = "unknown"


# File extension mappings
EXTENSION_MAP: dict[str, FormatType] = {
    ".yaml": FormatType.YAML,
    ".yml": FormatType.YAML,
    ".json": FormatType.JSON,
    ".toon": FormatType.TOON,
}


def detect_format(source: str | Path, content: str | None = None) -> FormatType:
    """
    Detect the format of a configuration source.
    
    Detection priority:
    1. File extension (if path provided)
    2. Content heuristics
    3. Default to YAML
    
    Args:
        source: File path or content string
        content: Optional content (if source is a path)
        
    Returns:
        Detected FormatType
    """
    # Try extension-based detection first
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        path = Path(source)
        fmt = EXTENSION_MAP.get(path.suffix.lower())
        if fmt:
            return fmt
        
        # Load content if not provided
        if content is None:
            content = path.read_text()
    else:
        content = source
    
    return detect_format_from_content(content)


def detect_format_from_content(content: str) -> FormatType:
    """
    Detect format from content using heuristics.
    
    Heuristics:
    - JSON: Starts with { or [, valid JSON parse
    - TOON: Contains tabular headers like [N]{field,...}:
    - YAML: Default fallback
    
    Args:
        content: Configuration content string
        
    Returns:
        Detected FormatType
    """
    import json as json_module
    
    content = content.strip()
    
    # Empty content
    if not content:
        return FormatType.YAML
    
    # JSON detection
    if content.startswith("{") or content.startswith("["):
        try:
            json_module.loads(content)
            return FormatType.JSON
        except json_module.JSONDecodeError:
            pass
    
    # TOON detection (tabular headers)
    # Pattern: key[N]{field1,field2,...}:
    if _looks_like_toon(content):
        return FormatType.TOON
    
    # Default to YAML
    return FormatType.YAML


def _looks_like_toon(content: str) -> bool:
    """
    Check if content looks like TOON format.
    
    TOON characteristics:
    - Tabular headers: [N]{field1,field2}:
    - Inline arrays: [N]: value1,value2
    - Colon-based key-value pairs
    """
    import re
    
    # Look for tabular array pattern: key[N]{fields}:
    tabular_pattern = r'\w+\[\d+\]\{[\w,]+\}:'
    if re.search(tabular_pattern, content):
        return True
    
    # Look for inline array pattern: key[N]:
    inline_pattern = r'\w+\[\d+\]:'
    if re.search(inline_pattern, content):
        return True
    
    return False


def get_format_extension(fmt: FormatType) -> str:
    """
    Get the canonical file extension for a format.
    
    Args:
        fmt: Format type
        
    Returns:
        File extension (with dot)
    """
    extension_map = {
        FormatType.YAML: ".yaml",
        FormatType.JSON: ".json",
        FormatType.TOON: ".toon",
    }
    return extension_map.get(fmt, ".yaml")


def get_format_mime_type(fmt: FormatType) -> str:
    """
    Get the MIME type for a format.
    
    Args:
        fmt: Format type
        
    Returns:
        MIME type string
    """
    mime_map = {
        FormatType.YAML: "application/x-yaml",
        FormatType.JSON: "application/json",
        FormatType.TOON: "text/toon",  # Provisional
    }
    return mime_map.get(fmt, "text/plain")


def validate_format_content(content: str, expected_format: FormatType) -> tuple[bool, str | None]:
    """
    Validate that content matches expected format.
    
    Args:
        content: Content string to validate
        expected_format: Expected format type
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import json as json_module
    import yaml
    
    try:
        if expected_format == FormatType.JSON:
            json_module.loads(content)
            return True, None
            
        elif expected_format == FormatType.YAML:
            yaml.safe_load(content)
            return True, None
            
        elif expected_format == FormatType.TOON:
            # Try to import toon_format
            try:
                import toon_format
                toon_format.decode(content)
                return True, None
            except ImportError:
                return False, "TOON format library not installed"
            except Exception as e:
                return False, f"TOON parse error: {str(e)}"
                
    except json_module.JSONDecodeError as e:
        return False, f"JSON parse error: {str(e)}"
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {str(e)}"
    except Exception as e:
        return False, f"Parse error: {str(e)}"
    
    return False, f"Unknown format: {expected_format}"


class FormatRegistry:
    """
    Registry for format handlers.
    
    Allows registration of custom parsers and serializers for extensibility.
    """
    
    def __init__(self):
        self._parsers: dict[FormatType, callable] = {}
        self._serializers: dict[FormatType, callable] = {}
        self._validators: dict[FormatType, callable] = {}
        
        # Register defaults
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default format handlers."""
        import json as json_module
        import yaml
        
        # YAML
        self._parsers[FormatType.YAML] = yaml.safe_load
        self._serializers[FormatType.YAML] = lambda d: yaml.dump(d, default_flow_style=False)
        
        # JSON
        self._parsers[FormatType.JSON] = json_module.loads
        self._serializers[FormatType.JSON] = lambda d: json_module.dumps(d, indent=2)
    
    def register_parser(self, fmt: FormatType, parser: callable):
        """Register a custom parser for a format."""
        self._parsers[fmt] = parser
    
    def register_serializer(self, fmt: FormatType, serializer: callable):
        """Register a custom serializer for a format."""
        self._serializers[fmt] = serializer
    
    def register_validator(self, fmt: FormatType, validator: callable):
        """Register a custom validator for a format."""
        self._validators[fmt] = validator
    
    def parse(self, content: str, fmt: FormatType) -> Any:
        """Parse content using registered parser."""
        parser = self._parsers.get(fmt)
        if not parser:
            raise ValueError(f"No parser registered for format: {fmt}")
        return parser(content)
    
    def serialize(self, data: Any, fmt: FormatType) -> str:
        """Serialize data using registered serializer."""
        serializer = self._serializers.get(fmt)
        if not serializer:
            raise ValueError(f"No serializer registered for format: {fmt}")
        return serializer(data)
    
    def validate(self, content: str, fmt: FormatType) -> tuple[bool, str | None]:
        """Validate content using registered validator."""
        validator = self._validators.get(fmt)
        if validator:
            return validator(content)
        return validate_format_content(content, fmt)


# Global format registry instance
format_registry = FormatRegistry()
