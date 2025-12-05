import pytest
import json
import yaml
from pathlib import Path
from lattice_lock_agents.prompt_architect.subagents.spec_analyzer import SpecAnalyzer
from lattice_lock_agents.prompt_architect.models import SpecificationAnalysis

@pytest.fixture
def sample_markdown_spec(tmp_path):
    content = """
# Project Alpha

## Phase 1: Inception
Start the project.

## Requirements
- The system must be fast.
- The UI should be responsive.
"""
    f = tmp_path / "spec.md"
    f.write_text(content)
    return str(f)

@pytest.fixture
def sample_yaml_spec(tmp_path):
    content = """
project_name: Project Beta
phases:
  - name: Phase 1
    description: Init
requirements:
  - description: Must be secure
"""
    f = tmp_path / "spec.yaml"
    f.write_text(content)
    return str(f)

def test_analyze_markdown(sample_markdown_spec):
    analyzer = SpecAnalyzer()
    result = analyzer.analyze(sample_markdown_spec)
    assert isinstance(result, SpecificationAnalysis)
    assert result.project_name == "Project Alpha"
    assert len(result.phases) == 1
    assert result.phases[0].name == "Phase 1: Inception"
    assert len(result.requirements) == 2

def test_analyze_yaml(sample_yaml_spec):
    analyzer = SpecAnalyzer()
    result = analyzer.analyze(sample_yaml_spec)
    assert isinstance(result, SpecificationAnalysis)
    assert result.project_name == "Project Beta"
    assert len(result.phases) == 1
    assert len(result.requirements) == 1

def test_file_not_found():
    analyzer = SpecAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.analyze("non_existent.md")

def test_unsupported_format(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("content")
    analyzer = SpecAnalyzer()
    with pytest.raises(ValueError):
        analyzer.analyze(str(f))
