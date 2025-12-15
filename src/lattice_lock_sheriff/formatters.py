from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
import json
import xml.etree.ElementTree as ET
from defusedxml import minidom

from .rules import Violation # Import the updated Violation

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, violations: List[Violation], target_path: Path) -> str:
        """Format violations for output.

        Args:
            violations: List of Violation objects (from rules.py)
            target_path: The path that was validated

        Returns:
            Formatted string output
        """
        pass

    @abstractmethod
    def format_error(self, message: str) -> str:
        """Format an error message for output.

        Args:
            message: The error message

        Returns:
            Formatted string output
        """
        pass

    def get_exit_code(self, violations: List[Violation]) -> int:
        """Determine the exit code based on violations.

        Args:
            violations: List of violations

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        return 1 if violations else 0


class TextFormatter(OutputFormatter):
    """Human-readable text formatter for terminal output."""

    def format(self, violations: List[Violation], target_path: Path) -> str:
        """Format violations as human-readable text."""
        output_lines = []
        if not violations:
            output_lines.append(f"\nSheriff found no violations in {target_path}")
        else:
            output_lines.append(f"\nSheriff found {len(violations)} violations in {target_path}:")
            for v in violations:
                output_lines.append(
                    f"  {v.filename}:{v.line_number}: {v.rule_id} - {v.message}"
                )

        output_lines.append(f"\nSummary: {len(violations)} violations found.")
        return "\n".join(output_lines)

    def format_error(self, message: str) -> str:
        return f"Error: {message}"


class JSONFormatter(OutputFormatter):
    """JSON formatter for machine-readable output."""

    def format(self, violations: List[Violation], target_path: Path) -> str:
        """Format violations as JSON."""
        violations_data = []
        for v in violations:
            violations_data.append({
                "rule_id": v.rule_id,
                "message": v.message,
                "line_number": v.line_number,
                "filename": str(v.filename), # Ensure Path is str for JSON
            })

        result = {
            "violations": violations_data,
            "count": len(violations),
            "target": str(target_path),
            "success": len(violations) == 0
        }
        return json.dumps(result, indent=2)

    def format_error(self, message: str) -> str:
        return json.dumps({"error": message, "success": False}, indent=2)


class GitHubFormatter(OutputFormatter):
    """GitHub Actions annotation formatter.

    Produces output in the format:
    ::error file={file},line={line},col={col}::{message}
    ::warning file={file},line={line},col={col}::{message}
    """

    # Rules that should be warnings instead of errors
    # Using specific rule_ids for determination
    WARNING_RULES = {"SHERIFF_002"} # TypeHintRule is typically a warning

    def format(self, violations: List[Violation], target_path: Path) -> str:
        """Format violations as GitHub Actions annotations."""
        if not violations:
            return "::notice::Sheriff found no violations"

        lines = []
        error_count = 0
        warning_count = 0

        for v in violations:
            # Determine severity based on rule_id
            severity = "warning" if v.rule_id in self.WARNING_RULES else "error"
            if severity == "error":
                error_count += 1
            else:
                warning_count += 1

            # Format message (escape special characters)
            message = self._escape_message(f"[{v.rule_id}] {v.message}")

            # Build annotation
            annotation = f"::{severity} file={v.filename},line={v.line_number},title={v.rule_id}::{message}"
            lines.append(annotation)

        # Add summary
        summary_parts = []
        if error_count > 0:
            summary_parts.append(f"{error_count} error(s)")
        if warning_count > 0:
            summary_parts.append(f"{warning_count} warning(s)")

        summary_text = " and ".join(summary_parts)
        summary = f"::notice::Sheriff found {summary_text} in {target_path}"
        lines.append(summary)

        return "\n".join(lines)

    def format_error(self, message: str) -> str:
        return f"::error::{message}"

    def _escape_message(self, message: str) -> str:
        """Escape special characters for GitHub Actions."""
        # GitHub Actions uses %0A for newlines, %25 for %, %0D for carriage return
        return (
            message
            .replace("%", "%25")
            .replace("\r", "%0D")
            .replace("\n", "%0A")
        )

    def get_exit_code(self, violations: List[Violation]) -> int:
        # Only return non-zero for errors, not warnings
        error_count = sum(1 for v in violations if v.rule_id not in self.WARNING_RULES)
        return 1 if error_count > 0 else 0


class JUnitFormatter(OutputFormatter):
    """JUnit XML formatter for CI system integration."""

    def format(self, violations: List[Violation], target_path: Path) -> str:
        """Format violations as JUnit XML."""
        # Group violations by file
        violations_by_file: Dict[str, List[Violation]] = {}
        for v in violations:
            file_key = str(v.filename)
            if file_key not in violations_by_file:
                violations_by_file[file_key] = []
            violations_by_file[file_key].append(v)

        # Create root element
        testsuites = ET.Element("testsuites")
        testsuites.set("name", "Sheriff Validation")
        testsuites.set("tests", str(self._count_tests(violations_by_file)))
        testsuites.set("failures", str(len(violations)))
        testsuites.set("errors", "0")

        if violations_by_file:
            # Create test suites for files with violations
            for file_path_str, file_violations in violations_by_file.items():
                testsuite = self._create_testsuite(file_path_str, file_violations)
                testsuites.append(testsuite)
        else:
            # Create a single passing test suite if no violations
            testsuite = ET.SubElement(testsuites, "testsuite")
            testsuite.set("name", str(target_path))
            testsuite.set("tests", "1")
            testsuite.set("failures", "0")
            testsuite.set("errors", "0")

            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", "Sheriff validation passed")
            testcase.set("classname", str(target_path))

        # Pretty print XML
        return self._prettify_xml(testsuites)

    def format_error(self, message: str) -> str:
        root = ET.Element("testsuites", name="Sheriff Validation", tests="1", failures="0", errors="1")
        testsuite = ET.SubElement(root, "testsuite", name="Sheriff", tests="1", failures="0", errors="1")
        testcase = ET.SubElement(testsuite, "testcase", name="ConfigurationError", classname="sheriff.config")
        error_elem = ET.SubElement(testcase, "error", message=message, type="ConfigurationError")
        error_elem.text = message
        ET.SubElement(testcase, "system-out").text = message
        return self._prettify_xml(root)

    def _create_testsuite(self, file_path_str: str, violations: List[Violation]) -> ET.Element:
        """Create a testsuite element for a file."""
        testsuite = ET.Element("testsuite")
        testsuite.set("name", file_path_str)
        testsuite.set("tests", str(len(violations)))
        testsuite.set("failures", str(len(violations)))
        testsuite.set("errors", "0")

        for v in violations:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", f"{v.rule_id} at line {v.line_number}")
            testcase.set("classname", file_path_str)

            failure = ET.SubElement(testcase, "failure")
            failure.set("message", v.message)
            failure.set("type", v.rule_id)

            # Add detailed failure text
            failure_text_parts = [
                f"Rule: {v.rule_id}",
                f"File: {v.filename}",
                f"Line: {v.line_number}",
                f"Message: {v.message}"
            ]
            failure.text = "\n".join(failure_text_parts)

        return testsuite

    def _count_tests(self, violations_by_file: Dict[str, List[Violation]]) -> int:
        """Count total tests (violations count as tests)."""
        if not violations_by_file:
            return 1  # One passing test
        return sum(len(v) for v in violations_by_file.values())

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def get_formatter(format_name: str) -> OutputFormatter:
    """Factory function to get the appropriate formatter."""
    formatters = {
        "text": TextFormatter,
        "json": JSONFormatter,
        "github": GitHubFormatter,
        "junit": JUnitFormatter
    }

    if format_name not in formatters:
        valid_formats = ", ".join(formatters.keys())
        raise ValueError(f"Unknown format '{format_name}'. Valid formats: {valid_formats}")

    return formatters[format_name]()
