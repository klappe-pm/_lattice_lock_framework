"""
Tests for AWS CodePipeline and CodeBuild templates.

Tests template loading, rendering, and CloudFormation validity.
"""

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from lattice_lock.cli.__main__ import cli
from lattice_lock.cli.templates import TEMPLATES_DIR, get_template, render_template


def get_cfn_loader():
    """Get a YAML loader that handles CloudFormation intrinsic functions."""
    loader = yaml.SafeLoader

    cfn_tags = [
        "!Sub",
        "!Ref",
        "!GetAtt",
        "!Join",
        "!Select",
        "!Split",
        "!If",
        "!Not",
        "!Equals",
        "!And",
        "!Or",
        "!Condition",
        "!Base64",
        "!Cidr",
        "!FindInMap",
        "!GetAZs",
        "!ImportValue",
        "!Transform",
    ]

    def cfn_constructor(loader, node):
        if isinstance(node, yaml.ScalarNode):
            return loader.construct_scalar(node)
        elif isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        elif isinstance(node, yaml.MappingNode):
            return loader.construct_mapping(node)
        return None

    for tag in cfn_tags:
        loader.add_constructor(tag, cfn_constructor)

    return loader


def cfn_safe_load(content: str):
    """Load YAML content with CloudFormation intrinsic function support."""
    return yaml.load(content, Loader=get_cfn_loader())


class TestAWSTemplateLoading:
    """Tests for AWS template loading."""

    def test_load_buildspec_template(self) -> None:
        """Test loading buildspec.yml.j2 template."""
        template = get_template("ci/aws/buildspec.yml.j2")
        assert template is not None
        assert hasattr(template, "render")

    def test_load_pipeline_template(self) -> None:
        """Test loading pipeline.yml.j2 template."""
        template = get_template("ci/aws/pipeline.yml.j2")
        assert template is not None
        assert hasattr(template, "render")

    def test_load_codebuild_project_template(self) -> None:
        """Test loading codebuild_project.yml.j2 template."""
        template = get_template("ci/aws/codebuild_project.yml.j2")
        assert template is not None
        assert hasattr(template, "render")


