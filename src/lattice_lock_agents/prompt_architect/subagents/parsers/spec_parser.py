"""
Specification parsers for different file formats.

Supports markdown, YAML, and JSON specification formats.
"""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

import yaml

from ..models import (
    Component,
    ComponentLayer,
    Constraint,
    ConstraintType,
    Phase,
    Requirement,
    RequirementType,
    SpecificationAnalysis,
    SpecificationMetadata,
)


class SpecParser(ABC):
    """Abstract base class for specification parsers."""

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content.

        Args:
            content: The content to check.

        Returns:
            True if this parser can handle the content.
        """
        pass

    @abstractmethod
    def parse(
        self,
        content: str,
        source_file: Optional[str] = None,
    ) -> SpecificationAnalysis:
        """Parse the content and return a SpecificationAnalysis.

        Args:
            content: The content to parse.
            source_file: Optional source file path for metadata.

        Returns:
            SpecificationAnalysis with extracted data.
        """
        pass


class JSONSpecParser(SpecParser):
    """Parser for JSON specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content is valid JSON."""
        content_stripped = content.strip()
        if not (content_stripped.startswith('{') or content_stripped.startswith('[')):
            return False
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

    def parse(
        self,
        content: str,
        source_file: Optional[str] = None,
    ) -> SpecificationAnalysis:
        """Parse JSON specification content."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return SpecificationAnalysis(
                metadata=SpecificationMetadata(
                    source_file=source_file,
                    file_format="json",
                ),
            )

        # Extract metadata
        metadata = SpecificationMetadata(
            title=data.get("title"),
            version=data.get("version"),
            author=data.get("author"),
            source_file=source_file,
            file_format="json",
        )

        # Extract phases
        phases = []
        for phase_data in data.get("phases", []):
            if isinstance(phase_data, str):
                phases.append(Phase(name=phase_data))
            elif isinstance(phase_data, dict):
                phases.append(Phase(**phase_data))

        # Extract components
        components = []
        for comp_data in data.get("components", []):
            if isinstance(comp_data, str):
                components.append(Component(name=comp_data))
            elif isinstance(comp_data, dict):
                if "layer" in comp_data and isinstance(comp_data["layer"], str):
                    try:
                        comp_data["layer"] = ComponentLayer(comp_data["layer"])
                    except ValueError:
                        comp_data["layer"] = ComponentLayer.APPLICATION
                components.append(Component(**comp_data))

        # Extract requirements
        requirements = []
        for req_data in data.get("requirements", []):
            if isinstance(req_data, str):
                requirements.append(
                    Requirement(
                        id=f"REQ-{len(requirements) + 1:03d}",
                        description=req_data,
                    )
                )
            elif isinstance(req_data, dict):
                if "type" in req_data and isinstance(req_data["type"], str):
                    try:
                        req_data["requirement_type"] = RequirementType(req_data.pop("type"))
                    except ValueError:
                        pass
                requirements.append(Requirement(**req_data))

        # Extract constraints
        constraints = []
        for con_data in data.get("constraints", []):
            if isinstance(con_data, str):
                constraints.append(
                    Constraint(
                        id=f"CON-{len(constraints) + 1:03d}",
                        description=con_data,
                    )
                )
            elif isinstance(con_data, dict):
                if "type" in con_data and isinstance(con_data["type"], str):
                    try:
                        con_data["constraint_type"] = ConstraintType(con_data.pop("type"))
                    except ValueError:
                        pass
                constraints.append(Constraint(**con_data))

        return SpecificationAnalysis(
            metadata=metadata,
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
        )


