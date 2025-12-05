"""
Specification Parsers for different file formats.

Provides parsers for Markdown, YAML, and JSON specification files.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

import yaml

from lattice_lock_agents.prompt_architect.subagents.models import (
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

logger = logging.getLogger(__name__)


class SpecParser(ABC):
    """Abstract base class for specification parsers."""

    @abstractmethod
    def parse(self, content: str, source_path: Optional[str] = None) -> SpecificationAnalysis:
        """Parse specification content into a SpecificationAnalysis object.

        Args:
            content: The raw content of the specification file.
            source_path: Optional path to the source file for metadata.

        Returns:
            A SpecificationAnalysis object containing the parsed data.
        """
        pass

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content.

        Args:
            content: The raw content to check.

        Returns:
            True if this parser can handle the content, False otherwise.
        """
        pass

    def _extract_metadata(
        self, data: dict[str, Any], source_path: Optional[str] = None
    ) -> SpecificationMetadata:
        """Extract metadata from parsed data."""
        return SpecificationMetadata(
            title=data.get("title"),
            version=data.get("version"),
            author=data.get("author"),
            source_file=source_path,
        )


class MarkdownSpecParser(SpecParser):
    """Parser for Markdown specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content appears to be Markdown."""
        return content.strip().startswith("#") or "##" in content

    def parse(self, content: str, source_path: Optional[str] = None) -> SpecificationAnalysis:
        """Parse Markdown specification content."""
        sections = self._extract_sections(content)
        metadata = self._parse_metadata(content, source_path)

        phases = self._extract_phases(sections)
        components = self._extract_components(sections)
        requirements = self._extract_requirements(sections)
        constraints = self._extract_constraints(sections)

        return SpecificationAnalysis(
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
            metadata=metadata,
            raw_sections=sections,
        )

    def _extract_sections(self, content: str) -> dict[str, Any]:
        """Extract sections from Markdown content."""
        sections: dict[str, Any] = {}
        current_section = ""
        current_content: list[str] = []
        current_level = 0

        lines = content.split("\n")
        for line in lines:
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                if current_section:
                    sections[current_section] = {
                        "content": "\n".join(current_content),
                        "level": current_level,
                    }
                current_level = len(header_match.group(1))
                current_section = header_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = {
                "content": "\n".join(current_content),
                "level": current_level,
            }

        return sections

    def _parse_metadata(
        self, content: str, source_path: Optional[str] = None
    ) -> SpecificationMetadata:
        """Parse metadata from Markdown content."""
        title = None
        version = None
        author = None

        lines = content.split("\n")
        for line in lines:
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif "**Version:**" in line or "Version:" in line:
                version_match = re.search(r"Version:\*?\*?\s*(.+?)(?:\s*$|\s*\*\*)", line)
                if version_match:
                    version = version_match.group(1).strip()
            elif "**Author:**" in line or "Author:" in line:
                author_match = re.search(r"Author:\*?\*?\s*(.+?)(?:\s*$|\s*\*\*)", line)
                if author_match:
                    author = author_match.group(1).strip()

        return SpecificationMetadata(
            title=title,
            version=version,
            author=author,
            source_file=source_path,
            file_format="markdown",
        )

    def _extract_phases(self, sections: dict[str, Any]) -> list[Phase]:
        """Extract phases from sections."""
        phases: list[Phase] = []
        phase_counter = 0

        for section_name, section_data in sections.items():
            section_lower = section_name.lower()
            if "phase" in section_lower:
                phase_counter += 1
                phase_match = re.match(
                    r"(?:phase\s*)?(\d+)?[:\s]*(.+)?", section_name, re.IGNORECASE
                )
                name = section_name
                if phase_match and phase_match.group(2):
                    name = phase_match.group(2).strip()

                content = section_data.get("content", "")
                components = self._extract_list_items(content, "component")
                deliverables = self._extract_list_items(content, "deliverable")
                dependencies = self._extract_list_items(content, "depend")

                phases.append(
                    Phase(
                        name=name,
                        description=self._get_first_paragraph(content),
                        components=components,
                        deliverables=deliverables,
                        dependencies=dependencies,
                    )
                )

        if not phases:
            for section_name, section_data in sections.items():
                if "roadmap" in section_name.lower() or "timeline" in section_name.lower():
                    content = section_data.get("content", "")
                    phase_items = self._extract_list_items(content)
                    for i, item in enumerate(phase_items, 1):
                        phases.append(
                            Phase(
                                name=item,
                                description=f"Phase {i}: {item}",
                            )
                        )

        return phases

    def _extract_components(self, sections: dict[str, Any]) -> list[Component]:
        """Extract components from sections."""
        components: list[Component] = []

        for section_name, section_data in sections.items():
            section_lower = section_name.lower()
            if "component" in section_lower or "architecture" in section_lower:
                content = section_data.get("content", "")
                items = self._extract_list_items(content)
                for item in items:
                    layer = self._infer_component_layer(item)
                    components.append(
                        Component(
                            name=item,
                            layer=layer,
                        )
                    )

            if "layer" in section_lower:
                content = section_data.get("content", "")
                layer = self._infer_component_layer(section_name)
                items = self._extract_list_items(content)
                for item in items:
                    components.append(
                        Component(
                            name=item,
                            layer=layer,
                            description=f"Part of {section_name}",
                        )
                    )

        return components

    def _extract_requirements(self, sections: dict[str, Any]) -> list[Requirement]:
        """Extract requirements from sections."""
        requirements: list[Requirement] = []
        req_counter = 0

        for section_name, section_data in sections.items():
            section_lower = section_name.lower()
            content = section_data.get("content", "")

            if "requirement" in section_lower:
                req_type = RequirementType.FUNCTIONAL
                if "non-functional" in section_lower or "nonfunctional" in section_lower:
                    req_type = RequirementType.NON_FUNCTIONAL
                elif "performance" in section_lower:
                    req_type = RequirementType.PERFORMANCE
                elif "security" in section_lower:
                    req_type = RequirementType.SECURITY

                items = self._extract_list_items(content)
                for item in items:
                    req_counter += 1
                    requirements.append(
                        Requirement(
                            id=f"REQ-{req_counter:03d}",
                            description=item,
                            requirement_type=req_type,
                            source_section=section_name,
                        )
                    )

            elif "specification" in section_lower or "feature" in section_lower:
                items = self._extract_list_items(content)
                for item in items:
                    req_counter += 1
                    requirements.append(
                        Requirement(
                            id=f"REQ-{req_counter:03d}",
                            description=item,
                            requirement_type=RequirementType.FUNCTIONAL,
                            source_section=section_name,
                        )
                    )

        return requirements

    def _extract_constraints(self, sections: dict[str, Any]) -> list[Constraint]:
        """Extract constraints from sections."""
        constraints: list[Constraint] = []
        constraint_counter = 0

        for section_name, section_data in sections.items():
            section_lower = section_name.lower()
            content = section_data.get("content", "")

            if "constraint" in section_lower or "limitation" in section_lower:
                constraint_type = ConstraintType.TECHNICAL
                if "business" in section_lower:
                    constraint_type = ConstraintType.BUSINESS
                elif "regulatory" in section_lower or "compliance" in section_lower:
                    constraint_type = ConstraintType.REGULATORY
                elif "resource" in section_lower:
                    constraint_type = ConstraintType.RESOURCE
                elif "time" in section_lower or "schedule" in section_lower:
                    constraint_type = ConstraintType.TIME

                items = self._extract_list_items(content)
                for item in items:
                    constraint_counter += 1
                    constraints.append(
                        Constraint(
                            id=f"CON-{constraint_counter:03d}",
                            description=item,
                            constraint_type=constraint_type,
                            source_section=section_name,
                        )
                    )

            elif "guardrail" in section_lower or "rule" in section_lower:
                items = self._extract_list_items(content)
                for item in items:
                    constraint_counter += 1
                    constraints.append(
                        Constraint(
                            id=f"CON-{constraint_counter:03d}",
                            description=item,
                            constraint_type=ConstraintType.TECHNICAL,
                            source_section=section_name,
                        )
                    )

        return constraints

    def _extract_list_items(
        self, content: str, filter_keyword: Optional[str] = None
    ) -> list[str]:
        """Extract list items from content."""
        items: list[str] = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                item = line[2:].strip()
                if filter_keyword:
                    if filter_keyword.lower() in item.lower():
                        items.append(item)
                else:
                    if item:
                        items.append(item)
            elif re.match(r"^\d+\.\s+", line):
                item = re.sub(r"^\d+\.\s+", "", line).strip()
                if filter_keyword:
                    if filter_keyword.lower() in item.lower():
                        items.append(item)
                else:
                    if item:
                        items.append(item)

        return items

    def _get_first_paragraph(self, content: str) -> Optional[str]:
        """Get the first non-empty paragraph from content."""
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith("-") and not para.startswith("*"):
                if not para.startswith("|"):
                    return para
        return None

    def _infer_component_layer(self, text: str) -> ComponentLayer:
        """Infer the component layer from text."""
        text_lower = text.lower()
        if "presentation" in text_lower or "ui" in text_lower or "frontend" in text_lower:
            return ComponentLayer.PRESENTATION
        elif "domain" in text_lower or "business" in text_lower:
            return ComponentLayer.DOMAIN
        elif "infrastructure" in text_lower or "infra" in text_lower:
            return ComponentLayer.INFRASTRUCTURE
        elif "data" in text_lower or "database" in text_lower or "storage" in text_lower:
            return ComponentLayer.DATA
        elif "integration" in text_lower or "api" in text_lower or "gateway" in text_lower:
            return ComponentLayer.INTEGRATION
        return ComponentLayer.APPLICATION


