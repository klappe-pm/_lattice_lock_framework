"""
Data models for Approver Agent results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ApprovalStatus(Enum):
    """Status of an approval decision."""

    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    CONDITIONAL = "conditional"


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CoverageResult:
    """Result from coverage analysis."""

    line_coverage: float
    branch_coverage: float
    function_coverage: float
    target: int
    meets_threshold: bool
    uncovered_files: list[str] = field(default_factory=list)
    uncovered_lines: dict[str, list[int]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Primary coverage percentage (line coverage)."""
        return self.line_coverage


@dataclass
class DocumentationResult:
    """Result from documentation validation."""

    valid: bool
    broken_links: list[str] = field(default_factory=list)
    invalid_code_examples: list[str] = field(default_factory=list)
    diagram_errors: list[str] = field(default_factory=list)
    style_violations: list[str] = field(default_factory=list)
    files_checked: int = 0

    @property
    def total_issues(self) -> int:
        """Total number of documentation issues."""
        return (
            len(self.broken_links)
            + len(self.invalid_code_examples)
            + len(self.diagram_errors)
            + len(self.style_violations)
        )


@dataclass
class TestReviewResult:
    """Result from test review."""

    quality_score: int  # 0-100
    tests_reviewed: int
    pattern_violations: list[str] = field(default_factory=list)
    naming_issues: list[str] = field(default_factory=list)
    flaky_tests: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Whether test quality meets minimum threshold (70)."""
        return self.quality_score >= 70


@dataclass
class BlockingIssue:
    """A blocking issue that prevents approval."""

    message: str
    severity: Severity
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    category: str = "general"


@dataclass
class ApprovalResult:
    """Complete approval result from Approver Agent."""

    status: ApprovalStatus
    approved: bool
    timestamp: datetime = field(default_factory=datetime.now)

    # Sub-results
    coverage_result: Optional[CoverageResult] = None
    documentation_result: Optional[DocumentationResult] = None
    test_review_result: Optional[TestReviewResult] = None

    # Issues and recommendations
    blocking_issues: list[BlockingIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Metadata
    pr_number: Optional[int] = None
    commit_sha: Optional[str] = None
    reviewed_by: str = "ApproverAgent"

    @property
    def coverage_passed(self) -> bool:
        """Whether coverage requirements are met."""
        if self.coverage_result is None:
            return True
        return self.coverage_result.meets_threshold

    @property
    def docs_passed(self) -> bool:
        """Whether documentation validation passed."""
        if self.documentation_result is None:
            return True
        return self.documentation_result.valid

    @property
    def tests_passed(self) -> bool:
        """Whether test review passed."""
        if self.test_review_result is None:
            return True
        return self.test_review_result.passed

    def to_markdown(self) -> str:
        """Generate markdown report of approval result."""
        status_emoji = "✅" if self.approved else "❌"
        lines = [
            f"# Approver Agent Review {status_emoji}",
            "",
            f"**Status**: {self.status.value.upper()}",
            f"**Timestamp**: {self.timestamp.isoformat()}",
            "",
        ]

        if self.coverage_result:
            cov = self.coverage_result
            cov_status = "✅" if cov.meets_threshold else "❌"
            lines.extend(
                [
                    "## Coverage Analysis",
                    f"- Line Coverage: {cov.line_coverage:.1f}% {cov_status}",
                    f"- Branch Coverage: {cov.branch_coverage:.1f}%",
                    f"- Target: {cov.target}%",
                    "",
                ]
            )

        if self.documentation_result:
            doc = self.documentation_result
            doc_status = "✅" if doc.valid else "❌"
            lines.extend(
                [
                    "## Documentation Validation",
                    f"- Status: {'PASSED' if doc.valid else 'FAILED'} {doc_status}",
                    f"- Files Checked: {doc.files_checked}",
                    f"- Issues Found: {doc.total_issues}",
                    "",
                ]
            )

        if self.test_review_result:
            test = self.test_review_result
            test_status = "✅" if test.passed else "❌"
            lines.extend(
                [
                    "## Test Review",
                    f"- Quality Score: {test.quality_score}/100 {test_status}",
                    f"- Tests Reviewed: {test.tests_reviewed}",
                    "",
                ]
            )

        if self.blocking_issues:
            lines.extend(
                [
                    "## Blocking Issues",
                    "",
                ]
            )
            for issue in self.blocking_issues:
                lines.append(f"- **[{issue.severity.value.upper()}]** {issue.message}")
            lines.append("")

        if self.recommendations:
            lines.extend(
                [
                    "## Recommendations",
                    "",
                ]
            )
            for rec in self.recommendations:
                lines.append(f"- {rec}")

        return "\n".join(lines)
