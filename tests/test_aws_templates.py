"""
Tests for the AWS CI/CD templates.

Tests buildspec.yml, CloudFormation templates, and variable substitution.
"""

import pytest
import yaml
from pathlib import Path
from click.testing import CliRunner
from jinja2 import Template

from lattice_lock_cli.__main__ import cli
from lattice_lock_cli.templates import render_template, TEMPLATES_DIR


# Register CloudFormation tags for YAML parsing
for tag in ['!Ref', '!Sub', '!GetAtt', '!ImportValue']:
    yaml.add_constructor(tag, lambda loader, node: str(node.value), Loader=yaml.SafeLoader)


class TestAWSTemplatesExist:
    """Tests that AWS template files exist."""

    def test_aws_templates_directory_exists(self) -> None:
        """Test that AWS templates directory exists."""
        aws_dir = TEMPLATES_DIR / "ci" / "aws"
        assert aws_dir.exists()
        assert aws_dir.is_dir()

    def test_buildspec_template_exists(self) -> None:
        """Test that buildspec.yml.j2 exists."""
        template_path = TEMPLATES_DIR / "ci" / "aws" / "buildspec.yml.j2"
        assert template_path.exists()

    def test_pipeline_template_exists(self) -> None:
        """Test that pipeline.yml.j2 exists."""
        template_path = TEMPLATES_DIR / "ci" / "aws" / "pipeline.yml.j2"
        assert template_path.exists()

    def test_codebuild_project_template_exists(self) -> None:
        """Test that codebuild-project.yml.j2 exists."""
        template_path = TEMPLATES_DIR / "ci" / "aws" / "codebuild-project.yml.j2"
        assert template_path.exists()


class TestBuildspecTemplate:
    """Tests for buildspec.yml template."""

    def test_buildspec_renders_valid_yaml(self) -> None:
        """Test that buildspec template produces valid YAML."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None

    def test_buildspec_has_required_phases(self) -> None:
        """Test that buildspec has all required phases."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        assert "phases" in parsed
        phases = parsed["phases"]
        assert "install" in phases
        assert "pre_build" in phases
        assert "build" in phases
        assert "post_build" in phases

    def test_buildspec_install_phase_has_python(self) -> None:
        """Test that install phase sets up Python 3.10+."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        install = parsed["phases"]["install"]
        assert "runtime-versions" in install
        assert "python" in install["runtime-versions"]

    def test_buildspec_pre_build_runs_validate(self) -> None:
        """Test that pre_build phase runs lattice-lock validate."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        pre_build_commands = parsed["phases"]["pre_build"]["commands"]
        assert any("lattice-lock validate" in cmd for cmd in pre_build_commands)

    def test_buildspec_build_runs_sheriff_and_gauntlet(self) -> None:
        """Test that build phase runs sheriff and gauntlet."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        build_commands = parsed["phases"]["build"]["commands"]
        assert any("sheriff" in cmd for cmd in build_commands)
        assert any("gauntlet" in cmd for cmd in build_commands)

    def test_buildspec_post_build_runs_pytest(self) -> None:
        """Test that post_build phase runs pytest."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        post_build_commands = parsed["phases"]["post_build"]["commands"]
        assert any("pytest" in cmd for cmd in post_build_commands)

    def test_buildspec_has_artifacts(self) -> None:
        """Test that buildspec defines artifacts."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)
        parsed = yaml.safe_load(output)

        assert "artifacts" in parsed
        assert "files" in parsed["artifacts"]


class TestPipelineTemplate:
    """Tests for pipeline.yml CloudFormation template."""

    def test_pipeline_renders_valid_yaml(self) -> None:
        """Test that pipeline template produces valid YAML."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None

    def test_pipeline_is_valid_cloudformation(self) -> None:
        """Test that pipeline template has CloudFormation structure."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)
        parsed = yaml.safe_load(output)

        assert "AWSTemplateFormatVersion" in parsed
        assert "Resources" in parsed

    def test_pipeline_has_parameters(self) -> None:
        """Test that pipeline template has parameters section."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)
        parsed = yaml.safe_load(output)

        assert "Parameters" in parsed
        params = parsed["Parameters"]
        assert "PipelineName" in params or "RepositoryName" in params

    def test_pipeline_has_source_stage(self) -> None:
        """Test that pipeline has a source stage."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        pipeline_found = False
        for resource_name, resource in resources.items():
            if resource.get("Type") == "AWS::CodePipeline::Pipeline":
                pipeline_found = True
                properties = resource.get("Properties", {})
                stages = properties.get("Stages", [])
                stage_names = [s.get("Name") for s in stages]
                assert "Source" in stage_names

        assert pipeline_found, "No CodePipeline resource found"

    def test_pipeline_has_build_stage(self) -> None:
        """Test that pipeline has a build stage."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        for resource_name, resource in resources.items():
            if resource.get("Type") == "AWS::CodePipeline::Pipeline":
                properties = resource.get("Properties", {})
                stages = properties.get("Stages", [])
                stage_names = [s.get("Name") for s in stages]
                assert "Build" in stage_names

    def test_pipeline_has_iam_role(self) -> None:
        """Test that pipeline defines IAM roles."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        iam_roles = [r for r in resources.values() if r.get("Type") == "AWS::IAM::Role"]
        assert len(iam_roles) > 0, "No IAM roles defined"


class TestCodeBuildProjectTemplate:
    """Tests for codebuild-project.yml CloudFormation template."""

    def test_codebuild_renders_valid_yaml(self) -> None:
        """Test that codebuild template produces valid YAML."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None

    def test_codebuild_is_valid_cloudformation(self) -> None:
        """Test that codebuild template has CloudFormation structure."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)
        parsed = yaml.safe_load(output)

        assert "AWSTemplateFormatVersion" in parsed
        assert "Resources" in parsed

    def test_codebuild_has_project_resource(self) -> None:
        """Test that codebuild template defines a CodeBuild project."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        codebuild_projects = [
            r for r in resources.values()
            if r.get("Type") == "AWS::CodeBuild::Project"
        ]
        assert len(codebuild_projects) > 0, "No CodeBuild project defined"

    def test_codebuild_has_python_environment(self) -> None:
        """Test that codebuild uses Python environment."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        for resource in resources.values():
            if resource.get("Type") == "AWS::CodeBuild::Project":
                properties = resource.get("Properties", {})
                environment = properties.get("Environment", {})
                image = environment.get("Image", "")
                env_vars = environment.get("EnvironmentVariables", [])
                has_python = "python" in image.lower() or any(
                    v.get("Name") == "PYTHON_VERSION" for v in env_vars
                )
                assert has_python or "codebuild/standard" in image

    def test_codebuild_has_service_role(self) -> None:
        """Test that codebuild defines a service role."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        iam_roles = [r for r in resources.values() if r.get("Type") == "AWS::IAM::Role"]
        assert len(iam_roles) > 0, "No IAM service role defined"

    def test_codebuild_has_cache_configuration(self) -> None:
        """Test that codebuild has cache configuration for pip."""
        context = {"project_name": "test_project"}
        output = render_template("ci/aws/codebuild-project.yml.j2", context)
        parsed = yaml.safe_load(output)

        resources = parsed["Resources"]
        for resource in resources.values():
            if resource.get("Type") == "AWS::CodeBuild::Project":
                properties = resource.get("Properties", {})
                cache = properties.get("Cache", {})
                assert "Type" in cache, "No cache configuration"


