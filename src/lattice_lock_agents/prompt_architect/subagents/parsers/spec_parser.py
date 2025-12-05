import json
import yaml
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path
from ...models import SpecificationAnalysis, Phase, Component, Requirement, Constraint

class SpecParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> SpecificationAnalysis:
        pass

class JSONSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        data = json.loads(content)
        # Basic mapping, assumes structure matches somewhat or is raw
        # For robust parsing, we'd need schema validation or flexible mapping
        # Here we'll try to map direct fields if they exist
        return SpecificationAnalysis(**data)

class YAMLSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        data = yaml.safe_load(content)
        return SpecificationAnalysis(**data)

class MarkdownSpecParser(SpecParser):
    def parse(self, content: str) -> SpecificationAnalysis:
        analysis = SpecificationAnalysis(raw_content=content)
        
        # Simple heuristic parsing for Markdown
        # 1. Extract Project Name
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            analysis.project_name = title_match.group(1).strip()
            
        # 2. Extract Phases (Headers starting with "Phase")
        phase_matches = re.finditer(r'^##\s+(Phase\s+\d+[:\s].+)$', content, re.MULTILINE)
        for match in phase_matches:
            analysis.phases.append(Phase(name=match.group(1).strip(), description=""))
            
        # 3. Extract Requirements (Bullet points under "Requirements" section - simplified)
        # This is a naive implementation. A robust one would track sections.
        # For now, we'll look for lines starting with "- " or "* " that contain "must" or "should"
        req_matches = re.finditer(r'^[\-\*]\s+(.+?(?:must|should).+?)$', content, re.MULTILINE | re.IGNORECASE)
        for match in req_matches:
            analysis.requirements.append(Requirement(description=match.group(1).strip()))
            
        return analysis
