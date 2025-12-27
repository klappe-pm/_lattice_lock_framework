"""
Tests for the Specification Analyzer subagent.

Tests the models, parsers, and SpecAnalyzer class.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from lattice_lock.agents.prompt_architect.subagents.models import (
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
from lattice_lock.agents.prompt_architect.subagents.parsers.spec_parser import (
    JSONSpecParser,
    MarkdownSpecParser,
    YAMLSpecParser,
    detect_parser,
    get_parser_for_file,
)
from lattice_lock.agents.prompt_architect.subagents.spec_analyzer import SpecAnalyzer

# LLMClient is not yet implemented - tests that require it will be skipped
try:
    from lattice_lock.agents.prompt_architect.subagents.spec_analyzer import LLMClient
except ImportError:
    LLMClient = None  # type: ignore[misc, assignment]


class TestRequirementType:
    """Tests for RequirementType enum."""

    def test_requirement_types_exist(self) -> None:
        """Test that all expected requirement types exist."""
        assert RequirementType.FUNCTIONAL.value == "functional"
        assert RequirementType.NON_FUNCTIONAL.value == "non_functional"
        assert RequirementType.CONSTRAINT.value == "constraint"
        assert RequirementType.INTERFACE.value == "interface"
        assert RequirementType.PERFORMANCE.value == "performance"
        assert RequirementType.SECURITY.value == "security"


class TestConstraintType:
    """Tests for ConstraintType enum."""

    def test_constraint_types_exist(self) -> None:
        """Test that all expected constraint types exist."""
        assert ConstraintType.TECHNICAL.value == "technical"
        assert ConstraintType.BUSINESS.value == "business"
        assert ConstraintType.REGULATORY.value == "regulatory"
        assert ConstraintType.RESOURCE.value == "resource"
        assert ConstraintType.TIME.value == "time"
        assert ConstraintType.DEPENDENCY.value == "dependency"


class TestComponentLayer:
    """Tests for ComponentLayer enum."""

    def test_component_layers_exist(self) -> None:
        """Test that all expected component layers exist."""
        assert ComponentLayer.PRESENTATION.value == "presentation"
        assert ComponentLayer.APPLICATION.value == "application"
        assert ComponentLayer.DOMAIN.value == "domain"
        assert ComponentLayer.INFRASTRUCTURE.value == "infrastructure"
        assert ComponentLayer.DATA.value == "data"
        assert ComponentLayer.INTEGRATION.value == "integration"


class TestRequirement:
    """Tests for Requirement model."""

    def test_create_requirement(self) -> None:
        """Test creating a requirement."""
        req = Requirement(
            id="REQ-001",
            description="The system must support user authentication",
            priority="high",
            phase="Phase 1",
            requirement_type=RequirementType.FUNCTIONAL,
        )
        assert req.id == "REQ-001"
        assert req.description == "The system must support user authentication"
        assert req.priority == "high"
        assert req.phase == "Phase 1"
        assert req.requirement_type == RequirementType.FUNCTIONAL

    def test_requirement_defaults(self) -> None:
        """Test requirement default values."""
        req = Requirement(
            id="REQ-002",
            description="Test requirement",
        )
        assert req.priority == "medium"
        assert req.phase is None
        assert req.requirement_type == RequirementType.FUNCTIONAL
        assert req.acceptance_criteria == []
        assert req.dependencies == []


class TestConstraint:
    """Tests for Constraint model."""

    def test_create_constraint(self) -> None:
        """Test creating a constraint."""
        con = Constraint(
            id="CON-001",
            description="Must use Python 3.10+",
            constraint_type=ConstraintType.TECHNICAL,
        )
        assert con.id == "CON-001"
        assert con.description == "Must use Python 3.10+"
        assert con.constraint_type == ConstraintType.TECHNICAL

    def test_constraint_defaults(self) -> None:
        """Test constraint default values."""
        con = Constraint(
            id="CON-002",
            description="Test constraint",
        )
        assert con.constraint_type == ConstraintType.TECHNICAL
        assert con.source_section is None
        assert con.impact is None
        assert con.mitigation is None


class TestComponent:
    """Tests for Component model."""

    def test_create_component(self) -> None:
        """Test creating a component."""
        comp = Component(
            name="AuthService",
            description="Handles user authentication",
            layer=ComponentLayer.APPLICATION,
            interfaces=["IAuthService"],
            files=["src/auth/service.py"],
        )
        assert comp.name == "AuthService"
        assert comp.description == "Handles user authentication"
        assert comp.layer == ComponentLayer.APPLICATION
        assert "IAuthService" in comp.interfaces
        assert "src/auth/service.py" in comp.files

    def test_component_defaults(self) -> None:
        """Test component default values."""
        comp = Component(name="TestComponent")
        assert comp.layer == ComponentLayer.APPLICATION
        assert comp.interfaces == []
        assert comp.files == []
        assert comp.dependencies == []
        assert comp.responsibilities == []


class TestPhase:
    """Tests for Phase model."""

    def test_create_phase(self) -> None:
        """Test creating a phase."""
        phase = Phase(
            name="Foundation",
            description="Set up project foundation",
            scope="Core infrastructure",
            components=["CLI", "Validator"],
            dependencies=[],
        )
        assert phase.name == "Foundation"
        assert phase.description == "Set up project foundation"
        assert phase.scope == "Core infrastructure"
        assert "CLI" in phase.components
        assert "Validator" in phase.components

    def test_phase_defaults(self) -> None:
        """Test phase default values."""
        phase = Phase(name="Test Phase")
        assert phase.description is None
        assert phase.scope is None
        assert phase.components == []
        assert phase.dependencies == []
        assert phase.deliverables == []


class TestSpecificationMetadata:
    """Tests for SpecificationMetadata model."""

    def test_create_metadata(self) -> None:
        """Test creating metadata."""
        meta = SpecificationMetadata(
            title="Test Specification",
            version="1.0.0",
            author="Test Author",
            source_file="test.md",
            file_format="markdown",
        )
        assert meta.title == "Test Specification"
        assert meta.version == "1.0.0"
        assert meta.author == "Test Author"
        assert meta.source_file == "test.md"
        assert meta.file_format == "markdown"


class TestSpecificationAnalysis:
    """Tests for SpecificationAnalysis model."""

    def test_create_analysis(self) -> None:
        """Test creating an analysis."""
        analysis = SpecificationAnalysis(
            phases=[Phase(name="Phase 1")],
            components=[Component(name="Component A")],
            requirements=[Requirement(id="REQ-001", description="Test")],
            constraints=[Constraint(id="CON-001", description="Test")],
        )
        assert len(analysis.phases) == 1
        assert len(analysis.components) == 1
        assert len(analysis.requirements) == 1
        assert len(analysis.constraints) == 1

    def test_analysis_defaults(self) -> None:
        """Test analysis default values."""
        analysis = SpecificationAnalysis()
        assert analysis.phases == []
        assert analysis.components == []
        assert analysis.requirements == []
        assert analysis.constraints == []
        assert analysis.confidence_score == 1.0
        assert analysis.llm_assisted is False
        assert analysis.warnings == []

    def test_to_dict(self) -> None:
        """Test converting analysis to dictionary."""
        analysis = SpecificationAnalysis(
            phases=[Phase(name="Phase 1")],
            requirements=[Requirement(id="REQ-001", description="Test")],
        )
        data = analysis.to_dict()
        assert isinstance(data, dict)
        assert "phases" in data
        assert "requirements" in data
        assert len(data["phases"]) == 1
        assert len(data["requirements"]) == 1

    def test_get_phase_by_name(self) -> None:
        """Test getting a phase by name."""
        analysis = SpecificationAnalysis(
            phases=[
                Phase(name="Foundation"),
                Phase(name="Implementation"),
            ]
        )
        phase = analysis.get_phase_by_name("Foundation")
        assert phase is not None
        assert phase.name == "Foundation"

        phase = analysis.get_phase_by_name("foundation")
        assert phase is not None

        phase = analysis.get_phase_by_name("NonExistent")
        assert phase is None

    def test_get_component_by_name(self) -> None:
        """Test getting a component by name."""
        analysis = SpecificationAnalysis(
            components=[
                Component(name="AuthService"),
                Component(name="DataService"),
            ]
        )
        comp = analysis.get_component_by_name("AuthService")
        assert comp is not None
        assert comp.name == "AuthService"

        comp = analysis.get_component_by_name("authservice")
        assert comp is not None

        comp = analysis.get_component_by_name("NonExistent")
        assert comp is None

    def test_get_requirements_by_phase(self) -> None:
        """Test getting requirements by phase."""
        analysis = SpecificationAnalysis(
            requirements=[
                Requirement(id="REQ-001", description="Test 1", phase="Phase 1"),
                Requirement(id="REQ-002", description="Test 2", phase="Phase 1"),
                Requirement(id="REQ-003", description="Test 3", phase="Phase 2"),
            ]
        )
        reqs = analysis.get_requirements_by_phase("Phase 1")
        assert len(reqs) == 2

        reqs = analysis.get_requirements_by_phase("phase 1")
        assert len(reqs) == 2

        reqs = analysis.get_requirements_by_phase("Phase 3")
        assert len(reqs) == 0

    def test_get_requirements_by_type(self) -> None:
        """Test getting requirements by type."""
        analysis = SpecificationAnalysis(
            requirements=[
                Requirement(
                    id="REQ-001",
                    description="Test 1",
                    requirement_type=RequirementType.FUNCTIONAL,
                ),
                Requirement(
                    id="REQ-002",
                    description="Test 2",
                    requirement_type=RequirementType.PERFORMANCE,
                ),
                Requirement(
                    id="REQ-003",
                    description="Test 3",
                    requirement_type=RequirementType.FUNCTIONAL,
                ),
            ]
        )
        reqs = analysis.get_requirements_by_type(RequirementType.FUNCTIONAL)
        assert len(reqs) == 2

        reqs = analysis.get_requirements_by_type(RequirementType.PERFORMANCE)
        assert len(reqs) == 1

        reqs = analysis.get_requirements_by_type(RequirementType.SECURITY)
        assert len(reqs) == 0


class TestMarkdownSpecParser:
    """Tests for MarkdownSpecParser."""

    def test_parse_simple_markdown(self) -> None:
        """Test parsing simple markdown content."""
        parser = MarkdownSpecParser()
        content = """# Test Specification

