"""
Specification Analyzer - Analyzes specification documents and extracts structured data.

Supports markdown, YAML, and JSON specification formats with optional LLM enhancement.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional

from .models import (
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
from .parsers.spec_parser import (
    JSONSpecParser,
    MarkdownSpecParser,
    YAMLSpecParser,
    detect_parser,
    get_parser_for_file,
)


class LLMClient:
    """Client for LLM-assisted specification extraction.

    Provides optional LLM enhancement for extracting structured data from specifications.
    """

    def __init__(
        self,
        primary_model: str = "llama3.2:3b",
        fallback_model: str = "phi3:mini",
        ollama_base_url: str = "http://localhost:11434",
    ):
        """Initialize the LLM client.

        Args:
            primary_model: Primary model to use for extraction.
            fallback_model: Fallback model if primary is unavailable.
            ollama_base_url: Base URL for Ollama API.
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.ollama_base_url = ollama_base_url
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if the LLM service is available.

        Returns:
            True if the service is reachable, False otherwise.
        """
        if self._available is not None:
            return self._available

        try:
            import requests
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            self._available = response.status_code == 200
        except Exception:
            self._available = False

        return self._available

    def extract_structured_data(self, content: str) -> Optional[dict[str, Any]]:
        """Extract structured data from content using LLM.

        Args:
            content: The specification content to analyze.

        Returns:
            Extracted data as a dictionary, or None if extraction fails.
        """
        if not self.is_available():
            return None

        try:
            import requests

            prompt = f"""Analyze this specification and extract:
1. Phases with names and descriptions
2. Components with names, layers, and interfaces
3. Requirements with IDs, descriptions, types, and priorities
4. Constraints with IDs, descriptions, and types

Return as JSON with keys: phases, components, requirements, constraints