class YAMLSpecParser(SpecParser):
    """Parser for YAML specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content is valid YAML."""
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False

    def parse(
        self,
        content: str,
        source_file: Optional[str] = None,
    ) -> SpecificationAnalysis:
        """Parse YAML specification content."""
        try:
            data = yaml.safe_load(content) or {}
        except yaml.YAMLError:
            return SpecificationAnalysis(
                metadata=SpecificationMetadata(
                    source_file=source_file,
                    file_format="yaml",
                ),
            )

        # Extract metadata
        metadata = SpecificationMetadata(
            title=data.get("title"),
            version=data.get("version"),
            author=data.get("author"),
            source_file=source_file,
            file_format="yaml",
        )

        # Extract phases
        phases = []
        for phase_data in data.get("phases", []):
            if isinstance(phase_data, str):
                phases.append(Phase(name=phase_data))
            elif isinstance(phase_data, dict):
                phases.append(Phase(**phase_data))

        # Extract components
        components = []
        for comp_data in data.get("components", []):
            if isinstance(comp_data, str):
                components.append(Component(name=comp_data))
            elif isinstance(comp_data, dict):
                if "layer" in comp_data and isinstance(comp_data["layer"], str):
                    try:
                        comp_data["layer"] = ComponentLayer(comp_data["layer"])
                    except ValueError:
                        comp_data["layer"] = ComponentLayer.APPLICATION
                components.append(Component(**comp_data))

        # Extract requirements
        requirements = []
        for req_data in data.get("requirements", []):
            if isinstance(req_data, str):
                requirements.append(
                    Requirement(
                        id=f"REQ-{len(requirements) + 1:03d}",
                        description=req_data,
                    )
                )
            elif isinstance(req_data, dict):
                if "type" in req_data and isinstance(req_data["type"], str):
                    try:
                        req_data["requirement_type"] = RequirementType(req_data.pop("type"))
                    except ValueError:
                        pass
                requirements.append(Requirement(**req_data))

        # Extract constraints
        constraints = []
        for con_data in data.get("constraints", []):
            if isinstance(con_data, str):
                constraints.append(
                    Constraint(
                        id=f"CON-{len(constraints) + 1:03d}",
                        description=con_data,
                    )
                )
            elif isinstance(con_data, dict):
                if "type" in con_data and isinstance(con_data["type"], str):
                    try:
                        con_data["constraint_type"] = ConstraintType(con_data.pop("type"))
                    except ValueError:
                        pass
                constraints.append(Constraint(**con_data))

        return SpecificationAnalysis(
            metadata=metadata,
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
        )


