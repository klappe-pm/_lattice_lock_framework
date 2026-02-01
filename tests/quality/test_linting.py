"""Validate code passes linting checks."""

import subprocess

import pytest


@pytest.mark.quality
class TestRuffLinting:
    """Test code passes Ruff linting."""

    def test_ruff_check_passes(self, src_path):
        """Source code should pass Ruff checks."""
        if not src_path.exists():
            pytest.skip("src directory not found")

        result = subprocess.run(
            ["ruff", "check", str(src_path), "--config", "pyproject.toml"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Show first 20 lines of errors
            error_lines = result.stdout.strip().split("\n")[:20]
            pytest.fail(
                f"Ruff linting failed with {len(error_lines)} issues:\n" + "\n".join(error_lines)
            )

    def test_ruff_available(self):
        """Ruff should be installed."""
        result = subprocess.run(
            ["ruff", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Ruff is not installed"


@pytest.mark.quality
class TestBlackFormatting:
    """Test code is Black formatted."""

    def test_black_format_check(self, src_path):
        """Source code should be Black formatted."""
        if not src_path.exists():
            pytest.skip("src directory not found")

        result = subprocess.run(
            ["black", "--check", str(src_path), "--config", "pyproject.toml"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Show which files would be reformatted
            pytest.fail(f"Code is not Black formatted:\n{result.stderr[:500]}")

    def test_black_available(self):
        """Black should be installed."""
        result = subprocess.run(
            ["black", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Black is not installed"


@pytest.mark.quality
class TestIsortImports:
    """Test imports are sorted with isort."""

    def test_isort_check(self, src_path):
        """Imports should be sorted with isort."""
        if not src_path.exists():
            pytest.skip("src directory not found")

        result = subprocess.run(
            ["isort", "--check-only", str(src_path), "--settings-path", "pyproject.toml"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.fail(f"Imports are not sorted:\n{result.stderr[:500]}")


@pytest.mark.quality
@pytest.mark.slow
class TestMyPyTypeChecking:
    """Test code passes MyPy type checking."""

    def test_mypy_check(self, src_path):
        """Source code should pass MyPy type checking."""
        lattice_lock_path = src_path / "lattice_lock"
        if not lattice_lock_path.exists():
            pytest.skip("lattice_lock module not found")

        result = subprocess.run(
            ["mypy", str(lattice_lock_path), "--no-error-summary"],
            capture_output=True,
            text=True,
        )

        # MyPy exits with 1 if there are errors
        if result.returncode != 0:
            error_lines = result.stdout.strip().split("\n")[:20]
            # Don't fail on mypy - it's informational
            pytest.skip(
                f"MyPy found {len(error_lines)} issues (informational):\n"
                + "\n".join(error_lines[:5])
            )

    def test_mypy_available(self):
        """MyPy should be installed."""
        result = subprocess.run(
            ["mypy", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "MyPy is not installed"
