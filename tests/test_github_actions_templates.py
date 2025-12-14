import pytest
import yaml
from pathlib import Path
from lattice_lock_cli.templates import render_template

TEMPLATE_DIR = Path(__file__).parents[1] / "src" / "lattice_lock_cli" / "templates" / "ci" / "github_actions"

def test_lattice_lock_workflow_renders_valid_yaml():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/lattice-lock.yml.j2", context)

    # Check if valid YAML
    data = yaml.safe_load(rendered)
    assert data["name"] == "Lattice Lock Validation"
    assert "push" in data["on"]
    assert "pull_request" in data["on"]

def test_lattice_lock_workflow_steps():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/lattice-lock.yml.j2", context)

    assert "lattice-lock validate" in rendered
    assert "lattice-lock sheriff src/" in rendered
    assert "lattice-lock gauntlet" in rendered
    assert "pytest tests/" in rendered

def test_validate_only_workflow_renders_valid_yaml():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/validate-only.yml.j2", context)

    # Check if valid YAML
    data = yaml.safe_load(rendered)
    assert data["name"] == "Lattice Lock Quick Validation"
    assert "pull_request" in data["on"]
    assert "push" not in data["on"]

def test_validate_only_workflow_steps():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/validate-only.yml.j2", context)

    assert "lattice-lock validate" in rendered
    assert "lattice-lock sheriff src/" in rendered
    assert "lattice-lock gauntlet" not in rendered # Should not be in validate-only

def test_full_pipeline_workflow_renders_valid_yaml():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/full-pipeline.yml.j2", context)

    # Check if valid YAML
    data = yaml.safe_load(rendered)
    assert data["name"] == "Lattice Lock Full Pipeline"

def test_full_pipeline_workflow_steps():
    context = {"project_name": "test_project"}
    rendered = render_template("ci/github_actions/full-pipeline.yml.j2", context)

    assert "lattice-lock validate" in rendered
    assert "lattice-lock sheriff src/" in rendered
    assert "lattice-lock gauntlet" in rendered
    assert "pytest tests/" in rendered
    assert "codecov/codecov-action" in rendered
    assert "actions/upload-artifact" in rendered

def test_variable_substitution():
    context = {"project_name": "my_custom_project"}
    rendered = render_template("ci/github_actions/lattice-lock.yml.j2", context)

    assert "# Generated for: my_custom_project" in rendered