**Version:** 1.0.0

## Requirements

- System must support authentication
- Application must be scalable
"""
        result = parser.parse(content)

        assert result.metadata.title == "Test Specification"
        assert result.metadata.version == "1.0.0"
        assert result.metadata.file_format == "markdown"
        assert len(result.requirements) >= 2

    def test_parse_with_phases(self) -> None:
        """Test parsing markdown with phase sections."""
        parser = MarkdownSpecParser()
        content = """# Project Spec

## Phase 1: Foundation

Setup the foundation.

## Phase 2: Implementation

Implement features.
"""
        result = parser.parse(content)
        assert len(result.phases) == 2
        # Parser extracts phase name after "Phase X:" prefix
        assert result.phases[0].name == "Foundation"
        assert result.phases[1].name == "Implementation"

    def test_parse_with_constraints(self) -> None:
        """Test parsing markdown with constraints."""
        parser = MarkdownSpecParser()
        content = """# Spec

## Constraints

- Must use Python 3.10+
- Must be compatible with Linux
"""
        result = parser.parse(content)
        assert len(result.constraints) >= 2

    def test_parse_empty_content(self) -> None:
        """Test parsing empty content."""
        parser = MarkdownSpecParser()
        result = parser.parse("")
        assert result.phases == []
        assert result.components == []
        assert result.requirements == []


class TestYAMLSpecParser:
    """Tests for YAMLSpecParser."""

    def test_parse_yaml_spec(self) -> None:
        """Test parsing YAML specification."""
        parser = YAMLSpecParser()
        content = """