class TestBuildspecTemplate:
    """Tests for AWS CodeBuild buildspec template."""

    def test_render_buildspec_produces_valid_yaml(self) -> None:
        """Test that buildspec template produces valid YAML."""
        context = {
            "project_name": "test-project",
            "python_version": "3.11",
        }
        output = render_template("ci/aws/buildspec.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert parsed is not None
        assert "version" in parsed
        assert parsed["version"] == 0.2

    def test_buildspec_has_required_phases(self) -> None:
        """Test that buildspec has all required phases."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        parsed = yaml.safe_load(output)
        phases = parsed.get("phases", {})

        assert "install" in phases
        assert "pre_build" in phases
        assert "build" in phases
        assert "post_build" in phases

    def test_buildspec_installs_lattice_lock(self) -> None:
        """Test that buildspec installs lattice-lock package."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        assert "lattice-lock" in output
        assert "pip install" in output

    def test_buildspec_runs_validation(self) -> None:
        """Test that buildspec runs lattice-lock validation."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        assert "lattice-lock validate" in output

    def test_buildspec_runs_sheriff_and_gauntlet(self) -> None:
        """Test that buildspec runs sheriff and gauntlet checks."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        assert "lattice-lock sheriff" in output
        assert "lattice-lock gauntlet" in output

    def test_buildspec_runs_pytest(self) -> None:
        """Test that buildspec runs pytest."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        assert "pytest" in output

    def test_buildspec_has_reports_section(self) -> None:
        """Test that buildspec has reports configuration."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert "reports" in parsed

    def test_buildspec_has_cache_section(self) -> None:
        """Test that buildspec has cache configuration."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/buildspec.yml.j2", context)

        parsed = yaml.safe_load(output)
        assert "cache" in parsed

    def test_buildspec_variable_substitution(self) -> None:
        """Test that buildspec substitutes variables correctly."""
        context = {
            "project_name": "my-custom-project",
            "python_version": "3.12",
        }
        output = render_template("ci/aws/buildspec.yml.j2", context)

        assert "3.12" in output


class TestPipelineTemplate:
    """Tests for AWS CodePipeline CloudFormation template."""

    def test_render_pipeline_produces_valid_yaml(self) -> None:
        """Test that pipeline template produces valid YAML."""
        context = {
            "project_name": "test-project",
            "repository_name": "test-repo",
            "branch_name": "main",
        }
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert parsed is not None

    def test_pipeline_has_cloudformation_version(self) -> None:
        """Test that pipeline template has AWSTemplateFormatVersion."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "AWSTemplateFormatVersion" in parsed
        assert parsed["AWSTemplateFormatVersion"] == "2010-09-09"

    def test_pipeline_has_parameters(self) -> None:
        """Test that pipeline template has Parameters section."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "Parameters" in parsed
        params = parsed["Parameters"]
        assert "ProjectName" in params
        assert "RepositoryName" in params
        assert "BranchName" in params

    def test_pipeline_has_resources(self) -> None:
        """Test that pipeline template has required resources."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "Resources" in parsed
        resources = parsed["Resources"]
        assert "ArtifactBucket" in resources
        assert "PipelineRole" in resources
        assert "Pipeline" in resources

    def test_pipeline_has_outputs(self) -> None:
        """Test that pipeline template has Outputs section."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/pipeline.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "Outputs" in parsed

    def test_pipeline_variable_substitution(self) -> None:
        """Test that pipeline substitutes variables correctly."""
        context = {
            "project_name": "my-custom-project",
            "repository_name": "my-repo",
            "branch_name": "develop",
        }
        output = render_template("ci/aws/pipeline.yml.j2", context)

        assert "my-custom-project" in output
        assert "my-repo" in output
        assert "develop" in output


class TestCodeBuildProjectTemplate:
    """Tests for AWS CodeBuild project CloudFormation template."""

    def test_render_codebuild_produces_valid_yaml(self) -> None:
        """Test that codebuild template produces valid YAML."""
        context = {
            "project_name": "test-project",
            "python_version": "3.11",
        }
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert parsed is not None

    def test_codebuild_has_cloudformation_version(self) -> None:
        """Test that codebuild template has AWSTemplateFormatVersion."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "AWSTemplateFormatVersion" in parsed

    def test_codebuild_has_service_role(self) -> None:
        """Test that codebuild template has IAM service role."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        resources = parsed.get("Resources", {})
        assert "CodeBuildServiceRole" in resources

    def test_codebuild_has_project_resource(self) -> None:
        """Test that codebuild template has CodeBuild project resource."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        resources = parsed.get("Resources", {})
        assert "CodeBuildProject" in resources

    def test_codebuild_has_log_group(self) -> None:
        """Test that codebuild template has CloudWatch log group."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        resources = parsed.get("Resources", {})
        assert "BuildLogGroup" in resources

    def test_codebuild_has_outputs(self) -> None:
        """Test that codebuild template has Outputs section."""
        context = {"project_name": "test-project"}
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        parsed = cfn_safe_load(output)
        assert "Outputs" in parsed
        outputs = parsed["Outputs"]
        assert "CodeBuildProjectArn" in outputs

    def test_codebuild_variable_substitution(self) -> None:
        """Test that codebuild substitutes variables correctly."""
        context = {
            "project_name": "my-custom-project",
            "python_version": "3.12",
        }
        output = render_template("ci/aws/codebuild_project.yml.j2", context)

        assert "my-custom-project" in output


class TestAWSTemplateIntegration:
    """Integration tests for AWS templates working together."""

    def test_all_aws_templates_render_with_same_context(self) -> None:
        """Test that all AWS templates render with the same context."""
        context = {
            "project_name": "integration-test-project",
            "repository_name": "integration-repo",
            "branch_name": "main",
            "python_version": "3.11",
        }

        templates = [
            "ci/aws/buildspec.yml.j2",
            "ci/aws/pipeline.yml.j2",
            "ci/aws/codebuild_project.yml.j2",
        ]

        for template_name in templates:
            output = render_template(template_name, context)
            try:
                cfn_safe_load(output)
            except yaml.YAMLError as e:
                pytest.fail(f"Template {template_name} produced invalid YAML: {e}")

    def test_aws_templates_use_consistent_naming(self) -> None:
        """Test that AWS templates use consistent project naming."""
        context = {
            "project_name": "consistent-naming-test",
            "repository_name": "test-repo",
            "branch_name": "main",
            "python_version": "3.11",
        }

        pipeline_output = render_template("ci/aws/pipeline.yml.j2", context)
        codebuild_output = render_template("ci/aws/codebuild_project.yml.j2", context)

        assert "consistent-naming-test" in pipeline_output
        assert "consistent-naming-test" in codebuild_output


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
        """Test that codebuild_project.yml.j2 exists."""
        template_path = TEMPLATES_DIR / "ci" / "aws" / "codebuild_project.yml.j2"
        assert template_path.exists()


class TestInitCommandWithAWSCI:
    """Tests for init command with --ci aws flag."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI test runner."""
        return CliRunner()

    def test_init_with_aws_ci_creates_aws_directory(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that --ci aws creates ci/aws directory."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_aws_project",
                "--ci",
                "aws",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        aws_dir = tmp_path / "my_aws_project" / "ci" / "aws"
        assert aws_dir.exists()
        assert aws_dir.is_dir()

    def test_init_with_aws_ci_creates_buildspec(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates buildspec.yml."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_aws_project",
                "--ci",
                "aws",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        buildspec = tmp_path / "my_aws_project" / "ci" / "aws" / "buildspec.yml"
        assert buildspec.exists()

        content = buildspec.read_text()
        parsed = yaml.safe_load(content)
        assert "phases" in parsed

    def test_init_with_aws_ci_creates_pipeline(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --ci aws creates pipeline.yml."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_aws_project",
                "--ci",
                "aws",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        pipeline = tmp_path / "my_aws_project" / "ci" / "aws" / "pipeline.yml"
        assert pipeline.exists()

        content = pipeline.read_text()
        parsed = cfn_safe_load(content)
        assert "AWSTemplateFormatVersion" in parsed

    def test_init_with_aws_ci_creates_codebuild_project(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that --ci aws creates codebuild-project.yml."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_aws_project",
                "--ci",
                "aws",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        codebuild = tmp_path / "my_aws_project" / "ci" / "aws" / "codebuild-project.yml"
        assert codebuild.exists()

        content = codebuild.read_text()
        parsed = cfn_safe_load(content)
        assert "Resources" in parsed

    def test_init_default_ci_is_github(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that default CI provider is github (no aws directory)."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_default_project",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        github_workflow = (
            tmp_path / "my_default_project" / ".github" / "workflows" / "lattice-lock.yml"
        )
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

    def test_init_with_aws_ci_still_creates_github_workflow(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that --ci aws still creates github workflow."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_aws_project",
                "--ci",
                "aws",
                "--output-dir",
                str(tmp_path),
            ],
            input="\n",  # Skip GitHub repo prompt
        )

        assert result.exit_code == 0
        github_workflow = tmp_path / "my_aws_project" / ".github" / "workflows" / "lattice-lock.yml"
        assert github_workflow.exists()
