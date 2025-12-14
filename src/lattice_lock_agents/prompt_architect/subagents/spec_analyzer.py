import os
from pathlib import Path
from typing import Optional
from .parsers.spec_parser import MarkdownSpecParser, YAMLSpecParser, JSONSpecParser, SpecParser
from ..models import SpecificationAnalysis

class SpecAnalyzer:
    def __init__(self):
        self.parsers = {
            '.md': MarkdownSpecParser(),
            '.markdown': MarkdownSpecParser(),
            '.yaml': YAMLSpecParser(),
            '.yml': YAMLSpecParser(),
            '.json': JSONSpecParser()
        }

    def analyze(self, spec_path: str) -> SpecificationAnalysis:
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        suffix = path.suffix.lower()
        parser = self.parsers.get(suffix)

        if not parser:
            raise ValueError(f"Unsupported file format: {suffix}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return parser.parse(content)

    # Future: Add LLM-assisted extraction here
    # def analyze_with_llm(self, content: str) -> SpecificationAnalysis:
    #     ...
