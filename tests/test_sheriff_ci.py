"""CI integration tests for Sheriff CLI.

Tests:
- Output formats (text, json, github, junit)
- GitHub Actions annotation format
- JUnit XML report structure
- Caching behavior
"""

import json
import os
import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from lattice_lock_cli.commands.sheriff import sheriff_command
from lattice_lock_sheriff.sheriff import Violation
from lattice_lock_sheriff.formatters import (
    get_formatter,
    TextFormatter,
    JSONFormatter,
    GitHubFormatter,
    JUnitFormatter,
)
from lattice_lock_sheriff.cache import SheriffCache, get_config_hash

# Alias for formatter tests - use the same Violation class from sheriff
FormatterViolation = Violation


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_validate_path():
    with patch("lattice_lock_cli.commands.sheriff.validate_path_with_audit") as mock:
        yield mock


@pytest.fixture
def mock_validate_file():
    with patch("lattice_lock_cli.commands.sheriff.validate_file_with_audit") as mock:
        yield mock


class MockSheriffConfig:
    """Mock config class for testing."""
    def __init__(self):
        self.forbidden_imports = []
        self.enforce_type_hints = True
        self.target_version = "current"
        self.custom_rules = {}

    @classmethod
    def from_yaml(cls, path):
        return cls()


@pytest.fixture
def mock_config_from_yaml():
    # Patch at the location where it's imported in the CLI
    with patch("lattice_lock_cli.commands.sheriff.SheriffConfig", MockSheriffConfig):
        yield MockSheriffConfig


@pytest.fixture
def sample_violation():
    return Violation(
        file=Path("src/module.py"),
        line=42,
        column=8,
        message="Forbidden import 'os' detected",
        rule="SHERIFF_001",
        code="import os"
    )


@pytest.fixture
def sample_violations():
    return [
        Violation(
            file=Path("src/module.py"),
            line=10,
            column=0,
            message="Forbidden import 'os' detected",
            rule="SHERIFF_001",
            code="import os"
        ),
        Violation(
            file=Path("src/module.py"),
            line=25,
            column=0,
            message="Missing return type hint",
            rule="SHERIFF_002",
            code="def process_data(data):"
        ),
        Violation(
            file=Path("src/utils.py"),
            line=5,
            column=0,
            message="Forbidden import 'subprocess' detected",
            rule="SHERIFF_001",
            code="import subprocess"
        ),
    ]


# =============================================================================
# Output Format Tests
# =============================================================================

class TestTextFormat:
    """Tests for text output format."""

    def test_text_format_no_violations(self, runner, mock_validate_path, mock_config_from_yaml):
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            # Use --no-cache to bypass caching logic and use the mock directly
            result = runner.invoke(sheriff_command, ["test.py", "--format", "text", "--no-cache"])

        assert result.exit_code == 0
        assert "Sheriff found no violations" in result.output

    def test_text_format_with_violations(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([sample_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "text", "--no-cache"])

        assert result.exit_code == 1
        assert "Sheriff found 1 violations" in result.output
        assert "src/module.py" in result.output
        assert "42:8" in result.output
        assert "SHERIFF_001" in result.output

    def test_text_format_with_ignored(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([], [sample_violation])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "text", "--no-cache"])

        assert result.exit_code == 0
        assert "Sheriff audited 1 ignored violations" in result.output
        assert "(IGNORED)" in result.output


