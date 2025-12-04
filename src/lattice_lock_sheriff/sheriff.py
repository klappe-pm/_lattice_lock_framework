import ast
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from .config import SheriffConfig
from .ast_visitor import SheriffVisitor
from .rules import Violation as RuleViolation

@dataclass
class Violation:
    file: Path
    line: int
    column: int
    message: str
    rule: str
    code: Optional[str] = None

def validate_file(file_path: Path, config: SheriffConfig, ignore_patterns: List[str]) -> List[Violation]:
    if not file_path.suffix == ".py":
        return []

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
        cli_violations = []
        for rv in visitor.get_violations():
            # Get code snippet
            code_snippet = file_lines[rv.line_number - 1].strip() if 0 <= rv.line_number - 1 < len(file_lines) else None
            
            cli_violations.append(Violation(
                file=file_path,
                line=rv.line_number,
                column=0, # Column not currently captured by RuleViolation
                message=rv.message,
                rule=rv.rule_id,
                code=code_snippet
            ))
            
        return cli_violations

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
        ]
    except Exception as e:
        return [
            Violation(
                file=file_path,
                line=0,
                column=0,
                message=f"Error parsing file: {e}",
                rule="ParseError"
            )
        ]

def validate_path(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: Optional[List[str]] = None,
) -> List[Violation]:
    if ignore_patterns is None:
        ignore_patterns = []

    violations: List[Violation] = []
    
    # Check if path is ignored
    for pattern in ignore_patterns:
        if path.match(pattern):
            return []

    if path.is_file():
        if path.suffix == ".py":
             # Apply file-level ignore patterns
            for pattern in ignore_patterns:
                if path.match(pattern):
                    return []
            violations.extend(validate_file(path, config, ignore_patterns))
            
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

                    violations.extend(validate_file(file_path, config, ignore_patterns))
    return violations