title: Test Specification
version: 1.0.0

phases:
  - name: Foundation
    description: Set up foundation
  - name: Implementation
    description: Implement features

components:
  - name: AuthService
    description: Authentication service

requirements:
  - id: REQ-001
    description: Must support authentication
  - id: REQ-002
    description: Must be scalable

constraints:
  - id: CON-001
    description: Must use Python 3.10+
"""
        result = parser.parse(content)

        assert result.metadata.title == "Test Specification"
        assert result.metadata.version == "1.0.0"
        assert result.metadata.file_format == "yaml"
        assert len(result.phases) == 2
        assert len(result.components) == 1
        assert len(result.requirements) == 2
        assert len(result.constraints) == 1

    def test_parse_yaml_with_string_items(self) -> None:
        """Test parsing YAML with string list items."""
        parser = YAMLSpecParser()
        content = """
phases:
  - Phase 1
  - Phase 2

components:
  - Component A
  - Component B

requirements:
  - Must be fast
  - Must be secure
"""
        result = parser.parse(content)
        assert len(result.phases) == 2
        assert len(result.components) == 2
        assert len(result.requirements) == 2

    def test_parse_invalid_yaml(self) -> None:
        """Test parsing invalid YAML content returns empty result."""
        parser = YAMLSpecParser()
        # Parser gracefully handles invalid YAML by returning empty result
        result = parser.parse("invalid: yaml: content: [")
        assert result.phases == []
        assert result.components == []
        assert result.requirements == []


class TestJSONSpecParser:
    """Tests for JSONSpecParser."""

    def test_parse_json_spec(self) -> None:
        """Test parsing JSON specification."""
        parser = JSONSpecParser()
        content = json.dumps(
            {
                "title": "Test Specification",
                "version": "1.0.0",
                "phases": [
                    {"name": "Foundation", "description": "Set up foundation"},
                    {"name": "Implementation", "description": "Implement features"},
                ],
                "components": [
                    {"name": "AuthService", "description": "Auth service"},
                ],
                "requirements": [
                    {
                        "id": "REQ-001",
                        "description": "Must support authentication",
                    },
                ],
            }
        )
        result = parser.parse(content)

        assert result.metadata.title == "Test Specification"
        assert result.metadata.file_format == "json"
        assert len(result.phases) == 2
        assert len(result.components) == 1
        assert len(result.requirements) == 1

    def test_parse_invalid_json(self) -> None:
        """Test parsing invalid JSON content returns empty result."""
        parser = JSONSpecParser()
        # Parser gracefully handles invalid JSON by returning empty result
        result = parser.parse("{invalid json}")
        assert result.phases == []
        assert result.components == []
        assert result.requirements == []


class TestGetParserForFile:
    """Tests for get_parser_for_file function."""

    def test_get_markdown_parser(self) -> None:
        """Test getting parser for markdown files."""
        parser = get_parser_for_file("test.md")
        assert isinstance(parser, MarkdownSpecParser)

        parser = get_parser_for_file("test.markdown")
        assert isinstance(parser, MarkdownSpecParser)

    def test_get_yaml_parser(self) -> None:
        """Test getting parser for YAML files."""
        parser = get_parser_for_file("test.yaml")
        assert isinstance(parser, YAMLSpecParser)

        parser = get_parser_for_file("test.yml")
        assert isinstance(parser, YAMLSpecParser)

    def test_get_json_parser(self) -> None:
        """Test getting parser for JSON files."""
        parser = get_parser_for_file("test.json")
        assert isinstance(parser, JSONSpecParser)

    def test_unsupported_extension(self) -> None:
        """Test error for unsupported file extension."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            get_parser_for_file("test.txt")


