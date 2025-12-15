"""
Sheriff AST Validator for Lattice Lock Framework.

This module provides AST-based code analysis to enforce Lattice-specific rules
that generic linters cannot handle. Sheriff validates:

1. Import discipline - enforces canonical import paths
2. Forbidden imports - blocks disallowed modules
3. Type hints - ensures public functions have return type hints
4. Path hygiene - detects hardcoded user paths
5. Size limits - warns on overly long functions
6. Duplicate definitions - catches duplicate class/function names

Usage:
    python -m lattice_lock.sheriff src/
    python -m lattice_lock.sheriff --json src/
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from lattice_lock.utils.safe_path import resolve_under_root


class ViolationSeverity(Enum):
    """Severity levels for Sheriff violations."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    """Represents a single Sheriff violation."""
    rule: str
    message: str
    file: str
    line: int
    column: int = 0
    severity: ViolationSeverity = ViolationSeverity.ERROR
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert violation to dictionary for JSON output."""
        return {
            "rule": self.rule,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
        }

    def __str__(self) -> str:
        prefix = "ERROR" if self.severity == ViolationSeverity.ERROR else "WARN"
        result = f"[{prefix}] {self.file}:{self.line}: {self.rule} - {self.message}"
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        return result


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
            "warning_count": sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING),
            "violations": [v.to_dict() for v in self.violations],
        }


# Configuration for Sheriff rules
DEFAULT_CONFIG = {
    "canonical_modules": {
        "types": "lattice_lock.types",
        "orchestrator": "lattice_lock_orchestrator.core",
        "api_clients": "lattice_lock_orchestrator.api_clients",
    },
    "forbidden_imports": [
        "requests",  # Use api_clients instead
        "psycopg2",  # Use SQLModel
        "sqlite3",   # Use SQLModel
    ],
    "path_hygiene_patterns": [
        'Path.home() / "Obsidian"',
        'Path.home() / "Downloads"',
        'Path.home() / "Desktop"',
        "os.path.expanduser",
        '"/Users/"',
        '"/home/"',
    ],
    "size_limits": {
        "max_function_lines": 100,
        "warn_function_lines": 50,
        "max_file_lines": 500,
    },
}


class SheriffVisitor(ast.NodeVisitor):
    """AST visitor that checks for Sheriff rule violations."""

    def __init__(self, filename: str, source_lines: list[str], config: dict) -> None:
        self.filename = filename
        self.source_lines = source_lines
        self.config = config
        self.violations: list[Violation] = []
        self.defined_names: dict[str, int] = {}  # name -> line number

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements for forbidden modules."""
        for alias in node.names:
            module_name = alias.name.split(".")[0]
            if module_name in self.config.get("forbidden_imports", []):
                self.violations.append(Violation(
                    rule="FORBIDDEN_IMPORT",
                    message=f"Forbidden import '{alias.name}'",
                    file=self.filename,
                    line=node.lineno,
                    severity=ViolationSeverity.ERROR,
                    suggestion=f"Use approved alternatives instead of '{module_name}'",
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from...import statements for forbidden modules."""
        if node.module:
            module_name = node.module.split(".")[0]
            if module_name in self.config.get("forbidden_imports", []):
                self.violations.append(Violation(
                    rule="FORBIDDEN_IMPORT",
                    message=f"Forbidden import from '{node.module}'",
                    file=self.filename,
                    line=node.lineno,
                    severity=ViolationSeverity.ERROR,
                    suggestion=f"Use approved alternatives instead of '{module_name}'",
                ))

            # Check for src. imports (legacy pattern)
            if node.module.startswith("src."):
                self.violations.append(Violation(
                    rule="LEGACY_IMPORT",
                    message=f"Legacy import pattern 'from src.{node.module[4:]}' detected",
                    file=self.filename,
                    line=node.lineno,
                    severity=ViolationSeverity.ERROR,
                    suggestion=f"Use 'from {node.module[4:]}' instead",
                ))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for type hints and size limits."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function definitions."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Common checks for function definitions."""
        # Check for duplicate definitions
        if node.name in self.defined_names:
            self.violations.append(Violation(
                rule="DUPLICATE_DEFINITION",
                message=f"Duplicate function definition '{node.name}'",
                file=self.filename,
                line=node.lineno,
                severity=ViolationSeverity.WARNING,
                suggestion=f"Previously defined at line {self.defined_names[node.name]}",
            ))
        else:
            self.defined_names[node.name] = node.lineno

        # Check for return type hint on public functions
        is_public = not node.name.startswith("_")
        if is_public and node.returns is None:
            self.violations.append(Violation(
                rule="MISSING_RETURN_TYPE",
                message=f"Public function '{node.name}' missing return type hint",
                file=self.filename,
                line=node.lineno,
                severity=ViolationSeverity.WARNING,
                suggestion=f"Add return type hint: def {node.name}(...) -> ReturnType:",
            ))

        # Check function size
        size_limits = self.config.get("size_limits", {})
        if node.end_lineno:
            func_lines = node.end_lineno - node.lineno
            max_lines = size_limits.get("max_function_lines", 100)
            warn_lines = size_limits.get("warn_function_lines", 50)

            if func_lines > max_lines:
                self.violations.append(Violation(
                    rule="FUNCTION_TOO_LONG",
                    message=f"Function '{node.name}' is {func_lines} lines (max: {max_lines})",
                    file=self.filename,
                    line=node.lineno,
                    severity=ViolationSeverity.ERROR,
                    suggestion="Consider breaking this function into smaller functions",
                ))
            elif func_lines > warn_lines:
                self.violations.append(Violation(
                    rule="FUNCTION_TOO_LONG",
                    message=f"Function '{node.name}' is {func_lines} lines (warn: {warn_lines})",
                    file=self.filename,
                    line=node.lineno,
                    severity=ViolationSeverity.WARNING,
                    suggestion="Consider refactoring for better maintainability",
                ))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for duplicates."""
        if node.name in self.defined_names:
            self.violations.append(Violation(
                rule="DUPLICATE_DEFINITION",
                message=f"Duplicate class definition '{node.name}'",
                file=self.filename,
                line=node.lineno,
                severity=ViolationSeverity.WARNING,
                suggestion=f"Previously defined at line {self.defined_names[node.name]}",
            ))
        else:
            self.defined_names[node.name] = node.lineno
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check string constants for hardcoded paths."""
        if isinstance(node.value, str):
            for pattern in self.config.get("path_hygiene_patterns", []):
                if pattern in node.value:
                    self.violations.append(Violation(
                        rule="HARDCODED_PATH",
                        message=f"Hardcoded path pattern detected: '{pattern}'",
                        file=self.filename,
                        line=node.lineno,
                        severity=ViolationSeverity.ERROR,
                        suggestion="Use configuration or environment variables for paths",
                    ))
        self.generic_visit(node)

    def check_source_patterns(self) -> None:
        """Check source code for patterns that AST doesn't catch."""
        for i, line in enumerate(self.source_lines, 1):
            # Check for Path.home() patterns
            for pattern in self.config.get("path_hygiene_patterns", []):
                if pattern in line and "# lattice:ignore" not in line:
                    self.violations.append(Violation(
                        rule="HARDCODED_PATH",
                        message=f"Hardcoded path pattern: '{pattern}'",
                        file=self.filename,
                        line=i,
                        severity=ViolationSeverity.ERROR,
                        suggestion="Use configuration or environment variables for paths",
                    ))


