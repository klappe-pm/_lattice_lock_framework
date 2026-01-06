"""Sheriff validation module for AST-based Python code analysis.

Provides validation functions that check Python files against configured rules
for import discipline, type hints, and other code quality standards.
"""

import ast
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from lattice_lock.utils.safe_path import resolve_under_root

from .ast_visitor import SheriffVisitor
from .config import SheriffConfig, ViolationSeverity
from .rules import Violation

logger = logging.getLogger("lattice_lock.sheriff")


@dataclass
class SheriffResult:
    """Result of Sheriff analysis."""

    violations: list[Violation] = field(default_factory=list)
    files_checked: int = 0
    passed: bool = True

    def add_violation(self, violation: Violation) -> None:
        """Add a violation and update passed status."""
        self.violations.append(violation)
        if violation.severity == ViolationSeverity.ERROR:
            self.passed = False

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON output."""
        return {
            "passed": self.passed,
            "files_checked": self.files_checked,
            "error_count": sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR),
            "warning_count": sum(
                1 for v in self.violations if v.severity == ViolationSeverity.WARNING
            ),
            "violations": [
                {
                    "rule": v.rule_id,
                    "message": v.message,
                    "file": v.filename,
                    "line": v.line_number,
                    "column": v.column,
                    "severity": v.severity.value,
                    "suggestion": v.suggestion,
                }
                for v in self.violations
            ],
        }


def validate_file_with_audit(
    file_path: Path, config: SheriffConfig, ignore_patterns: list[str] | None = None
) -> tuple[list[Violation], list[Violation]]:
    """Validate a single Python file and return violations with audit info.

    Args:
        file_path: Path to the Python file
        config: Sheriff configuration
        ignore_patterns: Optional list of glob patterns to ignore

    Returns:
        Tuple of (violations, ignored_violations)
    """
    if ignore_patterns is None:
        ignore_patterns = []

    if file_path.suffix != ".py":
        return [], []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(file_path))

        # Run Visitor
        visitor = SheriffVisitor(str(file_path), config, content)
        visitor.visit(tree)

        # Return violations directly from visitor
        return visitor.get_violations(), visitor.get_ignored_violations()

    except SyntaxError as e:
        return [
            Violation(
                rule_id="SyntaxError",
                message=f"Syntax error: {e.msg}",
                line_number=e.lineno if e.lineno else 0,
                filename=str(file_path),
            )
        ], []
    except Exception as e:
        return [
            Violation(
                rule_id="ParseError",
                message=f"Error parsing file: {e}",
                line_number=0,
                filename=str(file_path),
            )
        ], []


def validate_path_with_audit(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: list[str] | None = None,
) -> tuple[list[Violation], list[Violation]]:
    """Validate a file or directory and return violations with audit info.

    Args:
        path: Path to validate (file or directory)
        config: Sheriff configuration
        ignore_patterns: Optional list of glob patterns to ignore

    Returns:
        Tuple of (violations, ignored_violations)
    """
    if ignore_patterns is None:
        ignore_patterns = []

    violations: list[Violation] = []
    ignored_violations: list[Violation] = []

    # Check if path is ignored
    for pattern in ignore_patterns:
        if path.match(pattern):
            return [], []

    if path.is_file():
        if path.suffix == ".py":
            # Apply file-level ignore patterns
            for pattern in ignore_patterns:
                if path.match(pattern):
                    return [], []
            v, iv = validate_file_with_audit(path, config, ignore_patterns)
            violations.extend(v)
            ignored_violations.extend(iv)

    elif path.is_dir():
        for root, _, files in os.walk(path):
            current_dir = Path(root)

            # Apply directory-level ignore patterns
            ignored_by_dir_pattern = False
            for pattern in ignore_patterns:
                relative_dir = current_dir.relative_to(path) if current_dir != path else Path(".")
                if relative_dir.match(pattern):
                    ignored_by_dir_pattern = True
                    break
            if ignored_by_dir_pattern:
                continue

            for file in files:
                file_path = current_dir / file
                if file_path.suffix == ".py":
                    # Apply file-level ignore patterns
                    ignored_by_file_pattern = False
                    for pattern in ignore_patterns:
                        if file_path.match(pattern):
                            ignored_by_file_pattern = True
                            break
                    if ignored_by_file_pattern:
                        continue

                    v, iv = validate_file_with_audit(file_path, config, ignore_patterns)
                    violations.extend(v)
                    ignored_violations.extend(iv)

    return violations, ignored_violations


def validate_file(file_path: Path, config: SheriffConfig) -> list[Violation]:
    """Validate a single Python file.

    Args:
        file_path: Path to the Python file
        config: Sheriff configuration

    Returns:
        List of violations found
    """
    violations, _ = validate_file_with_audit(file_path, config)
    return violations


def validate_path(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: list[str] | None = None,
) -> list[Violation]:
    """Validate a file or directory.

    Args:
        path: Path to validate (file or directory)
        config: Sheriff configuration
        ignore_patterns: Optional list of glob patterns to ignore

    Returns:
        List of violations found (excludes ignored violations)
    """
    violations, _ = validate_path_with_audit(path, config, ignore_patterns)
    return violations


def run_sheriff(
    target_path: str,
    config: dict | None = None,
    json_output: bool = False,
) -> SheriffResult:
    """
    Run Sheriff analysis on a directory or file.

    Args:
        target_path: Path to analyze (file or directory)
        config: Optional configuration dict (uses DEFAULT_CONFIG if not provided)
        json_output: Whether to format output as JSON

    Returns:
        SheriffResult with all violations found
    """
    # Check feature flag
    from lattice_lock.config.feature_flags import Feature, is_feature_enabled

    if not is_feature_enabled(Feature.SHERIFF):
        logger.warning("Sheriff feature is disabled via feature flags. Skipping analysis.")
        return SheriffResult()

    # Create SheriffConfig object
    if config:
        sheriff_config = SheriffConfig(
            forbidden_imports=config.get("forbidden_imports", []),
            enforce_type_hints=config.get("enforce_type_hints", True),
            target_version=config.get("target_version", "current"),
            custom_rules=config.get("custom_rules", {}),
        )
    else:
        sheriff_config = SheriffConfig()

    result = SheriffResult()

    try:
        # Prevent Path Traversal by resolving under generic root
        target_path_resolved = resolve_under_root(os.getcwd(), target_path)
        target = Path(target_path_resolved)
    except ValueError as e:
        logger.error(f"Invalid path: {e}")
        return result

    if not target.exists():
        result.add_violation(
            Violation(
                rule_id="PATH_NOT_FOUND",
                message=f"Target path does not exist: {target_path}",
                file=target_path,
                line_number=0,
                filename=target_path,
                severity=ViolationSeverity.ERROR,
            )
        )
        return result

    # Collect Python files
    if target.is_file():
        python_files = [target] if target.suffix == ".py" else []
    else:
        python_files = list(target.rglob("*.py"))
        # Exclude common directories
        exclude_dirs = {"__pycache__", ".git", ".venv", "build", "dist", ".pytest_cache"}
        python_files = [
            f for f in python_files if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

    # Analyze each file
    for filepath in python_files:
        violations, _ = validate_file_with_audit(filepath, sheriff_config)
        for v in violations:
            result.add_violation(v)
        result.files_checked += 1

    return result
