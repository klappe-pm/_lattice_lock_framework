import json
import yaml
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path
from ..models import SpecificationAnalysis, SpecificationMetadata, Phase, Component, Requirement, Constraint

class SpecParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> SpecificationAnalysis:
        pass

class JSONSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        data = json.loads(content)
        return _parse_dict_to_analysis(data, file_format="json")

class YAMLSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        data = yaml.safe_load(content)
        return _parse_dict_to_analysis(data, file_format="yaml")


def _parse_dict_to_analysis(data: Dict[str, Any], file_format: str) -> SpecificationAnalysis:
    """Parse a dictionary into a SpecificationAnalysis object.
    
    Handles flexible input formats and maps to the expected model structure.
    """
    metadata = SpecificationMetadata(file_format=file_format)
    
    # Extract metadata fields
    if "title" in data:
        metadata.title = data["title"]
    if "version" in data:
        metadata.version = data["version"]
    if "author" in data:
        metadata.author = data["author"]
    
    # Parse phases
    phases: List[Phase] = []
    if "phases" in data and isinstance(data["phases"], list):
        for phase_data in data["phases"]:
            if isinstance(phase_data, dict):
                phases.append(Phase(
                    name=phase_data.get("name", "Unknown"),
                    description=phase_data.get("description")
                ))
            elif isinstance(phase_data, str):
                phases.append(Phase(name=phase_data))
    
    # Parse components
    components: List[Component] = []
    if "components" in data and isinstance(data["components"], list):
        for comp_data in data["components"]:
            if isinstance(comp_data, dict):
                components.append(Component(
                    name=comp_data.get("name", "Unknown"),
                    description=comp_data.get("description")
                ))
            elif isinstance(comp_data, str):
                components.append(Component(name=comp_data))
    
    # Parse requirements
    requirements: List[Requirement] = []
    if "requirements" in data and isinstance(data["requirements"], list):
        for i, req_data in enumerate(data["requirements"]):
            if isinstance(req_data, dict):
                requirements.append(Requirement(
                    id=req_data.get("id", f"REQ-{i+1:03d}"),
                    description=req_data.get("description", "")
                ))
            elif isinstance(req_data, str):
                requirements.append(Requirement(
                    id=f"REQ-{i+1:03d}",
                    description=req_data
                ))
    
    # Parse constraints
    constraints: List[Constraint] = []
    if "constraints" in data and isinstance(data["constraints"], list):
        for i, con_data in enumerate(data["constraints"]):
            if isinstance(con_data, dict):
                constraints.append(Constraint(
                    id=con_data.get("id", f"CON-{i+1:03d}"),
                    description=con_data.get("description", "")
                ))
            elif isinstance(con_data, str):
                constraints.append(Constraint(
                    id=f"CON-{i+1:03d}",
                    description=con_data
                ))
    
    return SpecificationAnalysis(
        metadata=metadata,
        phases=phases,
        components=components,
        requirements=requirements,
        constraints=constraints,
        raw_sections=data
    )

class MarkdownSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        metadata = SpecificationMetadata(file_format="markdown")

        # Simple heuristic parsing for Markdown
        # 1. Extract Title from first H1 header
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata.title = title_match.group(1).strip()

        # 2. Extract Version if present
        version_match = re.search(r'\*\*Version:\*\*\s*(.+?)(?:\n|$)', content)
        if version_match:
            metadata.version = version_match.group(1).strip()

        phases: List[Phase] = []
        requirements: List[Requirement] = []
        constraints: List[Constraint] = []

        # 3. Extract Phases (Headers starting with "Phase")
        phase_matches = re.finditer(r'^##\s+(Phase\s+\d+[:\s].+)$', content, re.MULTILINE)
        for match in phase_matches:
            phases.append(Phase(name=match.group(1).strip()))

        # 4. Extract Requirements (Bullet points under "Requirements" section - simplified)
        # Look for lines starting with "- " or "* " that contain "must" or "should"
        req_counter = 1
        req_matches = re.finditer(r'^[\-\*]\s+(.+?(?:must|should).+?)$', content, re.MULTILINE | re.IGNORECASE)
        for match in req_matches:
            requirements.append(Requirement(
                id=f"REQ-{req_counter:03d}",
                description=match.group(1).strip()
            ))
            req_counter += 1

        # 5. Extract Constraints (Bullet points under "Constraints" section)
        constraint_counter = 1
        constraint_section = re.search(r'##\s+Constraints\s*\n((?:[\-\*]\s+.+\n?)+)', content, re.MULTILINE)
        if constraint_section:
            constraint_matches = re.finditer(r'^[\-\*]\s+(.+)$', constraint_section.group(1), re.MULTILINE)
            for match in constraint_matches:
                constraints.append(Constraint(
                    id=f"CON-{constraint_counter:03d}",
                    description=match.group(1).strip()
                ))
                constraint_counter += 1

        return SpecificationAnalysis(
            metadata=metadata,
            phases=phases,
            requirements=requirements,
            constraints=constraints,
            raw_sections={"content": content}
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
        raise ValueError(f"Unsupported file format: {suffix}")

    return parser


def detect_parser(content: str) -> SpecParser:
    """Detect the appropriate parser based on content.

    Args:
        content: The specification content to analyze.

    Returns:
        An appropriate SpecParser instance.
    """
    content_stripped = content.strip()

    # Try JSON first
    if content_stripped.startswith('{') or content_stripped.startswith('['):
        return JSONSpecParser()

    # Try YAML (if it has YAML-specific patterns)
    if content_stripped.startswith('---') or ': ' in content_stripped.split('\n')[0]:
        return YAMLSpecParser()

    # Default to Markdown
    return MarkdownSpecParser()