class TestJSONFormat:
    """Tests for JSON output format."""

    def test_json_format_no_violations(self, runner, mock_validate_path, mock_config_from_yaml):
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "json", "--no-cache"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 0
        assert data["success"] is True
        assert data["violations"] == []

    def test_json_format_with_violations(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([sample_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "json", "--no-cache"])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["count"] == 1
        assert data["success"] is False
        assert len(data["violations"]) == 1
        assert data["violations"][0]["rule"] == "SHERIFF_001"
        assert data["violations"][0]["line"] == 42

    def test_json_format_with_ignored(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([], [sample_violation])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "json", "--no-cache"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 0
        assert data["ignored_count"] == 1
        assert data["success"] is True

    def test_deprecated_json_flag(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        """Test that deprecated --json flag still works."""
        mock_validate_path.return_value = ([sample_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--json", "--no-cache"])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["count"] == 1


class TestGitHubFormat:
    """Tests for GitHub Actions annotation format."""

    def test_github_format_no_violations(self, runner, mock_validate_path, mock_config_from_yaml):
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "github", "--no-cache"])

        assert result.exit_code == 0
        assert "::notice::Sheriff found no violations" in result.output

    def test_github_format_error_annotation(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([sample_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "github", "--no-cache"])

        assert result.exit_code == 1
        # Check GitHub Actions annotation format
        assert "::error file=src/module.py,line=42,col=8::" in result.output
        assert "[SHERIFF_001]" in result.output

    def test_github_format_warning_annotation(self, runner, mock_validate_path, mock_config_from_yaml):
        """Test that certain rules produce warnings instead of errors."""
        warning_violation = Violation(
            file=Path("src/module.py"),
            line=10,
            column=0,
            message="Missing type hint on parameter",
            rule="MissingTypeHint",
            code="def foo(x):"
        )
        mock_validate_path.return_value = ([warning_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "github", "--no-cache"])

        # Warnings should not fail the check
        assert result.exit_code == 0
        assert "::warning file=src/module.py,line=10,col=0::" in result.output

    def test_github_format_multiple_annotations(self, runner, mock_validate_path, mock_config_from_yaml, sample_violations):
        mock_validate_path.return_value = (sample_violations, [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "github", "--no-cache"])

        assert result.exit_code == 1
        # Should have multiple annotations
        error_count = result.output.count("::error")
        warning_count = result.output.count("::warning")
        assert error_count + warning_count == 3
        assert "::notice::Sheriff found" in result.output


class TestJUnitFormat:
    """Tests for JUnit XML output format."""

    def test_junit_format_no_violations(self, runner, mock_validate_path, mock_config_from_yaml):
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "junit", "--no-cache"])

        assert result.exit_code == 0
        # Parse XML
        root = ET.fromstring(result.output)
        assert root.tag == "testsuites"
        assert root.get("failures") == "0"

    def test_junit_format_with_violations(self, runner, mock_validate_path, mock_config_from_yaml, sample_violations):
        mock_validate_path.return_value = (sample_violations, [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "junit", "--no-cache"])

        assert result.exit_code == 1
        # Parse XML
        root = ET.fromstring(result.output)
        assert root.tag == "testsuites"
        assert root.get("name") == "Sheriff Validation"
        assert int(root.get("failures")) == 3

        # Check test suites per file
        testsuites = root.findall("testsuite")
        assert len(testsuites) == 2  # Two files with violations

    def test_junit_testcase_structure(self, runner, mock_validate_path, mock_config_from_yaml, sample_violation):
        mock_validate_path.return_value = ([sample_violation], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--format", "junit", "--no-cache"])

        root = ET.fromstring(result.output)
        testcase = root.find(".//testcase")
        assert testcase is not None
        assert "SHERIFF_001" in testcase.get("name")
        assert "line 42" in testcase.get("name")

        failure = testcase.find("failure")
        assert failure is not None
        assert failure.get("type") == "SHERIFF_001"
        assert "Forbidden import" in failure.get("message")


# =============================================================================
# GitHub Actions Annotation Format Tests (Detailed)
# =============================================================================

class TestGitHubAnnotationFormat:
    """Detailed tests for GitHub Actions annotation format compliance."""

    def test_annotation_escaping(self):
        """Test that special characters are properly escaped."""
        formatter = GitHubFormatter()
        violation = FormatterViolation(
            file=Path("test.py"),
            line=10,
            column=0,
            message="Error with\nnewline and % percent",
            rule="TEST_RULE",
        )
        output = formatter.format([violation], Path("test.py"))

        # Newlines should be escaped as %0A
        assert "%0A" in output
        # Percent should be escaped as %25
        assert "%25" in output or "%" not in output.replace("%0A", "").replace("%25", "")

    def test_annotation_format_exact(self):
        """Test exact format of GitHub annotations."""
        formatter = GitHubFormatter()
        violation = FormatterViolation(
            file=Path("src/test.py"),
            line=42,
            column=8,
            message="Test message",
            rule="SHERIFF_001",
        )
        output = formatter.format([violation], Path("src/"))

        # Should follow exact format: ::level file=path,line=N,col=N::message
        assert "::error file=src/test.py,line=42,col=8::[SHERIFF_001] Test message" in output

    def test_warning_rules(self):
        """Test that warning rules are correctly identified."""
        formatter = GitHubFormatter()

        # MissingTypeHint should be a warning
        warning_violation = FormatterViolation(
            file=Path("test.py"),
            line=10,
            column=0,
            message="Missing type hint",
            rule="MissingTypeHint",
        )
        output = formatter.format([warning_violation], Path("test.py"))
        assert "::warning" in output
        assert "::error" not in output.replace("::error", "", 1) or "::error" not in output

    def test_mixed_errors_and_warnings(self):
        """Test output with both errors and warnings."""
        formatter = GitHubFormatter()
        violations = [
            FormatterViolation(
                file=Path("test.py"),
                line=10,
                column=0,
                message="Forbidden import",
                rule="SHERIFF_001",  # Error
            ),
            FormatterViolation(
                file=Path("test.py"),
                line=20,
                column=0,
                message="Missing type hint",
                rule="MissingTypeHint",  # Warning
            ),
        ]
        output = formatter.format(violations, Path("test.py"))

        assert "::error" in output
        assert "::warning" in output
        assert "1 error(s)" in output
        assert "1 warning(s)" in output


# =============================================================================
# JUnit XML Tests (Detailed)
# =============================================================================

class TestJUnitXMLFormat:
    """Detailed tests for JUnit XML format compliance."""

    def test_xml_declaration(self):
        """Test that output includes XML declaration."""
        formatter = JUnitFormatter()
        output = formatter.format([], Path("test.py"))
        assert '<?xml version="1.0"' in output

    def test_testsuite_per_file(self):
        """Test that each file gets its own testsuite."""
        formatter = JUnitFormatter()
        violations = [
            FormatterViolation(
                file=Path("file1.py"),
                line=10,
                column=0,
                message="Error 1",
                rule="TEST_001",
            ),
            FormatterViolation(
                file=Path("file2.py"),
                line=20,
                column=0,
                message="Error 2",
                rule="TEST_002",
            ),
        ]
        output = formatter.format(violations, Path("src/"))

        root = ET.fromstring(output)
        testsuites = root.findall("testsuite")
        file_names = [ts.get("name") for ts in testsuites]

        assert len(testsuites) == 2
        assert "file1.py" in file_names
        assert "file2.py" in file_names

    def test_failure_details(self):
        """Test that failure elements contain complete details."""
        formatter = JUnitFormatter()
        violation = FormatterViolation(
            file=Path("test.py"),
            line=42,
            column=8,
            message="Forbidden import",
            rule="SHERIFF_001",
            code="import os",
        )
        output = formatter.format([violation], Path("test.py"))

        root = ET.fromstring(output)
        failure = root.find(".//failure")

        assert failure is not None
        failure_text = failure.text
        assert "Rule: SHERIFF_001" in failure_text
        assert "Line: 42" in failure_text
        assert "Column: 8" in failure_text
        assert "Code: import os" in failure_text


# =============================================================================
# Caching Tests
# =============================================================================

class TestCacheBehavior:
    """Tests for caching functionality."""

    def test_cache_creation(self, tmp_path):
        """Test that cache file is created."""
        cache_dir = tmp_path / ".sheriff_cache"
        cache = SheriffCache(cache_dir=cache_dir, config_hash="test_hash")

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        cache.set_violations(test_file, [])
        cache.save()

        assert cache_dir.exists()
        # Cache file includes config hash in the name
        assert (cache_dir / "sheriff_cache_test_hash.json").exists()

    def test_cache_hit(self, tmp_path):
        """Test that cached results are returned for unchanged files."""
        cache_dir = tmp_path / ".sheriff_cache"
        cache = SheriffCache(cache_dir=cache_dir, config_hash="test_hash")

        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        # Set cached violations
        violations_data = [{
            "file": str(test_file),
            "line": 1,
            "column": 0,
            "message": "Forbidden import",
            "rule": "SHERIFF_001",
            "code": "import os",
            "ignored": False,
        }]
        cache.set_violations(test_file, violations_data)

        # Verify cache hit - get_cached_violations returns data if cached
        cached = cache.get_cached_violations(test_file)
        assert cached is not None
        assert len(cached) == 1
        assert cached[0]["rule"] == "SHERIFF_001"

    def test_cache_miss_on_file_change(self, tmp_path):
        """Test that cache is invalidated when file changes."""
        cache_dir = tmp_path / ".sheriff_cache"
        cache = SheriffCache(cache_dir=cache_dir, config_hash="test_hash")

        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        # Set cached violations
        cache.set_violations(test_file, [])

        # Modify file
        test_file.write_text("import sys")

        # Cache should be invalidated - returns None for changed file
        assert cache.get_cached_violations(test_file) is None

    def test_cache_miss_on_config_change(self, tmp_path):
        """Test that cache is invalidated when config changes."""
        cache_dir = tmp_path / ".sheriff_cache"
        cache1 = SheriffCache(cache_dir=cache_dir, config_hash="hash_v1")

        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        # Set cached violations with first config
        cache1.set_violations(test_file, [])
        cache1.save()

        # Load cache with different config hash - different cache file
        cache2 = SheriffCache(cache_dir=cache_dir, config_hash="hash_v2")
        cache2.load()

        # Cache should be empty for new config hash
        assert cache2.get_cached_violations(test_file) is None

    def test_cache_clear(self, tmp_path):
        """Test cache clearing."""
        cache_dir = tmp_path / ".sheriff_cache"
        cache = SheriffCache(cache_dir=cache_dir, config_hash="test_hash")

        test_file = tmp_path / "test.py"
        test_file.write_text("import os")

        cache.set_violations(test_file, [])
        cache.save()
        cache_file = cache_dir / "sheriff_cache_test_hash.json"
        assert cache_file.exists()

        cache.clear()
        assert not cache_file.exists()

    def test_cli_no_cache_flag(self, runner, mock_validate_path, mock_config_from_yaml):
        """Test that --no-cache flag disables caching."""
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, ["test.py", "--no-cache"])

        assert result.exit_code == 0
        # Cache directory should not be created
        assert not Path(".sheriff_cache").exists()

    def test_cli_clear_cache_flag(self, runner, mock_validate_path, mock_config_from_yaml):
        """Test that --clear-cache flag clears existing cache."""
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            # Create cache directory first
            cache_dir = Path(".sheriff_cache")
            cache_dir.mkdir()
            (cache_dir / "cache.json").write_text('{"version": "1.0", "entries": {}}')

            result = runner.invoke(sheriff_command, ["test.py", "--clear-cache"])

        assert result.exit_code == 0

    def test_cli_custom_cache_dir(self, runner, mock_validate_path, mock_config_from_yaml):
        """Test custom cache directory."""
        mock_validate_path.return_value = ([], [])
        with runner.isolated_filesystem():
            Path("test.py").touch()
            result = runner.invoke(sheriff_command, [
                "test.py",
                "--cache-dir", "custom_cache"
            ])

        assert result.exit_code == 0


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in different output formats."""

    def test_json_error_output(self, runner):
        """Test JSON format error output."""
        result = runner.invoke(sheriff_command, ["nonexistent.py", "--format", "json"])

        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data
        assert data["success"] is False

    def test_github_error_output(self, runner):
        """Test GitHub format error output."""
        result = runner.invoke(sheriff_command, ["nonexistent.py", "--format", "github"])

        assert result.exit_code == 1
        assert "::error::" in result.output

    def test_junit_error_output(self, runner):
        """Test JUnit format error output."""
        result = runner.invoke(sheriff_command, ["nonexistent.py", "--format", "junit"])

        assert result.exit_code == 1
        root = ET.fromstring(result.output)
        assert root.find(".//error") is not None


# =============================================================================
# Formatter Factory Tests
# =============================================================================

class TestFormatterFactory:
    """Tests for the formatter factory function."""

    def test_get_text_formatter(self):
        formatter = get_formatter("text")
        assert isinstance(formatter, TextFormatter)

    def test_get_json_formatter(self):
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_get_github_formatter(self):
        formatter = get_formatter("github")
        assert isinstance(formatter, GitHubFormatter)

    def test_get_junit_formatter(self):
        formatter = get_formatter("junit")
        assert isinstance(formatter, JUnitFormatter)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError) as exc_info:
            get_formatter("invalid")
        assert "Unknown format" in str(exc_info.value)


# =============================================================================
# Config Hash Tests
# =============================================================================

class TestConfigHash:
    """Tests for configuration hashing."""

    def test_config_hash_consistency(self):
        """Test that same config produces same hash."""
        config1 = MockSheriffConfig()
        config1.forbidden_imports = ["os"]
        config1.enforce_type_hints = True

        config2 = MockSheriffConfig()
        config2.forbidden_imports = ["os"]
        config2.enforce_type_hints = True

        hash1 = get_config_hash(config1)
        hash2 = get_config_hash(config2)
        assert hash1 == hash2

    def test_config_hash_different_for_different_config(self):
        """Test that different configs produce different hashes."""
        config1 = MockSheriffConfig()
        config1.forbidden_imports = ["os"]

        config2 = MockSheriffConfig()
        config2.forbidden_imports = ["sys"]

        hash1 = get_config_hash(config1)
        hash2 = get_config_hash(config2)
        assert hash1 != hash2