class TestInitCommandWithAWSCI:
    """Tests for init command with --ci aws flag."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI test runner."""
        return CliRunner()

    def test_init_with_aws_ci_creates_aws_directory(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates ci/aws directory."""
        result = runner.invoke(cli, [
            "init", "my_aws_project",
            "--ci", "aws",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        aws_dir = tmp_path / "my_aws_project" / "ci" / "aws"
        assert aws_dir.exists()
        assert aws_dir.is_dir()

    def test_init_with_aws_ci_creates_buildspec(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates buildspec.yml."""
        result = runner.invoke(cli, [
            "init", "my_aws_project",
            "--ci", "aws",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        buildspec = tmp_path / "my_aws_project" / "ci" / "aws" / "buildspec.yml"
        assert buildspec.exists()

        content = buildspec.read_text()
        parsed = yaml.safe_load(content)
        assert "phases" in parsed

    def test_init_with_aws_ci_creates_pipeline(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates pipeline.yml."""
        result = runner.invoke(cli, [
            "init", "my_aws_project",
            "--ci", "aws",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        pipeline = tmp_path / "my_aws_project" / "ci" / "aws" / "pipeline.yml"
        assert pipeline.exists()

        content = pipeline.read_text()
        parsed = yaml.safe_load(content)
        assert "AWSTemplateFormatVersion" in parsed

    def test_init_with_aws_ci_creates_codebuild_project(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates codebuild-project.yml."""
        result = runner.invoke(cli, [
            "init", "my_aws_project",
            "--ci", "aws",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        codebuild = tmp_path / "my_aws_project" / "ci" / "aws" / "codebuild-project.yml"
        assert codebuild.exists()

        content = codebuild.read_text()
        parsed = yaml.safe_load(content)
        assert "Resources" in parsed

    def test_init_default_ci_is_github(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that default CI provider is github (no aws directory)."""
        result = runner.invoke(cli, [
            "init", "my_default_project",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        github_workflow = tmp_path / "my_default_project" / ".github" / "workflows" / "lattice-lock.yml"
        assert github_workflow.exists()

        aws_dir = tmp_path / "my_default_project" / "ci" / "aws"
        assert not aws_dir.exists()

    def test_init_help_shows_ci_option(self, runner: CliRunner) -> None:
        """Test that init --help shows --ci option."""
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "--ci" in result.output
        assert "github" in result.output
        assert "aws" in result.output

    def test_init_with_aws_ci_still_creates_github_workflow(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws still creates github workflow."""
        result = runner.invoke(cli, [
            "init", "my_aws_project",
            "--ci", "aws",
            "--output-dir", str(tmp_path),
        ])

        assert result.exit_code == 0
        github_workflow = tmp_path / "my_aws_project" / ".github" / "workflows" / "lattice-lock.yml"
        assert github_workflow.exists()
