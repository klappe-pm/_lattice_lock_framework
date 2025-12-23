import ast
import tokenize
from io import BytesIO

from .config import SheriffConfig
from .rules import (
    ImportDisciplineRule,
    Rule,
    RuleContext,
    TypeHintRule,
    VersionComplianceRule,
    Violation,
)


class SheriffVisitor(ast.NodeVisitor):
    """
    AST Visitor that applies Sheriff rules to the code.

    Attributes:
        filename (str): The name of the file being visited.
        config (SheriffConfig): The Sheriff configuration.
        source_code (str): The source code of the file.
        violations (List[Violation]): List of violations found.
        ignored_violations (List[Violation]): List of violations that were ignored via comments.
    """

    def __init__(self, filename: str, config: SheriffConfig, source_code: str):
        self.filename = filename
        self.config = config
        self.source_code = source_code
        self.context = RuleContext(filename=filename, config=config)
        self.violations: list[Violation] = []
        self.ignored_violations: list[Violation] = []
        self.ignored_lines: set[int] = self._parse_ignore_comments(source_code)

        # Initialize rules
        self.rules: list[Rule] = [ImportDisciplineRule(), TypeHintRule(), VersionComplianceRule()]

    def _parse_ignore_comments(self, source: str) -> set[int]:
        """Parses comments to find ignore directives (lattice:ignore)."""
        ignored = set()
        try:
            tokens = tokenize.tokenize(BytesIO(source.encode("utf-8")).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    if "lattice:ignore" in token.string:
                        ignored.add(token.start[0])
        except tokenize.TokenError:
            pass
        return ignored

    def visit(self, node: ast.AST):
        """Visits an AST node and applies rules."""
        # Apply rules to the current node
        for rule in self.rules:
            node_violations = rule.check(node, self.context)
            for violation in node_violations:
                if violation.line_number not in self.ignored_lines:
                    self.violations.append(violation)
                else:
                    self.ignored_violations.append(violation)

        # Continue traversal
        self.generic_visit(node)

    def get_violations(self) -> list[Violation]:
        """Returns the list of active violations."""
        return self.violations

    def get_ignored_violations(self) -> list[Violation]:
        """Returns the list of ignored violations."""
        return self.ignored_violations
