import ast
import tokenize
from typing import List, Set
from io import BytesIO
from .config import SheriffConfig
from .rules import Rule, RuleContext, Violation, ImportDisciplineRule, TypeHintRule, VersionComplianceRule

class SheriffVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, config: SheriffConfig, source_code: str):
        self.filename = filename
        self.config = config
        self.source_code = source_code
        self.context = RuleContext(filename=filename, config=config)
        self.violations: List[Violation] = []
        self.ignored_lines: Set[int] = self._parse_ignore_comments(source_code)
        
        # Initialize rules
        self.rules: List[Rule] = [
            ImportDisciplineRule(),
            TypeHintRule(),
            VersionComplianceRule()
        ]

    def _parse_ignore_comments(self, source: str) -> Set[int]:
        ignored = set()
        try:
            tokens = tokenize.tokenize(BytesIO(source.encode('utf-8')).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    if "lattice:ignore" in token.string:
                        ignored.add(token.start[0])
        except tokenize.TokenError:
            pass
        return ignored

    def visit(self, node: ast.AST):
        # Apply rules to the current node
        for rule in self.rules:
            node_violations = rule.check(node, self.context)
            for violation in node_violations:
                if violation.line_number not in self.ignored_lines:
                    self.violations.append(violation)
        
        # Continue traversal
        self.generic_visit(node)

    def get_violations(self) -> List[Violation]:
        return self.violations
