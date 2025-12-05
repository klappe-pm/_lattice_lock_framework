import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from .config import SheriffConfig

@dataclass
class RuleContext:
    """Context passed to rules during validation."""
    filename: str
    config: SheriffConfig

@dataclass
class Violation:
    """Represents a rule violation."""
    rule_id: str
    message: str
    line_number: int
    filename: str # Added filename to Violation

class Rule(ABC):
    """Abstract base class for Sheriff rules."""
    @abstractmethod
    def check(self, node: ast.AST, context: RuleContext) -> List[Violation]:
        """Checks an AST node for violations."""
        pass

class ImportDisciplineRule(Rule):
    """Enforces import restrictions based on configuration."""
    def check(self, node: ast.AST, context: RuleContext) -> List[Violation]:
        violations = []
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module_name = None
            if isinstance(node, ast.Import):
                for name in node.names:
                    module_name = name.name
                    self._check_import(module_name, node, context, violations)
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                self._check_import(module_name, node, context, violations)
        return violations

    def _check_import(self, module_name: Optional[str], node: ast.AST, context: RuleContext, violations: List[Violation]):
        if not module_name:
            return
            
        # Check if the imported module starts with any of the forbidden imports
        for forbidden in context.config.forbidden_imports:
            if module_name == forbidden or module_name.startswith(f"{forbidden}."):
                violations.append(Violation(
                    rule_id="SHERIFF_001",
                    message=f"Forbidden import detected: {module_name}",
                    line_number=node.lineno,
                    filename=context.filename
                ))

class TypeHintRule(Rule):
    """Enforces type hints on function definitions."""
    def check(self, node: ast.AST, context: RuleContext) -> List[Violation]:
        violations = []
        if not context.config.enforce_type_hints:
            return violations

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip checking __init__ or other magic methods if desired, but for now enforcing on all
            if node.returns is None:
                violations.append(Violation(
                    rule_id="SHERIFF_002",
                    message=f"Missing return type hint for function '{node.name}'",
                    line_number=node.lineno,
                    filename=context.filename
                ))
        return violations

class VersionComplianceRule(Rule):
    """Checks for version compliance issues."""
    def check(self, node: ast.AST, context: RuleContext) -> List[Violation]:
        # Placeholder for version compliance logic
        # Could check for deprecated features or version-specific syntax
        return []