class TestDetectParser:
    """Tests for detect_parser function."""

    def test_detect_json(self) -> None:
        """Test detecting JSON content."""
        parser = detect_parser('{"key": "value"}')
        assert isinstance(parser, JSONSpecParser)

    def test_detect_yaml(self) -> None:
        """Test detecting YAML content."""
        parser = detect_parser("key: value\nlist:\n  - item")
        assert isinstance(parser, YAMLSpecParser)

    def test_detect_markdown(self) -> None:
        """Test detecting markdown content."""
        parser = detect_parser("# Title\n\nContent here")
        assert isinstance(parser, MarkdownSpecParser)


@pytest.mark.skipif(LLMClient is None, reason="LLMClient not yet implemented")
class TestLLMClient:
    """Tests for LLMClient."""

    def test_create_client(self) -> None:
        """Test creating an LLM client."""
        client = LLMClient(
            primary_model="test-model",
            fallback_model="fallback-model",
            ollama_base_url="http://localhost:11434",
        )
        assert client.primary_model == "test-model"
        assert client.fallback_model == "fallback-model"

    def test_is_available_when_offline(self) -> None:
        """Test availability check when service is offline."""
        client = LLMClient(ollama_base_url="http://localhost:99999")
        assert client.is_available() is False

    @patch("requests.get")
    def test_is_available_when_online(self, mock_get: MagicMock) -> None:
        """Test availability check when service is online."""
        mock_get.return_value.status_code = 200
        client = LLMClient()
        client._available = None
        assert client.is_available() is True

    def test_extract_structured_data_when_unavailable(self) -> None:
        """Test extraction when LLM is unavailable."""
        client = LLMClient(ollama_base_url="http://localhost:99999")
        result = client.extract_structured_data("test content")
        assert result is None

    def test_parse_llm_response_valid_json(self) -> None:
        """Test parsing valid JSON response."""
        client = LLMClient()
        response = '{"phases": [], "components": []}'
        result = client._parse_llm_response(response)
        assert result is not None
        assert "phases" in result

    def test_parse_llm_response_with_markdown(self) -> None:
        """Test parsing JSON wrapped in markdown."""
        client = LLMClient()
        response = '```json\n{"phases": []}\n```'
        result = client._parse_llm_response(response)
        assert result is not None
        assert "phases" in result

    def test_parse_llm_response_invalid(self) -> None:
        """Test parsing invalid response."""
        client = LLMClient()
        result = client._parse_llm_response("not json at all")
        assert result is None


