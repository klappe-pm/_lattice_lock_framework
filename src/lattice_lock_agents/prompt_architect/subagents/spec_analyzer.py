"""
Specification Analyzer Subagent

Analyzes project specifications and extracts structured requirements for prompt generation.
"""

import json
import logging
import os
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
from lattice_lock_agents.prompt_architect.subagents.parsers.spec_parser import (
    SpecParser,
    MarkdownSpecParser,
    YAMLSpecParser,
    JSONSpecParser,
    get_parser_for_file,
    detect_parser,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM-assisted extraction."""

    def __init__(
        self,
        primary_model: str = "deepseek-r1:70b",
        fallback_model: str = "claude-opus-4.1",
        ollama_base_url: str = "http://localhost:11434",
    ) -> None:
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.ollama_base_url = ollama_base_url
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        if self._available is not None:
            return self._available

        try:
            import requests

            response = requests.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=5,
            )
            self._available = response.status_code == 200
        except Exception:
            self._available = False

        return self._available

    def extract_structured_data(
        self,
        content: str,
        extraction_type: str = "specification",
    ) -> Optional[dict[str, Any]]:
        """Use LLM to extract structured data from content.

        Args:
            content: The raw content to analyze.
            extraction_type: Type of extraction to perform.

        Returns:
            Extracted structured data or None if extraction fails.
        """
        if not self.is_available():
            logger.debug("LLM service not available, skipping LLM-assisted extraction")
            return None

        prompt = self._build_extraction_prompt(content, extraction_type)

        try:
            result = self._call_llm(prompt)
            if result:
                return self._parse_llm_response(result)
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}")

        return None

    def _build_extraction_prompt(self, content: str, extraction_type: str) -> str:
        """Build the extraction prompt for the LLM."""
        return f"""Analyze the following {extraction_type} document and extract structured information.

Return a JSON object with the following structure:
{{
    "phases": [
        {{"name": "...", "description": "...", "components": [...], "dependencies": [...]}}
    ],
    "components": [
        {{"name": "...", "layer": "...", "interfaces": [...], "files": [...], "dependencies": [...]}}
    ],
    "requirements": [
        {{"id": "REQ-001", "description": "...", "type": "functional|non_functional|performance|security", "priority": "high|medium|low", "phase": "..."}}
    ],
    "constraints": [
        {{"id": "CON-001", "description": "...", "type": "technical|business|regulatory|resource|time"}}
    ]
}}

Document content:
{content[:8000]}

Return ONLY the JSON object, no additional text."""

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the LLM API."""
        try:
            import requests

            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.primary_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 4096,
                    },
                },
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
        except Exception as e:
            logger.debug(f"Primary model call failed: {e}")

        return None

    def _parse_llm_response(self, response: str) -> Optional[dict[str, Any]]:
        """Parse the LLM response into structured data."""
        try:
            json_match = response.strip()
            if "```json" in json_match:
                json_match = json_match.split("```json")[1].split("```")[0]
            elif "```" in json_match:
                json_match = json_match.split("```")[1].split("```")[0]

            return json.loads(json_match)
        except json.JSONDecodeError:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass

        return None