def analyze_file(filepath: Path, config: dict) -> list[Violation]:
    """Analyze a single Python file for Sheriff violations."""
    violations = []

    try:
        source = filepath.read_text(encoding="utf-8")
        source_lines = source.splitlines()
    except (OSError, UnicodeDecodeError) as e:
        violations.append(Violation(
            rule="FILE_READ_ERROR",
            message=str(e),
            file=str(filepath),
            line=0,
            severity=ViolationSeverity.ERROR,
        ))
        return violations

    # Check file size
    size_limits = config.get("size_limits", {})
    max_file_lines = size_limits.get("max_file_lines", 500)
    if len(source_lines) > max_file_lines:
        violations.append(Violation(
            rule="FILE_TOO_LONG",
            message=f"File has {len(source_lines)} lines (max: {max_file_lines})",
            file=str(filepath),
            line=1,
            severity=ViolationSeverity.WARNING,
            suggestion="Consider splitting into multiple modules",
        ))

    # Parse and analyze AST
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        violations.append(Violation(
            rule="SYNTAX_ERROR",
            message=str(e),
            file=str(filepath),
            line=e.lineno or 0,
            severity=ViolationSeverity.ERROR,
        ))
        return violations

    visitor = SheriffVisitor(str(filepath), source_lines, config)
    visitor.visit(tree)
    visitor.check_source_patterns()
    violations.extend(visitor.violations)

    return violations


def run_sheriff(
    target_path: str,
    config: Optional[dict] = None,
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
    if config is None:
        config = DEFAULT_CONFIG

    result = SheriffResult()
    target = Path(target_path)

    if not target.exists():
        result.add_violation(Violation(
            rule="PATH_NOT_FOUND",
            message=f"Target path does not exist: {target_path}",
            file=target_path,
            line=0,
            severity=ViolationSeverity.ERROR,
        ))
        return result

    # Collect Python files
    if target.is_file():
        python_files = [target] if target.suffix == ".py" else []
    else:
        python_files = list(target.rglob("*.py"))
        # Exclude common directories
        exclude_dirs = {"__pycache__", ".git", ".venv", "venv", "build", "dist", ".pytest_cache"}
        python_files = [
            f for f in python_files
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

    # Analyze each file
    for filepath in python_files:
        violations = analyze_file(filepath, config)
        for v in violations:
            result.add_violation(v)
        result.files_checked += 1

    return result


def main() -> None:
    """CLI entry point for Sheriff."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sheriff AST Validator for Lattice Lock Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m lattice_lock.sheriff src/
    python -m lattice_lock.sheriff --json src/
    python -m lattice_lock.sheriff src/lattice_lock/core.py
        """,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target file or directory to analyze (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (YAML or JSON)",
    )

    args = parser.parse_args()

    # Load config if provided
    config = DEFAULT_CONFIG
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                if config_path.suffix in (".yaml", ".yml"):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)

    # Run analysis
    try:
        target_path = resolve_under_root(args.target)
    except ValueError as e:
         print(f"Error: {e}")
         sys.exit(1)
         
    if args.config:
         try:
             resolve_under_root(args.config) # Just validate
         except ValueError as e:
             print(f"Error: {e}")
             sys.exit(1)

    result = run_sheriff(target_path, config)

    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.violations:
            for violation in result.violations:
                print(violation)
            print()

        status = "PASSED" if result.passed else "FAILED"
        print(f"Sheriff: {status}")
        print(f"Files checked: {result.files_checked}")
        print(f"Errors: {sum(1 for v in result.violations if v.severity == ViolationSeverity.ERROR)}")
        print(f"Warnings: {sum(1 for v in result.violations if v.severity == ViolationSeverity.WARNING)}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
