"""Sheriff validation module for AST-based Python code analysis.

Provides validation functions that check Python files against configured rules
for import discipline, type hints, and other code quality standards.
"""

import ast
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .config import SheriffConfig
from .ast_visitor import SheriffVisitor
from .rules import Violation as RuleViolation


@dataclass
class Violation:
    """CLI-friendly violation representation with file context.

    This class wraps the internal RuleViolation with additional file context
    needed for CLI output and CI integration.
    """
    file: Path
    line: int
    column: int
    message: str
    rule: str
    code: Optional[str] = None


def _convert_rule_violation(
    rv: RuleViolation,
    file_path: Path,
    file_lines: List[str]
) -> Violation:
    """Convert a RuleViolation to a CLI Violation with file context."""
    code_snippet = None
    if 0 < rv.line_number <= len(file_lines):
        code_snippet = file_lines[rv.line_number - 1].strip()

    return Violation(
        file=file_path,
        line=rv.line_number,
        column=0,  # Column not currently captured by RuleViolation
        message=rv.message,
        rule=rv.rule_id,
        code=code_snippet
    )


def validate_file_with_audit(
    file_path: Path,
    config: SheriffConfig,
    ignore_patterns: Optional[List[str]] = None
) -> Tuple[List[Violation], List[Violation]]:
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

    if not file_path.suffix == ".py":
        return [], []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            file_lines = content.splitlines()

        # Parse AST
        tree = ast.parse(content, filename=str(file_path))

        # Run Visitor
        visitor = SheriffVisitor(str(file_path), config, content)
        visitor.visit(tree)

        # Convert RuleViolations to CLI Violations
        violations = [
            _convert_rule_violation(rv, file_path, file_lines)
            for rv in visitor.get_violations()
        ]
        ignored_violations = [
            _convert_rule_violation(rv, file_path, file_lines)
            for rv in visitor.get_ignored_violations()
        ]

        return violations, ignored_violations

    except SyntaxError as e:
        return [
            Violation(
                file=file_path,
                line=e.lineno if e.lineno else 0,
                column=e.offset if e.offset else 0,
                message=f"Syntax error: {e.msg}",
                rule="SyntaxError",
                code=e.text.strip() if e.text else None
            )
        ], []
    except Exception as e:
        return [
            Violation(
                file=file_path,
                line=0,
                column=0,
                message=f"Error parsing file: {e}",
                rule="ParseError"
            )
        ], []

def validate_path_with_audit(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: Optional[List[str]] = None,
) -> Tuple[List[Violation], List[Violation]]:
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

    violations: List[Violation] = []
    ignored_violations: List[Violation] = []

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
                relative_dir = current_dir.relative_to(path) if current_dir != path else Path('.')
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


def validate_file(file_path: Path, config: SheriffConfig) -> List[Violation]:
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
    ignore_patterns: Optional[List[str]] = None,
) -> List[Violation]:
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
