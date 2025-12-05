"""
Specification Parsers Package

Contains parsers for different specification file formats.
"""

from lattice_lock_agents.prompt_architect.subagents.parsers.spec_parser import (
    SpecParser,
    MarkdownSpecParser,
    YAMLSpecParser,
    JSONSpecParser,
    get_parser_for_file,
    detect_parser,
)

__all__ = [
    "SpecParser",
    "MarkdownSpecParser",
    "YAMLSpecParser",
    "JSONSpecParser",
    "get_parser_for_file",
    "detect_parser",
]
