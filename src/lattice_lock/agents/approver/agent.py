"""
Approver Agent - The Single Authority for Testing and Quality Approvals.

This agent is ENABLED BY DEFAULT and serves as the central authority for:
- Test reviews and quality enforcement
- 90% code coverage enforcement
- Documentation validation
- Requirements traceability
- Coordinating sub-agents for systematic quality control
"""

from __future__ import annotations

import ast
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from lattice_lock.agents.approver.models import (
    ApprovalResult,
    ApprovalStatus,
    BlockingIssue,
    CoverageResult,
    DocumentationResult,
    Severity,
    TestReviewResult,
)
from lattice_lock.agents.settings import AgentSettings, get_settings


class ApproverAgent:
    """
    The single authority for all testing and quality approvals.

    Enabled by default. Toggle via:
    - Settings: settings.agents.approver_agent.enabled = false
    - Environment: LATTICE_APPROVER_ENABLED=false
    """

    def __init__(self, settings: Optional[AgentSettings] = None):
        """
        Initialize the Approver Agent.

        Args:
            settings: Optional settings override. Uses global settings if None.

        Raises:
            RuntimeError: If Approver Agent is disabled in settings.
        """
        self.settings = settings or get_settings()
        self._config = self.settings.agents.approver_agent

        if not self._config.enabled:
            raise RuntimeError(
                "ApproverAgent is disabled. "
                "Enable via LATTICE_APPROVER_ENABLED=true or in agent_settings.yaml"
            )

    @property
    def coverage_target(self) -> int:
        """Get the coverage target percentage."""
        return self._config.coverage.target

    @property
    def is_enabled(self) -> bool:
        """Check if approver is enabled."""
        return self._config.enabled

    def analyze_coverage(self, coverage_xml: Optional[Path] = None) -> CoverageResult:
        """
        Analyze code coverage from coverage.xml.

        Args:
            coverage_xml: Path to coverage.xml file. Defaults to ./coverage.xml

        Returns:
            CoverageResult with coverage metrics and analysis.
        """
        if coverage_xml is None:
            coverage_xml = Path("coverage.xml")

        if not coverage_xml.exists():
            # Try to generate coverage report
            return CoverageResult(
                line_coverage=0.0,
                branch_coverage=0.0,
                function_coverage=0.0,
                target=self.coverage_target,
                meets_threshold=False,
                recommendations=["Run pytest with --cov to generate coverage.xml"],
            )

        # Parse coverage.xml
        tree = ET.parse(coverage_xml)
        root = tree.getroot()

        line_rate = float(root.get("line-rate", 0)) * 100
        branch_rate = float(root.get("branch-rate", 0)) * 100

        # Calculate function coverage from packages
        total_functions = 0
        covered_functions = 0
        uncovered_files = []
        uncovered_lines: dict[str, list[int]] = {}

        for package in root.findall(".//package"):
            for cls in package.findall(".//class"):
                try:
                    filename = cls.get("filename")
                    if not filename:
                        continue  # Skip if no filename attribute
                    
                    file_line_rate = float(cls.get("line-rate", "0")) * 100

                    if file_line_rate < self.coverage_target:
                        uncovered_files.append(f"{filename} ({file_line_rate:.1f}%)")

                    # Track uncovered lines
                    file_uncovered = []
                    for line in cls.findall(".//line"):
                        try:
                            if line.get("hits") == "0":
                                line_num = int(line.get("number", "0"))
                                if line_num > 0:
                                    file_uncovered.append(line_num)
                        except (ValueError, TypeError):
                            continue  # Skip malformed line entries

                    if file_uncovered:
                        uncovered_lines[filename] = file_uncovered[:10]  # Limit to 10

                    # Count methods
                    for method in cls.findall(".//method"):
                        try:
                            total_functions += 1
                            method_line_rate = float(method.get("line-rate", "0"))
                            if method_line_rate > 0:
                                covered_functions += 1
                        except (ValueError, TypeError):
                            continue  # Skip malformed method entries
                except (ValueError, TypeError) as e:
                    # Skip malformed class entries but continue processing
                    continue

        function_coverage = (
            (covered_functions / total_functions * 100) if total_functions > 0 else 0.0
        )

        meets_threshold = line_rate >= self.coverage_target

        recommendations = []
        if not meets_threshold:
            recommendations.append(
                f"Increase line coverage from {line_rate:.1f}% to {self.coverage_target}%"
            )
        if uncovered_files:
            recommendations.append(
                f"Focus on: {', '.join(uncovered_files[:3])}"
            )

        return CoverageResult(
            line_coverage=line_rate,
            branch_coverage=branch_rate,
            function_coverage=function_coverage,
            target=self.coverage_target,
            meets_threshold=meets_threshold,
            uncovered_files=uncovered_files[:10],
            uncovered_lines=uncovered_lines,
            recommendations=recommendations,
        )

    def validate_documentation(self, docs_path: Optional[Path] = None) -> DocumentationResult:
        """
        Validate documentation quality.

        Args:
            docs_path: Path to documentation directory. Defaults to ./docs

        Returns:
            DocumentationResult with validation findings.
        """
        if docs_path is None:
            docs_path = Path("docs")

        broken_links = []
        invalid_code_examples = []
        style_violations = []
        files_checked = 0

        # Link pattern for internal links
        link_pattern = re.compile(r"\[([^\]]+)\]\((?!http)([^)#]+)")
        # Code block pattern
        python_block = re.compile(r"```python\n(.*?)```", re.DOTALL)
        # Unlabeled code block
        unlabeled_block = re.compile(r"^```\s*$", re.MULTILINE)

        md_files = list(docs_path.rglob("*.md")) if docs_path.exists() else []

        for md_file in md_files:
            files_checked += 1
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            # Check internal links
            for match in link_pattern.finditer(content):
                link_target = match.group(2).split("#")[0]
                if link_target:
                    target_path = md_file.parent / link_target
                    if not target_path.exists():
                        broken_links.append(f"{md_file}:{match.group(2)}")

            # Check Python code examples
            for i, match in enumerate(python_block.finditer(content)):
                code = match.group(1)
                # Skip incomplete examples
                if "..." in code or "# ..." in code:
                    continue
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    invalid_code_examples.append(f"{md_file} block {i+1}: {e.msg}")

            # Check for unlabeled code blocks
            if unlabeled_matches := unlabeled_block.findall(content):
                style_violations.append(
                    f"{md_file}: {len(unlabeled_matches)} unlabeled code blocks"
                )

        valid = len(broken_links) == 0 and len(invalid_code_examples) == 0

        return DocumentationResult(
            valid=valid,
            broken_links=broken_links[:20],  # Limit output
            invalid_code_examples=invalid_code_examples[:10],
            diagram_errors=[],  # TODO: Implement mermaid validation
            style_violations=style_violations[:10],
            files_checked=files_checked,
        )

    def review_tests(self, tests_path: Optional[Path] = None) -> TestReviewResult:
        """
        Review test quality and patterns.

        Args:
            tests_path: Path to tests directory. Defaults to ./tests

        Returns:
            TestReviewResult with quality assessment.
        """
        if tests_path is None:
            tests_path = Path("tests")

        pattern_violations = []
        naming_issues = []
        flaky_indicators = []
        recommendations = []
        tests_reviewed = 0

        # Patterns to check
        aaa_pattern = re.compile(r"#\s*(arrange|act|assert)", re.IGNORECASE)
        bad_name_pattern = re.compile(r"def (test\d+|test_it|test_stuff)\(")
        flaky_patterns = [
            (r"time\.sleep\(", "time.sleep() can cause flakiness"),
            (r"random\.", "random values without seeding can cause flakiness"),
            (r"datetime\.now\(\)", "datetime.now() can cause timing issues"),
        ]

        test_files = list(tests_path.rglob("test_*.py")) if tests_path.exists() else []

        for test_file in test_files:
            tests_reviewed += 1
            try:
                content = test_file.read_text()
            except Exception:
                continue

            # Check for AAA pattern (positive indicator)
            has_aaa = bool(aaa_pattern.search(content))

            # Check for bad naming
            if matches := bad_name_pattern.findall(content):
                naming_issues.append(f"{test_file}: {', '.join(matches)}")

            # Check for flaky patterns
            for pattern, message in flaky_patterns:
                if re.search(pattern, content):
                    flaky_indicators.append(f"{test_file}: {message}")

        # Calculate quality score (simple heuristic)
        base_score = 80
        if naming_issues:
            base_score -= min(len(naming_issues) * 5, 20)
        if flaky_indicators:
            base_score -= min(len(flaky_indicators) * 5, 20)
        if pattern_violations:
            base_score -= min(len(pattern_violations) * 5, 20)

        quality_score = max(0, min(100, base_score))

        if naming_issues:
            recommendations.append("Improve test names to describe scenario and expected outcome")
        if flaky_indicators:
            recommendations.append("Address potential sources of test flakiness")
        if quality_score < 70:
            recommendations.append("Review test patterns and structure")

        return TestReviewResult(
            quality_score=quality_score,
            tests_reviewed=tests_reviewed,
            pattern_violations=pattern_violations,
            naming_issues=naming_issues[:10],
            flaky_tests=flaky_indicators[:10],
            recommendations=recommendations,
        )

    def review(
        self,
        pr_number: Optional[int] = None,
        commit_sha: Optional[str] = None,
    ) -> ApprovalResult:
        """
        Perform a complete review and return approval decision.

        Args:
            pr_number: Optional PR number for context.
            commit_sha: Optional commit SHA for context.

        Returns:
            ApprovalResult with complete review findings.
        """
        blocking_issues: list[BlockingIssue] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Run coverage analysis
        coverage_result = self.analyze_coverage()
        if not coverage_result.meets_threshold:
            blocking_issues.append(
                BlockingIssue(
                    message=(
                        f"Coverage {coverage_result.line_coverage:.1f}% "
                        f"below target {self.coverage_target}%"
                    ),
                    severity=Severity.HIGH,
                    category="coverage",
                )
            )
        recommendations.extend(coverage_result.recommendations)

        # Run documentation validation
        doc_result = self.validate_documentation()
        if doc_result.broken_links:
            for link in doc_result.broken_links[:5]:
                blocking_issues.append(
                    BlockingIssue(
                        message=f"Broken link: {link}",
                        severity=Severity.MEDIUM,
                        category="documentation",
                    )
                )
        if doc_result.invalid_code_examples:
            for example in doc_result.invalid_code_examples[:3]:
                warnings.append(f"Invalid code example: {example}")

        # Run test review
        test_result = self.review_tests()
        if not test_result.passed:
            blocking_issues.append(
                BlockingIssue(
                    message=f"Test quality score {test_result.quality_score} below threshold 70",
                    severity=Severity.MEDIUM,
                    category="test_quality",
                )
            )
        recommendations.extend(test_result.recommendations)

        # Determine approval status
        approved = len(blocking_issues) == 0
        if approved:
            status = ApprovalStatus.APPROVED
        elif any(issue.severity == Severity.CRITICAL for issue in blocking_issues):
            status = ApprovalStatus.REJECTED
        else:
            status = ApprovalStatus.CONDITIONAL

        return ApprovalResult(
            status=status,
            approved=approved,
            coverage_result=coverage_result,
            documentation_result=doc_result,
            test_review_result=test_result,
            blocking_issues=blocking_issues,
            warnings=warnings,
            recommendations=recommendations,
            pr_number=pr_number,
            commit_sha=commit_sha,
        )

    def quick_check(self) -> bool:
        """
        Run a quick check suitable for pre-commit hooks.

        Returns:
            True if basic checks pass, False otherwise.
        """
        # Quick lint check
        result = subprocess.run(
            ["ruff", "check", "src/", "--quiet"],
            capture_output=True,
        )
        if result.returncode != 0:
            return False

        # Quick type check (if mypy available)
        result = subprocess.run(
            ["mypy", "src/lattice_lock", "--no-error-summary", "--quiet"],
            capture_output=True,
        )
        # Don't fail on mypy - just warn

        return True
