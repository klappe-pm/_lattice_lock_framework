import ast

from lattice_lock.sheriff.config import SheriffConfig, ViolationSeverity
from lattice_lock.sheriff.rules import RuleContext, VersionComplianceRule


def test_version_compliance_match():
    rule = VersionComplianceRule()
    config = SheriffConfig(target_version="2.1.0")
    context = RuleContext(filename="test.py", config=config)

    node = ast.parse('__version__ = "2.1.0"').body[0]
    violations = rule.check(node, context)

    assert len(violations) == 0


def test_version_compliance_mismatch():
    rule = VersionComplianceRule()
    config = SheriffConfig(target_version="2.1.0")
    context = RuleContext(filename="test.py", config=config)

    node = ast.parse('__version__ = "2.0.0"').body[0]
    violations = rule.check(node, context)

    assert len(violations) == 1
    assert violations[0].rule_id == "SHERIFF_003"
    assert "Version mismatch" in violations[0].message
    assert violations[0].severity == ViolationSeverity.WARNING


def test_version_compliance_current_skips():
    rule = VersionComplianceRule()
    # "current" is the default and should skip the check
    config = SheriffConfig(target_version="current")
    context = RuleContext(filename="test.py", config=config)

    node = ast.parse('__version__ = "2.0.0"').body[0]
    violations = rule.check(node, context)

    assert len(violations) == 0


def test_version_compliance_multiple_targets():
    rule = VersionComplianceRule()
    config = SheriffConfig(target_version="2.1.0")
    context = RuleContext(filename="test.py", config=config)

    # __version__ = ver = "2.0.0"
    node = ast.parse('__version__ = ver = "2.0.0"').body[0]
    violations = rule.check(node, context)

    assert len(violations) == 1
    assert "Version mismatch" in violations[0].message
