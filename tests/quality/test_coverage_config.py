"""Validate coverage configuration meets standards."""

import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@pytest.mark.quality
class TestCoverageConfiguration:
    """Test coverage configuration in pyproject.toml."""

    @pytest.fixture
    def pyproject_config(self, pyproject_path):
        """Load pyproject.toml configuration."""
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)

    def test_coverage_target_is_90_percent(self, pyproject_config):
        """Coverage target should be 90% as defined in Testing Program Plan."""
        coverage_report = pyproject_config.get("tool", {}).get("coverage", {}).get("report", {})
        fail_under = coverage_report.get("fail_under", 0)

        assert fail_under == 90, (
            f"Coverage target should be 90% (Testing Program Plan requirement), "
            f"got {fail_under}%"
        )

    def test_pytest_coverage_flag(self, pyproject_config):
        """pytest addopts should enforce 90% coverage."""
        pytest_opts = pyproject_config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        addopts = pytest_opts.get("addopts", "")

        assert "--cov-fail-under=90" in addopts, "pytest addopts should include --cov-fail-under=90"

    def test_branch_coverage_enabled(self, pyproject_config):
        """Branch coverage should be enabled."""
        coverage_run = pyproject_config.get("tool", {}).get("coverage", {}).get("run", {})
        branch = coverage_run.get("branch", False)

        assert branch is True, "Branch coverage should be enabled"

    def test_coverage_source_configured(self, pyproject_config):
        """Coverage source should be configured."""
        coverage_run = pyproject_config.get("tool", {}).get("coverage", {}).get("run", {})
        source = coverage_run.get("source", [])

        assert source, "Coverage source should be configured"
        assert any(
            "lattice_lock" in s for s in source
        ), "Coverage source should include lattice_lock"


@pytest.mark.quality
class TestTestMarkers:
    """Test that required test markers are defined."""

    REQUIRED_MARKERS = [
        "critical",
        "unit",
        "integration",
        "documentation",
        "agent",
        "approver",
        "security",
    ]

    @pytest.fixture
    def pyproject_config(self, pyproject_path):
        """Load pyproject.toml configuration."""
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)

    def test_required_markers_defined(self, pyproject_config):
        """All required test markers should be defined."""
        pytest_opts = pyproject_config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        markers = pytest_opts.get("markers", [])
        marker_names = [m.split(":")[0].strip() for m in markers]

        missing = [m for m in self.REQUIRED_MARKERS if m not in marker_names]

        assert not missing, f"Missing required markers: {missing}"