class MarkdownSpecParser(SpecParser):
    """Parser for Markdown specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content appears to be markdown."""
        # Check for markdown indicators
        has_header = bool(re.search(r'^#+ ', content, re.MULTILINE))
        has_list = bool(re.search(r'^[\-\*] ', content, re.MULTILINE))
        # Not JSON
        not_json = not content.strip().startswith('{') and not content.strip().startswith('[')
        return (has_header or has_list) and not_json

    def parse(
        self,
        content: str,
        source_file: Optional[str] = None,
    ) -> SpecificationAnalysis:
        """Parse Markdown specification content."""
        metadata = SpecificationMetadata(
            source_file=source_file,
            file_format="markdown",
        )

        # Extract title from first H1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata.title = title_match.group(1).strip()

        # Extract version
        version_match = re.search(r'\*\*Version[:\s]*\*\*\s*(\S+)', content, re.IGNORECASE)
        if version_match:
            metadata.version = version_match.group(1).strip()

        # Extract author
        author_match = re.search(r'\*\*Author[:\s]*\*\*\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if author_match:
            metadata.author = author_match.group(1).strip()

        # Extract phases
        phases = []
        phase_pattern = re.compile(
            r'^##\s+(?:Phase\s+\d+[:\s]*)?(.+)$',
            re.MULTILINE | re.IGNORECASE,
        )
        for match in phase_pattern.finditer(content):
            phase_name = match.group(1).strip()
            # Filter out non-phase sections
            if phase_name.lower() not in ['requirements', 'constraints', 'components', 'overview']:
                phases.append(Phase(name=phase_name))

        # Extract components from bullet lists under "Components" section
        components = []
        comp_section = re.search(
            r'^##\s+Components?\s*\n((?:[\-\*]\s+.+\n?)+)',
            content,
            re.MULTILINE | re.IGNORECASE,
        )
        if comp_section:
            for line in comp_section.group(1).split('\n'):
                comp_match = re.match(r'^[\-\*]\s+(.+)$', line.strip())
                if comp_match:
                    comp_name = comp_match.group(1).strip()
                    # Remove markdown formatting
                    comp_name = re.sub(r'[\*_`]', '', comp_name)
                    components.append(Component(name=comp_name))

        # Extract requirements from bullet lists
        requirements = []
        req_idx = 1

        # Look for Requirements section
        req_section = re.search(
            r'^##\s+Requirements?\s*\n((?:[\-\*]\s+.+\n?)+)',
            content,
            re.MULTILINE | re.IGNORECASE,
        )
        if req_section:
            for line in req_section.group(1).split('\n'):
                req_match = re.match(r'^[\-\*]\s+(.+)$', line.strip())
                if req_match:
                    requirements.append(
                        Requirement(
                            id=f"REQ-{req_idx:03d}",
                            description=req_match.group(1).strip(),
                        )
                    )
                    req_idx += 1

        # Also extract "must" and "should" statements
        must_should_pattern = re.compile(
            r'^[\-\*]\s+(.+?(?:must|should).+?)$',
            re.MULTILINE | re.IGNORECASE,
        )
        existing_descs = {r.description.lower() for r in requirements}
        for match in must_should_pattern.finditer(content):
            desc = match.group(1).strip()
            if desc.lower() not in existing_descs:
                requirements.append(
                    Requirement(
                        id=f"REQ-{req_idx:03d}",
                        description=desc,
                    )
                )
                req_idx += 1
                existing_descs.add(desc.lower())

        # Extract constraints
        constraints = []
        con_idx = 1

        # Look for Constraints section
        con_section = re.search(
            r'^##\s+(?:Technical\s+)?Constraints?\s*\n((?:[\-\*]\s+.+\n?)+)',
            content,
            re.MULTILINE | re.IGNORECASE,
        )
        if con_section:
            for line in con_section.group(1).split('\n'):
                con_match = re.match(r'^[\-\*]\s+(.+)$', line.strip())
                if con_match:
                    constraints.append(
                        Constraint(
                            id=f"CON-{con_idx:03d}",
                            description=con_match.group(1).strip(),
                        )
                    )
                    con_idx += 1

        return SpecificationAnalysis(
            metadata=metadata,
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
        )


def get_parser_for_file(file_path: str) -> SpecParser:
    """Get the appropriate parser for a file based on its extension.

    Args:
        file_path: Path to the specification file.

    Returns:
        An appropriate SpecParser instance for the file type.

    Raises:
        ValueError: If the file format is not supported.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    parsers = {
        '.md': MarkdownSpecParser(),
        '.markdown': MarkdownSpecParser(),
        '.yaml': YAMLSpecParser(),
        '.yml': YAMLSpecParser(),
        '.json': JSONSpecParser(),
    }

    parser = parsers.get(suffix)
    if parser is None:
        raise ValueError(f"Unsupported file extension: {suffix}")

    return parser


def detect_parser(content: str) -> SpecParser:
    """Detect the appropriate parser based on content.

    Args:
        content: The specification content to analyze.

    Returns:
        An appropriate SpecParser instance.
    """
    content_stripped = content.strip()

    # Try JSON first (most specific)
    if content_stripped.startswith('{') or content_stripped.startswith('['):
        try:
            json.loads(content)
            return JSONSpecParser()
        except json.JSONDecodeError:
            pass

    # Try YAML (if it has YAML-specific patterns)
    if ':' in content_stripped.split('\n')[0]:
        try:
            yaml.safe_load(content)
            return YAMLSpecParser()
        except yaml.YAMLError:
            pass

    # Default to Markdown
    return MarkdownSpecParser()


__all__ = [
    "SpecParser",
    "JSONSpecParser",
    "YAMLSpecParser",
    "MarkdownSpecParser",
    "get_parser_for_file",
    "detect_parser",
]
