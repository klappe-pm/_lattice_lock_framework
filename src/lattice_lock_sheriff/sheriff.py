"""Sheriff validation module for AST-based Python code analysis.

Provides validation functions that check Python files against configured rules
for import discipline, type hints, and other code quality standards.
"""

import ast
import os
from pathlib import Path
from typing import Optional

from .ast_visitor import SheriffVisitor
from .config import SheriffConfig
from .rules import Violation


def validate_file_with_audit(
    file_path: Path, config: SheriffConfig, ignore_patterns: Optional[list[str]] = None
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
    ignore_patterns: Optional[list[str]] = None,
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
    ignore_patterns: Optional[list[str]] = None,
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