class SpecAnalyzer:
    """Specification Analyzer subagent.

    Analyzes project specifications and extracts structured requirements,
    components, and dependencies for prompt generation.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        use_llm: bool = True,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        """Initialize the SpecAnalyzer.

        Args:
            config_path: Path to the subagent YAML configuration file.
            use_llm: Whether to use LLM-assisted extraction for complex specs.
            llm_client: Optional custom LLM client instance.
        """
        self.config = self._load_config(config_path)
        self.use_llm = use_llm
        self.llm_client = llm_client or self._create_llm_client()

        self._parsers: dict[str, SpecParser] = {
            "markdown": MarkdownSpecParser(),
            "yaml": YAMLSpecParser(),
            "json": JSONSpecParser(),
        }

    def _load_config(self, config_path: Optional[str] = None) -> dict[str, Any]:
        """Load the subagent configuration from YAML."""
        if config_path is None:
            default_paths = [
                "agent_definitions/prompt_architect_agent/subagents/spec_analyzer.yaml",
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "agent_definitions"
                / "prompt_architect_agent"
                / "subagents"
                / "spec_analyzer.yaml",
            ]
            for path in default_paths:
                if Path(path).exists():
                    config_path = str(path)
                    break

        if config_path and Path(config_path).exists():
            try:
                with open(config_path) as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration if YAML file is not available."""
        return {
            "agent": {
                "identity": {
                    "name": "spec_analyzer",
                    "version": "1.0.0",
                },
            },
            "model_selection": {
                "default_provider": "local",
                "default_model": "deepseek-r1:70b",
                "strategies": {
                    "document_analysis": {
                        "primary": "deepseek-r1:70b",
                        "fallback": "claude-opus-4.1",
                    },
                    "extraction": {
                        "primary": "qwen2.5:32b",
                        "fallback": "claude-sonnet-4.5",
                    },
                },
            },
        }

    def _create_llm_client(self) -> LLMClient:
        """Create an LLM client based on configuration."""
        model_config = self.config.get("model_selection", {})
        strategies = model_config.get("strategies", {})
        doc_analysis = strategies.get("document_analysis", {})

        primary_model = doc_analysis.get("primary", "deepseek-r1:70b")
        fallback_model = doc_analysis.get("fallback", "claude-opus-4.1")

        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

        return LLMClient(
            primary_model=primary_model,
            fallback_model=fallback_model,
            ollama_base_url=ollama_url,
        )

    def analyze(self, spec_path: str) -> SpecificationAnalysis:
        """Analyze a specification file and extract structured data.

        Args:
            spec_path: Path to the specification file.

        Returns:
            A SpecificationAnalysis object containing the extracted data.

        Raises:
            FileNotFoundError: If the specification file does not exist.
            ValueError: If the file format is not supported.
        """
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        content = path.read_text(encoding="utf-8")
        parser = get_parser_for_file(spec_path)
        result = parser.parse(content, spec_path)

        if self.use_llm and self._should_use_llm(result):
            result = self._enhance_with_llm(content, result)

        return result

    def analyze_content(
        self,
        content: str,
        file_format: str = "markdown",
        source_path: Optional[str] = None,
    ) -> SpecificationAnalysis:
        """Analyze specification content directly.

        Args:
            content: The raw specification content.
            file_format: Format of the content (markdown, yaml, json).
            source_path: Optional source path for metadata.

        Returns:
            A SpecificationAnalysis object containing the extracted data.
        """
        parser = self._parsers.get(file_format.lower())
        if parser is None:
            parser = detect_parser(content)

        result = parser.parse(content, source_path)

        if self.use_llm and self._should_use_llm(result):
            result = self._enhance_with_llm(content, result)

        return result

    def _should_use_llm(self, result: SpecificationAnalysis) -> bool:
        """Determine if LLM enhancement should be used.

        Uses LLM if the basic parsing didn't extract enough structured data.
        """
        has_phases = len(result.phases) > 0
        has_components = len(result.components) > 0
        has_requirements = len(result.requirements) > 0

        if not has_phases and not has_components and not has_requirements:
            return True

        if result.confidence_score < 0.8:
            return True

        return False

    def _enhance_with_llm(
        self,
        content: str,
        base_result: SpecificationAnalysis,
    ) -> SpecificationAnalysis:
        """Enhance the analysis result using LLM extraction.

        Args:
            content: The raw specification content.
            base_result: The base analysis result from parsing.

        Returns:
            Enhanced SpecificationAnalysis with LLM-extracted data.
        """
        if not self.llm_client.is_available():
            base_result.warnings.append(
                "LLM service not available, using basic parsing only"
            )
            return base_result

        llm_data = self.llm_client.extract_structured_data(content)
        if llm_data is None:
            base_result.warnings.append("LLM extraction failed, using basic parsing only")
            return base_result

        enhanced = self._merge_results(base_result, llm_data)
        enhanced.llm_assisted = True
        enhanced.confidence_score = min(0.95, base_result.confidence_score + 0.2)

        return enhanced

    def _merge_results(
        self,
        base: SpecificationAnalysis,
        llm_data: dict[str, Any],
    ) -> SpecificationAnalysis:
        """Merge LLM-extracted data with base parsing results.

        Args:
            base: The base analysis result.
            llm_data: Data extracted by the LLM.

        Returns:
            Merged SpecificationAnalysis.
        """
        phases = list(base.phases)
        components = list(base.components)
        requirements = list(base.requirements)
        constraints = list(base.constraints)

        existing_phase_names = {p.name.lower() for p in phases}
        for phase_data in llm_data.get("phases", []):
            if isinstance(phase_data, dict):
                name = phase_data.get("name", "")
                if name.lower() not in existing_phase_names:
                    phases.append(
                        Phase(
                            name=name,
                            description=phase_data.get("description"),
                            components=phase_data.get("components", []),
                            dependencies=phase_data.get("dependencies", []),
                        )
                    )

        existing_component_names = {c.name.lower() for c in components}
        for comp_data in llm_data.get("components", []):
            if isinstance(comp_data, dict):
                name = comp_data.get("name", "")
                if name.lower() not in existing_component_names:
                    layer_str = comp_data.get("layer", "application")
                    try:
                        layer = ComponentLayer(layer_str.lower())
                    except ValueError:
                        layer = ComponentLayer.APPLICATION

                    components.append(
                        Component(
                            name=name,
                            layer=layer,
                            interfaces=comp_data.get("interfaces", []),
                            files=comp_data.get("files", []),
                            dependencies=comp_data.get("dependencies", []),
                        )
                    )

        existing_req_ids = {r.id for r in requirements}
        for req_data in llm_data.get("requirements", []):
            if isinstance(req_data, dict):
                req_id = req_data.get("id", f"REQ-{len(requirements) + 1:03d}")
                if req_id not in existing_req_ids:
                    req_type_str = req_data.get("type", "functional")
                    try:
                        req_type = RequirementType(req_type_str.lower())
                    except ValueError:
                        req_type = RequirementType.FUNCTIONAL

                    requirements.append(
                        Requirement(
                            id=req_id,
                            description=req_data.get("description", ""),
                            priority=req_data.get("priority", "medium"),
                            phase=req_data.get("phase"),
                            requirement_type=req_type,
                        )
                    )

        existing_con_ids = {c.id for c in constraints}
        for con_data in llm_data.get("constraints", []):
            if isinstance(con_data, dict):
                con_id = con_data.get("id", f"CON-{len(constraints) + 1:03d}")
                if con_id not in existing_con_ids:
                    con_type_str = con_data.get("type", "technical")
                    try:
                        con_type = ConstraintType(con_type_str.lower())
                    except ValueError:
                        con_type = ConstraintType.TECHNICAL

                    constraints.append(
                        Constraint(
                            id=con_id,
                            description=con_data.get("description", ""),
                            constraint_type=con_type,
                        )
                    )

        return SpecificationAnalysis(
            phases=phases,
            components=components,
            requirements=requirements,
            constraints=constraints,
            metadata=base.metadata,
            raw_sections=base.raw_sections,
            analysis_timestamp=base.analysis_timestamp,
            warnings=base.warnings,
        )

    def get_config(self) -> dict[str, Any]:
        """Get the current configuration."""
        return self.config

    def get_model_selection(self) -> dict[str, Any]:
        """Get the model selection configuration."""
        return self.config.get("model_selection", {})


__all__ = [
    "SpecAnalyzer",
    "LLMClient",
]
