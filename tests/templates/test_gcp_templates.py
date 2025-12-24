"""
Tests for GCP Cloud Build templates.

Tests template loading, rendering, and YAML validity.
"""

import pytest
import yaml

from lattice_lock.cli.templates import get_template, render_template


class TestGCPTemplateLoading:
    """Tests for GCP template loading."""

    def test_load_cloudbuild_template(self) -> None:
        """Test loading cloudbuild.yaml.j2 template."""
        template = get_template("ci/gcp/cloudbuild.yaml.j2")
        assert template is not None
        assert hasattr(template, "render")

    def test_load_cloudbuild_pr_template(self) -> None:
        """Test loading cloudbuild_pr.yaml.j2 template."""
        template = get_template("ci/gcp/cloudbuild_pr.yaml.j2")
        assert template is not None
        assert hasattr(template, "render")

    def test_load_trigger_config_template(self) -> None:
        """Test loading trigger_config.yaml.j2 template."""
        template = get_template("ci/gcp/trigger_config.yaml.j2")
        assert template is not None
        assert hasattr(template, "render")


class TestCloudBuildTemplate:
    """Tests for GCP Cloud Build main template."""

    def test_render_cloudbuild_produces_valid_yaml(self) -> None:
        """Test that cloudbuild template produces valid YAML."""
        context = {
            "project_name": "test-project",
            "python_version": "3.11",
        }
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None
        assert "steps" in parsed

    def test_cloudbuild_has_required_steps(self) -> None:
        """Test that cloudbuild has all required steps."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        parsed = yaml.safe_load(output)
        steps = parsed.get("steps", [])

        step_ids = [step.get("id") for step in steps]
        assert "install-dependencies" in step_ids
        assert "validate-schema" in step_ids
        assert "run-sheriff" in step_ids
        assert "run-gauntlet" in step_ids
        assert "run-tests" in step_ids

    def test_cloudbuild_installs_lattice_lock(self) -> None:
        """Test that cloudbuild installs lattice-lock package."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        assert "lattice-lock" in output

    def test_cloudbuild_has_artifacts(self) -> None:
        """Test that cloudbuild has artifacts configuration."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert "artifacts" in parsed

    def test_cloudbuild_has_timeout(self) -> None:
        """Test that cloudbuild has timeout configuration."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert "timeout" in parsed

    def test_cloudbuild_has_tags(self) -> None:
        """Test that cloudbuild has tags for filtering."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert "tags" in parsed
        assert "lattice-lock" in parsed["tags"]

    def test_cloudbuild_variable_substitution(self) -> None:
        """Test that cloudbuild substitutes variables correctly."""
        context = {
            "project_name": "my-custom-project",
            "python_version": "3.12",
        }
        output = render_template("ci/gcp/cloudbuild.yaml.j2", context)

        assert "my-custom-project" in output
        assert "3.12" in output


class TestCloudBuildPRTemplate:
    """Tests for GCP Cloud Build PR validation template."""

    def test_render_cloudbuild_pr_produces_valid_yaml(self) -> None:
        """Test that cloudbuild-pr template produces valid YAML."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild_pr.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None
        assert "steps" in parsed

    def test_cloudbuild_pr_is_lightweight(self) -> None:
        """Test that PR build has fewer steps than main build."""
        context = {"project_name": "test-project"}

        main_output = render_template("ci/gcp/cloudbuild.yaml.j2", context)
        pr_output = render_template("ci/gcp/cloudbuild_pr.yaml.j2", context)

        main_parsed = yaml.safe_load(main_output)
        pr_parsed = yaml.safe_load(pr_output)

        assert len(pr_parsed["steps"]) < len(main_parsed["steps"])

    def test_cloudbuild_pr_has_shorter_timeout(self) -> None:
        """Test that PR build has shorter timeout."""
        context = {"project_name": "test-project"}

        main_output = render_template("ci/gcp/cloudbuild.yaml.j2", context)
        pr_output = render_template("ci/gcp/cloudbuild_pr.yaml.j2", context)

        main_parsed = yaml.safe_load(main_output)
        pr_parsed = yaml.safe_load(pr_output)

        main_timeout = int(main_parsed["timeout"].rstrip("s"))
        pr_timeout = int(pr_parsed["timeout"].rstrip("s"))

        assert pr_timeout < main_timeout

    def test_cloudbuild_pr_has_pr_tag(self) -> None:
        """Test that PR build has pr-validation tag."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/cloudbuild_pr.yaml.j2", context)

        parsed = yaml.safe_load(output)
        assert "pr-validation" in parsed["tags"]


class TestTriggerConfigTemplate:
    """Tests for GCP Cloud Build trigger configuration template."""

    def test_render_trigger_config_produces_valid_yaml(self) -> None:
        """Test that trigger-config template produces valid YAML."""
        context = {
            "project_name": "test-project",
            "github_owner": "test-owner",
            "repository_name": "test-repo",
        }
        output = render_template("ci/gcp/trigger_config.yaml.j2", context)

        docs = list(yaml.safe_load_all(output))
        assert len(docs) >= 1
        assert docs[0] is not None

    def test_trigger_config_has_github_section(self) -> None:
        """Test that trigger config has GitHub configuration."""
        context = {"project_name": "test-project"}
        output = render_template("ci/gcp/trigger_config.yaml.j2", context)

        docs = list(yaml.safe_load_all(output))
        assert "github" in docs[0]

    def test_trigger_config_variable_substitution(self) -> None:
        """Test that trigger config substitutes variables correctly."""
        context = {
            "project_name": "my-custom-project",
            "github_owner": "my-org",
            "repository_name": "my-repo",
        }
        output = render_template("ci/gcp/trigger_config.yaml.j2", context)

        assert "my-custom-project" in output
        assert "my-org" in output
        assert "my-repo" in output


class TestGCPTemplateIntegration:
    """Integration tests for GCP templates working together."""

    def test_all_gcp_templates_render_with_same_context(self) -> None:
        """Test that all GCP templates render with the same context."""
        context = {
            "project_name": "integration-test-project",
            "python_version": "3.11",
            "github_owner": "test-owner",
            "repository_name": "test-repo",
        }

        templates = [
            "ci/gcp/cloudbuild.yaml.j2",
            "ci/gcp/cloudbuild_pr.yaml.j2",
            "ci/gcp/trigger_config.yaml.j2",
        ]

        for template_name in templates:
            output = render_template(template_name, context)
            try:
                list(yaml.safe_load_all(output))
            except yaml.YAMLError as e:
                pytest.fail(f"Template {template_name} produced invalid YAML: {e}")

    def test_gcp_templates_use_consistent_naming(self) -> None:
        """Test that GCP templates use consistent project naming."""
        context = {
            "project_name": "consistent-naming-test",
            "python_version": "3.11",
        }

        cloudbuild_output = render_template("ci/gcp/cloudbuild.yaml.j2", context)
        pr_output = render_template("ci/gcp/cloudbuild_pr.yaml.j2", context)

        assert "consistent-naming-test" in cloudbuild_output
        assert "consistent-naming-test" in pr_output
