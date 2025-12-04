"""
Tests for the Lattice Lock CLI templates.

Tests template loading, rendering, and output validation.
"""

import pytest
import yaml

from lattice_lock_cli.templates import (
    get_template,
    render_template,
    get_templates_for_type,
    TEMPLATES_DIR,
)


class TestTemplateLoader:
    """Tests for template loading functionality."""

    def test_templates_directory_exists(self) -> None:
        """Test that templates directory exists."""
        assert TEMPLATES_DIR.exists()
        assert TEMPLATES_DIR.is_dir()

    def test_get_template_base_lattice(self) -> None:
        """Test loading base/lattice.yaml.j2 template."""
        template = get_template("base/lattice.yaml.j2")
        assert template is not None
        assert hasattr(template, "render")

    def test_get_template_base_readme(self) -> None:
        """Test loading base/readme.md.j2 template."""
        template = get_template("base/readme.md.j2")
        assert template is not None

    def test_get_template_base_gitignore(self) -> None:
        """Test loading base/gitignore.j2 template."""
        template = get_template("base/gitignore.j2")
        assert template is not None

    def test_get_template_ci_workflow(self) -> None:
        """Test loading ci/github_workflow.yml.j2 template."""
        template = get_template("ci/github_workflow.yml.j2")
        assert template is not None

    def test_get_template_agent(self) -> None:
        """Test loading agent/agent_definition.yaml.j2 template."""
        template = get_template("agent/agent_definition.yaml.j2")
        assert template is not None

    def test_get_template_service(self) -> None:
        """Test loading service/service_scaffold.py.j2 template."""
        template = get_template("service/service_scaffold.py.j2")
        assert template is not None

    def test_get_template_library(self) -> None:
        """Test loading library/lib_init.py.j2 template."""
        template = get_template("library/lib_init.py.j2")
        assert template is not None

    def test_get_nonexistent_template_raises_error(self) -> None:
        """Test that loading nonexistent template raises error."""
        with pytest.raises(Exception):
            get_template("nonexistent/template.j2")


class TestTemplateRendering:
    """Tests for template rendering functionality."""

    def test_render_lattice_yaml(self) -> None:
        """Test rendering lattice.yaml template."""
        context = {
            "project_name": "test_project",
            "project_type": "service",
            "description": "A test project",
        }
        output = render_template("base/lattice.yaml.j2", context)

        assert "test_project" in output
        assert "service" in output
        # Verify it's valid YAML
        parsed = yaml.safe_load(output)
        assert parsed["project"]["name"] == "test_project"

    def test_render_readme(self) -> None:
        """Test rendering readme.md template."""
        context = {
            "project_name": "my_project",
            "description": "An awesome project",
        }
        output = render_template("base/readme.md.j2", context)

        assert "# my_project" in output
        assert "An awesome project" in output
        assert "Lattice Lock" in output

    def test_render_gitignore(self) -> None:
        """Test rendering gitignore template."""
        context = {"project_name": "test_project"}
        output = render_template("base/gitignore.j2", context)

        assert "__pycache__" in output
        assert ".env" in output
        assert "venv/" in output

    def test_render_github_workflow(self) -> None:
        """Test rendering GitHub workflow template."""
        context = {"project_name": "test_project"}
        output = render_template("ci/github_workflow.yml.j2", context)

        assert "Lattice Lock" in output
        assert "pytest" in output
        assert "validate" in output
        # Verify it's valid YAML
        parsed = yaml.safe_load(output)
        assert "jobs" in parsed

    def test_render_agent_definition(self) -> None:
        """Test rendering agent definition template."""
        context = {
            "project_name": "my_agent",
            "description": "An AI agent",
        }
        output = render_template("agent/agent_definition.yaml.j2", context)

        assert "my_agent" in output
        assert "capabilities" in output
        # Verify it's valid YAML
        parsed = yaml.safe_load(output)
        assert "agent" in parsed

    def test_render_service_scaffold(self) -> None:
        """Test rendering service scaffold template."""
        context = {"project_name": "my_service"}
        output = render_template("service/service_scaffold.py.j2", context)

        assert "my_service" in output
        assert "class" in output
        assert "def " in output
        # Basic Python syntax check - should compile
        compile(output, "<string>", "exec")

    def test_render_library_init(self) -> None:
        """Test rendering library init template."""
        context = {"project_name": "my_library"}
        output = render_template("library/lib_init.py.j2", context)

        assert "__version__" in output
        assert "my_library" in output
        # Basic Python syntax check - should compile
        compile(output, "<string>", "exec")

    def test_render_with_default_description(self) -> None:
        """Test that templates have sensible defaults."""
        context = {"project_name": "test_project", "project_type": "service"}
        output = render_template("base/lattice.yaml.j2", context)

        # Should not have empty description
        assert '""' not in output or "Lattice Lock" in output


class TestTemplatesForType:
    """Tests for get_templates_for_type function."""

    def test_service_templates(self) -> None:
        """Test that service type returns correct templates."""
        templates = get_templates_for_type("service")

        assert "base/lattice.yaml.j2" in templates
        assert "base/readme.md.j2" in templates
        assert "base/gitignore.j2" in templates
        assert "ci/github_workflow.yml.j2" in templates
        assert "service/service_scaffold.py.j2" in templates
        assert "agent/agent_definition.yaml.j2" not in templates

    def test_agent_templates(self) -> None:
        """Test that agent type returns correct templates."""
        templates = get_templates_for_type("agent")

        assert "base/lattice.yaml.j2" in templates
        assert "agent/agent_definition.yaml.j2" in templates
        assert "service/service_scaffold.py.j2" not in templates

    def test_library_templates(self) -> None:
        """Test that library type returns correct templates."""
        templates = get_templates_for_type("library")

        assert "base/lattice.yaml.j2" in templates
        assert "library/lib_init.py.j2" in templates
        assert "service/service_scaffold.py.j2" not in templates

    def test_unknown_type_returns_base_only(self) -> None:
        """Test that unknown type returns only base templates."""
        templates = get_templates_for_type("unknown")

        assert "base/lattice.yaml.j2" in templates
        assert "base/readme.md.j2" in templates
        # Should not have any type-specific templates
        assert len([t for t in templates if "agent/" in t or "service/" in t or "library/" in t]) == 0


class TestTemplateOutput:
    """Tests for template output validity."""

    def test_all_yaml_templates_produce_valid_yaml(self) -> None:
        """Test that all YAML templates produce valid YAML output."""
        context = {
            "project_name": "test_project",
            "project_type": "service",
            "description": "Test description",
        }

        yaml_templates = [
            "base/lattice.yaml.j2",
            "ci/github_workflow.yml.j2",
            "agent/agent_definition.yaml.j2",
        ]

        for template_name in yaml_templates:
            output = render_template(template_name, context)
            try:
                yaml.safe_load(output)
            except yaml.YAMLError as e:
                pytest.fail(f"Template {template_name} produced invalid YAML: {e}")

    def test_all_python_templates_produce_valid_python(self) -> None:
        """Test that all Python templates produce valid Python output."""
        context = {
            "project_name": "test_project",
            "author": "Test Author",
        }

        python_templates = [
            "service/service_scaffold.py.j2",
            "library/lib_init.py.j2",
        ]

        for template_name in python_templates:
            output = render_template(template_name, context)
            try:
                compile(output, f"<{template_name}>", "exec")
            except SyntaxError as e:
                pytest.fail(f"Template {template_name} produced invalid Python: {e}")
