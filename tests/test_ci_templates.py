from pathlib import Path

TEMPLATES_DIR = Path("src/lattice_lock_cli/templates/ci")


def test_github_actions_hardening():
    """Verify GitHub Actions template contains security audit."""
    template_path = TEMPLATES_DIR / "github_actions/lattice-lock.yml.j2"
    assert template_path.exists()
    content = template_path.read_text()
    assert "pip-audit" in content
    assert "Security Audit" in content


def test_gcp_cloudbuild_hardening():
    """Verify GCP Cloud Build template contains security audit."""
    template_path = TEMPLATES_DIR / "gcp/cloudbuild.yaml.j2"
    assert template_path.exists()
    content = template_path.read_text()
    assert "pip-audit" in content
    assert "Security Audit" in content


def test_aws_buildspec_hardening():
    """Verify AWS Buildspec template contains security audit."""
    template_path = TEMPLATES_DIR / "aws/buildspec.yml.j2"
    assert template_path.exists()
    content = template_path.read_text()
    assert "pip-audit" in content
    assert "Security Audit" in content