class TestSpecAnalyzer:
    """Tests for SpecAnalyzer."""

    def test_create_analyzer(self) -> None:
        """Test creating a SpecAnalyzer."""
        analyzer = SpecAnalyzer()
        assert analyzer is not None
        assert analyzer.parsers is not None

    def test_analyze_markdown_file(self) -> None:
        """Test analyzing a markdown specification file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                """# Test Specification

**Version:** 1.0.0

## Phase 1: Foundation

Setup the foundation.

## Phase 2: Implementation

Implement features.

## Requirements

- System must support authentication
- Application must be scalable

## Constraints

- Must use Python 3.10+
"""
            )
            f.flush()

            analyzer = SpecAnalyzer()
            result = analyzer.analyze(f.name)

            assert result is not None
            assert result.metadata.title == "Test Specification"
            assert result.metadata.version == "1.0.0"
            assert len(result.phases) == 2
            assert len(result.requirements) >= 2
            assert len(result.constraints) >= 1

            Path(f.name).unlink()

    def test_analyze_yaml_file(self) -> None:
        """Test analyzing a YAML specification file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "title": "YAML Spec",
                    "version": "2.0.0",
                    "phases": [
                        {"name": "Phase 1", "description": "First phase"},
                    ],
                    "requirements": [
                        {"id": "REQ-001", "description": "Test requirement"},
                    ],
                },
                f,
            )
            f.flush()

            analyzer = SpecAnalyzer()
            result = analyzer.analyze(f.name)

            assert result is not None
            assert result.metadata.title == "YAML Spec"
            assert len(result.phases) == 1
            assert len(result.requirements) == 1

            Path(f.name).unlink()

    def test_analyze_json_file(self) -> None:
        """Test analyzing a JSON specification file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "title": "JSON Spec",
                    "phases": [{"name": "Phase 1"}],
                    "components": [{"name": "Component A"}],
                },
                f,
            )
            f.flush()

            analyzer = SpecAnalyzer()
            result = analyzer.analyze(f.name)

            assert result is not None
            assert result.metadata.title == "JSON Spec"
            assert len(result.phases) == 1
            assert len(result.components) == 1

            Path(f.name).unlink()

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyzing a nonexistent file."""
        analyzer = SpecAnalyzer()
        with pytest.raises(FileNotFoundError):
            analyzer.analyze("/nonexistent/file.md")