class YAMLSpecParser(SpecParser):
    """Parser for YAML specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content appears to be YAML."""
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False

    def parse(self, content: str, source_path: Optional[str] = None) -> SpecificationAnalysis:
        """Parse YAML specification content."""
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                data = {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML: {e}")
            data = {}

        metadata = self._parse_metadata(data, source_path)
        phases = self._extract_phases(data)
        components = self._extract_components(data)
        requirements = self._extract_requirements(data)
        constraints = self._extract_constraints(data)

        return SpecificationAnalysis(
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
            metadata=metadata,
            raw_sections=data,
        )

    def _parse_metadata(
        self, data: dict[str, Any], source_path: Optional[str] = None
    ) -> SpecificationMetadata:
        """Parse metadata from YAML data."""
        return SpecificationMetadata(
            title=data.get("title") or data.get("name"),
            version=data.get("version"),
            author=data.get("author"),
            source_file=source_path,
            file_format="yaml",
        )

    def _extract_phases(self, data: dict[str, Any]) -> list[Phase]:
        """Extract phases from YAML data."""
        phases: list[Phase] = []
        phases_data = data.get("phases", [])

        if isinstance(phases_data, list):
            for i, phase_data in enumerate(phases_data):
                if isinstance(phase_data, dict):
                    phases.append(
                        Phase(
                            name=phase_data.get("name", f"Phase {i + 1}"),
                            description=phase_data.get("description"),
                            scope=phase_data.get("scope"),
                            components=phase_data.get("components", []),
                            dependencies=phase_data.get("dependencies", []),
                            deliverables=phase_data.get("deliverables", []),
                        )
                    )
                elif isinstance(phase_data, str):
                    phases.append(Phase(name=phase_data))

        return phases

    def _extract_components(self, data: dict[str, Any]) -> list[Component]:
        """Extract components from YAML data."""
        components: list[Component] = []
        components_data = data.get("components", [])

        if isinstance(components_data, list):
            for comp_data in components_data:
                if isinstance(comp_data, dict):
                    layer_str = comp_data.get("layer", "application")
                    try:
                        layer = ComponentLayer(layer_str.lower())
                    except ValueError:
                        layer = ComponentLayer.APPLICATION

                    components.append(
                        Component(
                            name=comp_data.get("name", "Unknown"),
                            description=comp_data.get("description"),
                            layer=layer,
                            interfaces=comp_data.get("interfaces", []),
                            files=comp_data.get("files", []),
                            dependencies=comp_data.get("dependencies", []),
                            responsibilities=comp_data.get("responsibilities", []),
                        )
                    )
                elif isinstance(comp_data, str):
                    components.append(Component(name=comp_data))

        return components

    def _extract_requirements(self, data: dict[str, Any]) -> list[Requirement]:
        """Extract requirements from YAML data."""
        requirements: list[Requirement] = []
        req_data = data.get("requirements", [])

        if isinstance(req_data, list):
            for i, req in enumerate(req_data):
                if isinstance(req, dict):
                    req_type_str = req.get("type", "functional")
                    try:
                        req_type = RequirementType(req_type_str.lower())
                    except ValueError:
                        req_type = RequirementType.FUNCTIONAL

                    requirements.append(
                        Requirement(
                            id=req.get("id", f"REQ-{i + 1:03d}"),
                            description=req.get("description", ""),
                            priority=req.get("priority", "medium"),
                            phase=req.get("phase"),
                            requirement_type=req_type,
                            acceptance_criteria=req.get("acceptance_criteria", []),
                            dependencies=req.get("dependencies", []),
                        )
                    )
                elif isinstance(req, str):
                    requirements.append(
                        Requirement(
                            id=f"REQ-{i + 1:03d}",
                            description=req,
                        )
                    )

        return requirements

    def _extract_constraints(self, data: dict[str, Any]) -> list[Constraint]:
        """Extract constraints from YAML data."""
        constraints: list[Constraint] = []
        constraints_data = data.get("constraints", [])

        if isinstance(constraints_data, list):
            for i, con in enumerate(constraints_data):
                if isinstance(con, dict):
                    con_type_str = con.get("type", "technical")
                    try:
                        con_type = ConstraintType(con_type_str.lower())
                    except ValueError:
                        con_type = ConstraintType.TECHNICAL

                    constraints.append(
                        Constraint(
                            id=con.get("id", f"CON-{i + 1:03d}"),
                            description=con.get("description", ""),
                            constraint_type=con_type,
                            impact=con.get("impact"),
                            mitigation=con.get("mitigation"),
                        )
                    )
                elif isinstance(con, str):
                    constraints.append(
                        Constraint(
                            id=f"CON-{i + 1:03d}",
                            description=con,
                        )
                    )

        return constraints


class JSONSpecParser(SpecParser):
    """Parser for JSON specification files."""

    def can_parse(self, content: str) -> bool:
        """Check if content appears to be JSON."""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

    def parse(self, content: str, source_path: Optional[str] = None) -> SpecificationAnalysis:
        """Parse JSON specification content."""
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                data = {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            data = {}

        yaml_parser = YAMLSpecParser()
        result = yaml_parser.parse(yaml.dump(data), source_path)
        result.metadata.file_format = "json"
        return result


def get_parser_for_file(file_path: str) -> SpecParser:
    """Get the appropriate parser for a file based on its extension.

    Args:
        file_path: Path to the specification file.

    Returns:
        An appropriate SpecParser instance.

    Raises:
        ValueError: If the file extension is not supported.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in (".md", ".markdown"):
        return MarkdownSpecParser()
    elif extension in (".yaml", ".yml"):
        return YAMLSpecParser()
    elif extension == ".json":
        return JSONSpecParser()
    else:
        raise ValueError(f"Unsupported file extension: {extension}")


def detect_parser(content: str) -> SpecParser:
    """Detect the appropriate parser based on content.

    Args:
        content: The raw content to parse.

    Returns:
        An appropriate SpecParser instance.
    """
    json_parser = JSONSpecParser()
    if json_parser.can_parse(content):
        return json_parser

    yaml_parser = YAMLSpecParser()
    if yaml_parser.can_parse(content) and not content.strip().startswith("#"):
        return yaml_parser

    return MarkdownSpecParser()


__all__ = [
    "SpecParser",
    "MarkdownSpecParser",
    "YAMLSpecParser",
    "JSONSpecParser",
    "get_parser_for_file",
    "detect_parser",
]
