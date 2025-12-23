import ast

from lattice_lock.sheriff.ast_visitor import SheriffVisitor
from lattice_lock.sheriff.config import SheriffConfig
from lattice_lock.sheriff.rules import ImportDisciplineRule, RuleContext, TypeHintRule

# --- Config Tests ---


def test_config_defaults():
    config = SheriffConfig()
    assert config.forbidden_imports == []
    assert config.enforce_type_hints is True
    assert config.target_version == "current"


def test_config_from_yaml(tmp_path):
    yaml_content = """
config:
  forbidden_imports:
    - "os"
    - "sys"
  enforce_type_hints: false
  target_version: "1.0"
"""
    yaml_file = tmp_path / "lattice.yaml"
    yaml_file.write_text(yaml_content)

    config = SheriffConfig.from_yaml(str(yaml_file))
    assert "os" in config.forbidden_imports
    assert "sys" in config.forbidden_imports
    assert config.enforce_type_hints is False
    assert config.target_version == "1.0"


def test_config_missing_file():
    config = SheriffConfig.from_yaml("non_existent_file.yaml")
    assert config.forbidden_imports == []


# --- Rule Tests ---


def test_import_discipline_rule():
    config = SheriffConfig(forbidden_imports=["os"])
    context = RuleContext(filename="test.py", config=config)
    rule = ImportDisciplineRule()

    code = "import os"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 1
    assert violations[0].rule_id == "SHERIFF_001"

    code = "import sys"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 0


def test_import_from_discipline_rule():
    config = SheriffConfig(forbidden_imports=["os"])
    context = RuleContext(filename="test.py", config=config)
    rule = ImportDisciplineRule()

    code = "from os import path"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 1
    assert violations[0].rule_id == "SHERIFF_001"


def test_type_hint_rule():
    config = SheriffConfig(enforce_type_hints=True)
    context = RuleContext(filename="test.py", config=config)
    rule = TypeHintRule()

    code = "def my_func(a): pass"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 1
    assert violations[0].rule_id == "SHERIFF_002"

    code = "def my_func(a) -> None: pass"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 0


def test_type_hint_rule_disabled():
    config = SheriffConfig(enforce_type_hints=False)
    context = RuleContext(filename="test.py", config=config)
    rule = TypeHintRule()

    code = "def my_func(a): pass"
    node = ast.parse(code).body[0]
    violations = rule.check(node, context)
    assert len(violations) == 0


# --- Visitor Tests ---


def test_visitor_collects_violations():
    config = SheriffConfig(forbidden_imports=["os"], enforce_type_hints=True)
    source_code = """
import os
def foo():
    pass
"""
    visitor = SheriffVisitor("test.py", config, source_code)
    visitor.visit(ast.parse(source_code))
    violations = visitor.get_violations()

    assert len(violations) == 2
    rule_ids = [v.rule_id for v in violations]
    assert "SHERIFF_001" in rule_ids
    assert "SHERIFF_002" in rule_ids


def test_visitor_ignore_comments():
    config = SheriffConfig(forbidden_imports=["os"])
    source_code = """
import os # lattice:ignore
import sys
"""
    visitor = SheriffVisitor("test.py", config, source_code)
    visitor.visit(ast.parse(source_code))
    violations = visitor.get_violations()

    assert len(violations) == 0


def test_visitor_ignore_comments_specific_line():
    config = SheriffConfig(forbidden_imports=["os"])
    source_code = """
import os # lattice:ignore
import os
"""
    visitor = SheriffVisitor("test.py", config, source_code)
    visitor.visit(ast.parse(source_code))
    violations = visitor.get_violations()

    assert len(violations) == 1
    assert violations[0].line_number == 3