Specification:
{content[:10000]}"""  # Limit content length

            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.primary_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return self._parse_llm_response(result.get("response", ""))
        except Exception:
            pass

        return None

    def _parse_llm_response(self, response: str) -> Optional[dict[str, Any]]:
        """Parse LLM response to extract JSON data.

        Args:
            response: Raw LLM response text.

        Returns:
            Parsed JSON data or None if parsing fails.
        """
        import json
        import re

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.+?)\n?```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        return None


class SpecAnalyzer:
    """Analyzes specification documents and extracts structured data.

    Supports markdown, YAML, and JSON formats with optional LLM enhancement.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        use_llm: bool = False,
    ):
        """Initialize the SpecAnalyzer.

        Args:
            config_path: Optional path to configuration file.
            use_llm: Whether to use LLM for enhanced extraction.
        """
        self.use_llm = use_llm
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.llm_client: Optional[LLMClient] = LLMClient() if use_llm else None

        self.parsers = {
            '.md': MarkdownSpecParser(),
            '.markdown': MarkdownSpecParser(),
            '.yaml': YAMLSpecParser(),
            '.yml': YAMLSpecParser(),
            '.json': JSONSpecParser(),
        }

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_path: Path to configuration file.

        Returns:
            Configuration dictionary.
        """
        default_config = {
            "llm": {
                "enabled": False,
                "primary_model": "llama3.2:3b",
                "fallback_model": "phi3:mini",
                "confidence_threshold": 0.7,
            },
            "parsing": {
                "auto_detect_format": True,
                "strict_validation": False,
            },
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        default_config.update(loaded_config)
            except Exception:
                pass

        return default_config

    def analyze(self, spec_path: str) -> SpecificationAnalysis:
        """Analyze a specification file.

        Args:
            spec_path: Path to the specification file.

        Returns:
            SpecificationAnalysis with extracted data.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is not supported.
        """
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        suffix = path.suffix.lower()
        parser = self.parsers.get(suffix)

        if not parser:
            raise ValueError(f"Unsupported file format: {suffix}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = parser.parse(content, str(path))

        # Update metadata
        result.metadata.source_file = str(path)
        result.metadata.file_format = suffix.lstrip('.')

        # Optionally enhance with LLM
        if self.use_llm and self._should_use_llm(result):
            result = self._enhance_with_llm(content, result)

        return result

    def analyze_content(
        self,
        content: str,
        file_format: str = "markdown",
    ) -> SpecificationAnalysis:
        """Analyze specification content directly.

        Args:
            content: The specification content.
            file_format: Format of the content (markdown, yaml, json).

        Returns:
            SpecificationAnalysis with extracted data.
        """
        format_to_parser = {
            "markdown": MarkdownSpecParser(),
            "md": MarkdownSpecParser(),
            "yaml": YAMLSpecParser(),
            "yml": YAMLSpecParser(),
            "json": JSONSpecParser(),
        }

        parser = format_to_parser.get(file_format.lower())
        if not parser:
            parser = detect_parser(content)

        result = parser.parse(content)
        result.metadata.file_format = file_format

        # Optionally enhance with LLM
        if self.use_llm and self._should_use_llm(result):
            result = self._enhance_with_llm(content, result)

        return result

    def get_config(self) -> dict[str, Any]:
        """Get the current configuration.

        Returns:
            Configuration dictionary.
        """
        return self.config

    def get_model_selection(self) -> dict[str, Any]:
        """Get the model selection configuration.

        Returns:
            Model selection configuration dictionary.
        """
        return self.config.get("llm", {})

    def _should_use_llm(self, result: SpecificationAnalysis) -> bool:
        """Determine if LLM enhancement should be used.

        Args:
            result: Initial analysis result.

        Returns:
            True if LLM should be used, False otherwise.
        """
        if not self.use_llm:
            return False

        # Use LLM if result is sparse or confidence is low
        has_phases = len(result.phases) > 0
        has_components = len(result.components) > 0
        has_requirements = len(result.requirements) > 0

        threshold = self.config.get("llm", {}).get("confidence_threshold", 0.7)

        # Use LLM if no data extracted or low confidence
        if not (has_phases or has_components or has_requirements):
            return True

        if result.confidence_score < threshold:
            return True

        return False

    def _enhance_with_llm(
        self,
        content: str,
        base_result: SpecificationAnalysis,
    ) -> SpecificationAnalysis:
        """Enhance the analysis result with LLM extraction.

        Args:
            content: Original specification content.
            base_result: Initial parsing result.

        Returns:
            Enhanced SpecificationAnalysis.
        """
        if not self.llm_client or not self.llm_client.is_available():
            base_result.warnings.append("LLM enhancement requested but not available")
            return base_result

        llm_data = self.llm_client.extract_structured_data(content)
        if llm_data:
            return self._merge_results(base_result, llm_data)

        base_result.warnings.append("LLM extraction returned no data")
        return base_result

    def _merge_results(
        self,
        base: SpecificationAnalysis,
        llm_data: dict[str, Any],
    ) -> SpecificationAnalysis:
        """Merge base analysis with LLM-extracted data.

        Args:
            base: Base analysis result.
            llm_data: LLM-extracted data dictionary.

        Returns:
            Merged SpecificationAnalysis.
        """
        # Track existing items to avoid duplicates
        existing_phase_names = {p.name.lower() for p in base.phases}
        existing_component_names = {c.name.lower() for c in base.components}
        existing_req_ids = {r.id.lower() for r in base.requirements}
        existing_constraint_ids = {c.id.lower() for c in base.constraints}

        # Merge phases
        for phase_data in llm_data.get("phases", []):
            if isinstance(phase_data, dict):
                name = phase_data.get("name", "")
                if name.lower() not in existing_phase_names:
                    base.phases.append(Phase(**phase_data))
                    existing_phase_names.add(name.lower())

        # Merge components
        for comp_data in llm_data.get("components", []):
            if isinstance(comp_data, dict):
                name = comp_data.get("name", "")
                if name.lower() not in existing_component_names:
                    # Map layer string to enum if present
                    if "layer" in comp_data and isinstance(comp_data["layer"], str):
                        try:
                            comp_data["layer"] = ComponentLayer(comp_data["layer"])
                        except ValueError:
                            comp_data["layer"] = ComponentLayer.APPLICATION
                    base.components.append(Component(**comp_data))
                    existing_component_names.add(name.lower())

        # Merge requirements
        for req_data in llm_data.get("requirements", []):
            if isinstance(req_data, dict):
                req_id = req_data.get("id", "")
                if req_id.lower() not in existing_req_ids:
                    # Map type string to enum if present
                    if "type" in req_data and isinstance(req_data["type"], str):
                        try:
                            req_data["requirement_type"] = RequirementType(req_data.pop("type"))
                        except ValueError:
                            pass
                    base.requirements.append(Requirement(**req_data))
                    existing_req_ids.add(req_id.lower())

        # Merge constraints
        for con_data in llm_data.get("constraints", []):
            if isinstance(con_data, dict):
                con_id = con_data.get("id", "")
                if con_id.lower() not in existing_constraint_ids:
                    # Map type string to enum if present
                    if "type" in con_data and isinstance(con_data["type"], str):
                        try:
                            con_data["constraint_type"] = ConstraintType(con_data.pop("type"))
                        except ValueError:
                            pass
                    base.constraints.append(Constraint(**con_data))
                    existing_constraint_ids.add(con_id.lower())

        base.llm_assisted = True
        return base


__all__ = ["SpecAnalyzer", "LLMClient"]
