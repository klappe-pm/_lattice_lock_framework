"""
Specification Parsers Package

Contains parsers for different specification file formats.
"""

from lattice_lock.agents.prompt_architect.subagents.parsers.spec_parser import (
    JSONSpecParser,
    MarkdownSpecParser,
    SpecParser,
    YAMLSpecParser,
    detect_parser,
    get_parser_for_file,
)

__all__ = [
    "SpecParser",
    "MarkdownSpecParser",
    "YAMLSpecParser",
    "JSONSpecParser",
    "get_parser_for_file",
    "detect_parser",
]
