#!/usr/bin/env python3
"""
Automated Agent Definition Validator

Programmatically validates agent YAML files against the Lattice Lock Framework v2.1 spec.
No LLM required - uses pure Python validation.

Usage:
    # Validate single file
    python3 validate_agents.py path/to/agent.yaml

    # Validate entire domain
    python3 validate_agents.py --domain engineering

    # Validate all agents
    python3 validate_agents.py --all

    # Output JSON report
    python3 validate_agents.py --all --json --output report.json

    # Verbose mode (show passed checks too)
    python3 validate_agents.py --domain ux --verbose

    # Fix mode (auto-fix simple issues)
    python3 validate_agents.py --domain content --fix --dry-run
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install with: pip3 install pyyaml")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

VALID_DOMAINS = {
    "business_review",
    "cloud",
    "content",
    "context",
    "education",
    "engineering",
    "financial",
    "google_apps_script",
    "model_orchestration",
    "product",
    "product_management",
    "project",
    "project_management",
    "prompt_architect",
    "public_relations",
    "research",
    "ux",
}

VALID_BASE_TEMPLATES = {"base_agent", "base_agent_v2.1", "base_subagent", "base_model"}

REQUIRED_SECTIONS = ["identity", "directive", "scope"]
REQUIRED_IDENTITY_FIELDS = ["name", "version", "description", "role"]

SEMVER_PATTERN = re.compile(r'^"?\d+\.\d+\.\d+"?$')
KEBAB_SNAKE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")

ACTION_VERBS = {
    "analyze",
    "audit",
    "build",
    "calculate",
    "check",
    "configure",
    "coordinate",
    "create",
    "debug",
    "define",
    "deploy",
    "design",
    "detect",
    "develop",
    "document",
    "enforce",
    "ensure",
    "establish",
    "evaluate",
    "execute",
    "extract",
    "facilitate",
    "generate",
    "handle",
    "identify",
    "implement",
    "improve",
    "integrate",
    "investigate",
    "maintain",
    "manage",
    "monitor",
    "optimize",
    "orchestrate",
    "organize",
    "perform",
    "plan",
    "prepare",
    "process",
    "produce",
    "provide",
    "research",
    "resolve",
    "review",
    "route",
    "run",
    "scan",
    "schedule",
    "secure",
    "select",
    "standardize",
    "streamline",
    "support",
    "sync",
    "test",
    "track",
    "transform",
    "translate",
    "update",
    "validate",
    "verify",
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ValidationIssue:
    rule: str
    severity: str  # "error", "warning", "info"
    message: str
    fix: str | None = None
    line: int | None = None
    auto_fixable: bool = False


@dataclass
class ValidationResult:
    file: str
    valid: bool
    score: int
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    info: list[ValidationIssue] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        parts.append(f"{len(self.passed_checks)} checks passed")
        return ", ".join(parts)

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "valid": self.valid,
            "score": self.score,
            "errors": [vars(e) for e in self.errors],
            "warnings": [vars(w) for w in self.warnings],
            "info": [vars(i) for i in self.info],
            "passed_checks": self.passed_checks,
            "summary": self.summary,
        }


@dataclass
class BatchResult:
    total_files: int
    valid: int
    invalid: int
    total_errors: int
    total_warnings: int
    average_score: float
    results: list[ValidationResult] = field(default_factory=list)
    common_issues: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "batch_summary": {
                "total_files": self.total_files,
                "valid": self.valid,
                "invalid": self.invalid,
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "average_score": round(self.average_score, 1),
            },
            "common_issues": [
                {"rule": rule, "count": len(files), "affected_files": files}
                for rule, files in sorted(self.common_issues.items(), key=lambda x: -len(x[1]))
            ],
            "results": [r.to_dict() for r in self.results],
        }


# =============================================================================
# Validators
# =============================================================================


class AgentValidator:
    """Validates a single agent YAML file."""

    def __init__(self, file_path: Path, base_dir: Path, all_agents: set[str] = None):
        self.file_path = file_path
        self.base_dir = base_dir
        self.relative_path = str(file_path.relative_to(base_dir))
        self.all_agents = all_agents or set()
        self.data: dict | None = None
        self.result = ValidationResult(file=self.relative_path, valid=True, score=100)

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        # Check 1: YAML syntax
        if not self._check_yaml_syntax():
            self.result.valid = False
            self.result.score = 0
            return self.result

        # Check 2: Required sections
        self._check_required_sections()

        # Check 3: Identity fields
        self._check_identity_fields()

        # Check 4: Naming convention
        self._check_naming_convention()

        # Check 5: Version format
        self._check_version_format()

        # Check 6: Directive format
        self._check_directive_format()

        # Check 7: Scope validity
        self._check_scope_validity()

        # Check 8: Tag consistency
        self._check_tag_consistency()

        # Check 9: Delegation rules
        self._check_delegation_rules()

        # Check 10: Inheritance
        self._check_inheritance()

        # Check 11: Subagent rules
        self._check_subagent_rules()

        # Check 12: Placeholder detection
        self._check_placeholders()

        # Calculate final score and validity
        error_penalty = len(self.result.errors) * 15
        warning_penalty = len(self.result.warnings) * 5
        self.result.score = max(0, 100 - error_penalty - warning_penalty)
        self.result.valid = len(self.result.errors) == 0

        return self.result

    def _check_yaml_syntax(self) -> bool:
        """Check if YAML is valid."""
        try:
            with open(self.file_path) as f:
                self.data = yaml.safe_load(f)

            if self.data is None:
                self._add_error("yaml_syntax", "File is empty or contains only comments")
                return False

            if not isinstance(self.data, dict):
                self._add_error("yaml_syntax", "Root element must be a mapping")
                return False

            self.result.passed_checks.append("yaml_syntax")
            return True

        except yaml.YAMLError as e:
            self._add_error("yaml_syntax", f"YAML parse error: {e}")
            return False
        except Exception as e:
            self._add_error("yaml_syntax", f"File read error: {e}")
            return False

    def _check_required_sections(self):
        """Check for required top-level sections."""
        agent = self.data.get("agent", {})

        if not agent:
            self._add_error(
                "schema_compliance",
                "Missing 'agent' root section",
                fix="Add 'agent:' as the root element",
            )
            return

        missing = [s for s in REQUIRED_SECTIONS if s not in agent]
        if missing:
            self._add_error(
                "schema_compliance",
                f"Missing required sections: {', '.join(missing)}",
                fix=f"Add missing sections: {', '.join(missing)}",
            )
        else:
            self.result.passed_checks.append("required_sections")

    def _check_identity_fields(self):
        """Check identity section fields."""
        identity = self._get_section("identity")
        if not identity:
            return

        missing = [f for f in REQUIRED_IDENTITY_FIELDS if not identity.get(f)]
        if missing:
            self._add_error(
                "schema_compliance",
                f"Missing required identity fields: {', '.join(missing)}",
                fix=f"Add: {', '.join([f'{f}: \"value\"' for f in missing])}",
            )
        else:
            self.result.passed_checks.append("identity_fields")

        # Check name format
        name = identity.get("name", "")
        if name and not KEBAB_SNAKE_PATTERN.match(name):
            self._add_warning(
                "naming_convention",
                f"Agent name should be lowercase with underscores/hyphens: '{name}'",
                fix="Use snake_case or kebab-case",
            )

    def _check_naming_convention(self):
        """Check file naming matches identity.name."""
        identity = self._get_section("identity")
        if not identity:
            return

        name = identity.get("name", "")
        filename = self.file_path.stem  # Without extension

        # Expected pattern: {name}_definition
        expected_filename = f"{name}_definition"

        if filename != expected_filename:
            self._add_warning(
                "naming_convention",
                f"Filename '{filename}' doesn't match identity.name '{name}'",
                fix=f"Rename file to '{expected_filename}.yaml' or change name to '{filename.replace('_definition', '')}'",
            )
        else:
            self.result.passed_checks.append("naming_convention")

    def _check_version_format(self):
        """Check version is valid semver."""
        identity = self._get_section("identity")
        if not identity:
            return

        version = identity.get("version")
        if version is None:
            return  # Already caught by required fields check

        version_str = str(version)

        # Must be semver format
        if not SEMVER_PATTERN.match(version_str):
            self._add_error(
                "version_format",
                f"Version must be semver format (X.Y.Z): got '{version}'",
                fix='Use format like version: "1.0.0"',
                auto_fixable=True,
            )
        else:
            self.result.passed_checks.append("version_format")

        # Should be quoted string
        if isinstance(version, (int, float)):
            self._add_warning(
                "version_format",
                "Version should be a quoted string",
                fix=f'Change to: version: "{version}"',
                auto_fixable=True,
            )

    def _check_directive_format(self):
        """Check directive section."""
        directive = self._get_section("directive")
        if not directive:
            return

        primary_goal = directive.get("primary_goal", "")
        if not primary_goal:
            self._add_error(
                "directive_format",
                "Missing primary_goal in directive section",
                fix="Add primary_goal with action verb",
            )
            return

        # Check starts with action verb
        first_word = primary_goal.split()[0].lower().rstrip("s")  # Handle plurals
        if first_word not in ACTION_VERBS:
            self._add_warning(
                "directive_format",
                f"primary_goal should start with action verb, got: '{first_word}'",
                fix="Rewrite to start with verb like: Manage, Analyze, Execute...",
            )
        else:
            self.result.passed_checks.append("directive_format")

    def _check_scope_validity(self):
        """Check scope section validity."""
        scope = self._get_section("scope")
        if not scope:
            return

        can_access = scope.get("can_access", [])
        if not can_access:
            self._add_warning(
                "scope_consistency",
                "scope.can_access is empty or missing",
                fix="Add list of accessible paths",
            )
        else:
            # Check for overly broad access
            broad_patterns = ["/", "/*", "**", "all", "everything"]
            for path in can_access:
                if str(path).lower() in broad_patterns:
                    self._add_warning(
                        "scope_consistency",
                        f"Overly broad access pattern: '{path}'",
                        fix="Limit to specific directories",
                    )

            self.result.passed_checks.append("scope_validity")

        # Check can_modify is subset of can_access
        can_modify = scope.get("can_modify", [])
        if can_modify and can_access:
            # Simple check - not comprehensive path matching
            modify_set = set(str(p) for p in can_modify)
            access_set = set(str(p) for p in can_access)
            if not modify_set.issubset(access_set):
                extra = modify_set - access_set
                self._add_info(
                    "scope_consistency",
                    f"can_modify paths not in can_access: {extra}",
                    fix="Add these paths to can_access or remove from can_modify",
                )

    def _check_tag_consistency(self):
        """Check tags include domain and are properly formatted."""
        identity = self._get_section("identity")
        if not identity:
            return

        tags = identity.get("tags", [])
        if not tags:
            self._add_warning(
                "tag_consistency", "No tags defined", fix="Add relevant tags including domain"
            )
            return

        # Extract domain from file path
        parts = self.relative_path.split("/")
        domain = None
        for part in parts:
            if part.startswith("agents_"):
                domain = part.replace("agents_", "")
                break

        if domain:
            # Check domain tag exists
            tag_values = [str(t).lower() for t in tags]
            domain_variants = [domain, domain.replace("_", "-"), domain.replace("-", "_")]

            if not any(d in tag_values for d in domain_variants):
                self._add_warning(
                    "tag_consistency",
                    f"Missing domain tag '{domain}'",
                    fix=f"Add '{domain}' to tags",
                )

        # Check for subagent tag if in subagents directory
        if "/subagents/" in self.relative_path:
            if "subagent" not in [str(t).lower() for t in tags]:
                self._add_warning(
                    "tag_consistency",
                    "Subagent missing 'subagent' tag",
                    fix="Add 'subagent' to tags",
                )

        # Check tag format
        for tag in tags:
            tag_str = str(tag)
            if tag_str != tag_str.lower():
                self._add_warning(
                    "tag_consistency",
                    f"Tag should be lowercase: '{tag}'",
                    fix=f"Change to '{tag_str.lower()}'",
                )
            if " " in tag_str:
                self._add_error(
                    "tag_consistency",
                    f"Tag cannot contain spaces: '{tag}'",
                    fix=f"Use underscore or hyphen: '{tag_str.replace(' ', '_')}'",
                )

        self.result.passed_checks.append("tag_format")

    def _check_delegation_rules(self):
        """Check delegation configuration."""
        delegation = self._get_section("delegation")
        if not delegation:
            self.result.passed_checks.append("delegation_rules")
            return

        enabled = delegation.get("enabled", False)

        if enabled:
            # Must have targets
            targets = delegation.get("allowed_subagents") or delegation.get("can_delegate_to") or []

            if not targets:
                self._add_error(
                    "delegation_rules",
                    "Delegation enabled but no allowed_subagents defined",
                    fix="Add allowed_subagents list or set enabled: false",
                )
            else:
                # Check targets exist (if we have all_agents context)
                if self.all_agents:
                    for target in targets:
                        # Handle dict format: {name: x, file: y}
                        if isinstance(target, dict):
                            target_name = target.get("name", "")
                        else:
                            target_name = str(target)

                        # Handle glob patterns
                        if "*" in target_name:
                            continue
                        if target_name and target_name not in self.all_agents:
                            self._add_warning(
                                "dependency_check",
                                f"Delegation target not found: '{target_name}'",
                                fix="Create subagent or remove from list",
                            )

                self.result.passed_checks.append("delegation_rules")

    def _check_inheritance(self):
        """Check inheritance configuration."""
        inheritance = self._get_section("inheritance")
        if not inheritance:
            # Not required, but recommended
            self._add_info(
                "inheritance",
                "No inheritance section - consider extending base_agent_v2.1",
                fix="Add: inheritance:\n  extends: base_agent_v2.1",
            )
            return

        extends = inheritance.get("extends")
        if extends and extends not in VALID_BASE_TEMPLATES:
            self._add_warning(
                "inheritance",
                f"Unknown base template: '{extends}'",
                fix=f"Use one of: {', '.join(sorted(VALID_BASE_TEMPLATES))}",
            )
        else:
            self.result.passed_checks.append("inheritance")

    def _check_subagent_rules(self):
        """Check subagent-specific rules."""
        if "/subagents/" not in self.relative_path:
            return

        # Subagents should not delegate (by default)
        delegation = self._get_section("delegation")
        if delegation and delegation.get("enabled", False):
            self._add_info(
                "subagent_rules",
                "Subagent has delegation enabled - typically subagents don't delegate",
                fix="Set delegation.enabled: false unless intentional",
            )

        self.result.passed_checks.append("subagent_rules")

    def _check_placeholders(self):
        """Check for placeholder text."""
        content = self.file_path.read_text()

        placeholders = [
            r"\[TODO\]",
            r"\[FILL[_ ]?IN\]",
            r"\[PLACEHOLDER\]",
            r"\[INSERT\]",
            r"\[CHANGE[_ ]?ME\]",
            r"\[YOUR[_ ]\w+\]",
            r"<PLACEHOLDER>",
            r"TBD",
            r"TODO:",
        ]

        for pattern in placeholders:
            if re.search(pattern, content, re.IGNORECASE):
                self._add_warning(
                    "placeholder_detection",
                    f"Found placeholder text matching: {pattern}",
                    fix="Replace placeholder with actual content",
                )
                return

        self.result.passed_checks.append("no_placeholders")

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_section(self, name: str) -> dict | None:
        """Get a section from agent data."""
        if not self.data:
            return None
        return self.data.get("agent", {}).get(name, {})

    def _add_error(self, rule: str, message: str, fix: str = None, auto_fixable: bool = False):
        self.result.errors.append(
            ValidationIssue(
                rule=rule, severity="error", message=message, fix=fix, auto_fixable=auto_fixable
            )
        )

    def _add_warning(self, rule: str, message: str, fix: str = None, auto_fixable: bool = False):
        self.result.warnings.append(
            ValidationIssue(
                rule=rule, severity="warning", message=message, fix=fix, auto_fixable=auto_fixable
            )
        )

    def _add_info(self, rule: str, message: str, fix: str = None):
        self.result.info.append(
            ValidationIssue(rule=rule, severity="info", message=message, fix=fix)
        )


# =============================================================================
# Batch Validation
# =============================================================================


def validate_batch(files: list[Path], base_dir: Path) -> BatchResult:
    """Validate multiple files and aggregate results."""
    # First pass: collect all agent names
    all_agents = set()
    for f in files:
        try:
            with open(f) as fp:
                data = yaml.safe_load(fp)
                name = data.get("agent", {}).get("identity", {}).get("name")
                if name:
                    all_agents.add(name)
        except Exception:
            pass

    # Second pass: validate with context
    results = []
    for f in files:
        validator = AgentValidator(f, base_dir, all_agents)
        results.append(validator.validate())

    # Aggregate
    valid_count = sum(1 for r in results if r.valid)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    avg_score = sum(r.score for r in results) / len(results) if results else 0

    # Find common issues
    common_issues: dict[str, list[str]] = {}
    for r in results:
        for e in r.errors + r.warnings:
            if e.rule not in common_issues:
                common_issues[e.rule] = []
            if r.file not in common_issues[e.rule]:
                common_issues[e.rule].append(r.file)

    return BatchResult(
        total_files=len(files),
        valid=valid_count,
        invalid=len(files) - valid_count,
        total_errors=total_errors,
        total_warnings=total_warnings,
        average_score=avg_score,
        results=results,
        common_issues=common_issues,
    )


# =============================================================================
# Output Formatting
# =============================================================================


def print_result(result: ValidationResult, verbose: bool = False):
    """Print a single validation result."""
    status = "✅ VALID" if result.valid else "❌ INVALID"
    print(f"\n{status} [{result.score}/100] {result.file}")

    if result.errors:
        print("  Errors:")
        for e in result.errors:
            print(f"    ❌ [{e.rule}] {e.message}")
            if e.fix:
                print(f"       Fix: {e.fix}")

    if result.warnings:
        print("  Warnings:")
        for w in result.warnings:
            print(f"    ⚠️  [{w.rule}] {w.message}")
            if w.fix:
                print(f"       Fix: {w.fix}")

    if verbose:
        if result.info:
            print("  Info:")
            for i in result.info:
                print(f"    ℹ️  [{i.rule}] {i.message}")

        if result.passed_checks:
            print(f"  Passed: {', '.join(result.passed_checks)}")


def print_batch_summary(batch: BatchResult):
    """Print batch validation summary."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Files:    {batch.total_files}")
    print(f"Valid:          {batch.valid} ({batch.valid/batch.total_files*100:.1f}%)")
    print(f"Invalid:        {batch.invalid}")
    print(f"Total Errors:   {batch.total_errors}")
    print(f"Total Warnings: {batch.total_warnings}")
    print(f"Average Score:  {batch.average_score:.1f}/100")

    if batch.common_issues:
        print("\nMost Common Issues:")
        for rule, files in sorted(batch.common_issues.items(), key=lambda x: -len(x[1]))[:5]:
            print(f"  - {rule}: {len(files)} files")


# =============================================================================
# Main
# =============================================================================


def find_agent_files(base_dir: Path, domain: str | None = None) -> list[Path]:
    """Find agent YAML files."""
    agent_defs = base_dir / "agent_definitions"

    if domain:
        domain_dir = agent_defs / f"agents_{domain}"
        if not domain_dir.exists():
            print(f"Error: Domain not found: {domain}")
            return []
        return sorted(domain_dir.rglob("*.yaml"))

    return sorted(agent_defs.rglob("*.yaml"))


def main():
    parser = argparse.ArgumentParser(
        description="Validate agent YAML files against v2.1 spec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("file", nargs="?", help="Single YAML file to validate")
    parser.add_argument("--domain", "-d", help="Validate entire domain")
    parser.add_argument("--all", "-a", action="store_true", help="Validate all agents")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file for JSON report")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show all checks including passed"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Only show errors")
    parser.add_argument("--list-domains", "-l", action="store_true", help="List available domains")

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    base_dir = script_dir

    if args.list_domains:
        agent_defs = base_dir / "agent_definitions"
        print("Available domains:")
        for d in sorted(agent_defs.iterdir()):
            if d.is_dir() and d.name.startswith("agents_"):
                count = len(list(d.rglob("*.yaml")))
                domain = d.name.replace("agents_", "")
                print(f"  {domain}: {count} agents")
        return 0

    # Determine files
    files = []
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            file_path = base_dir / args.file
        if not file_path.exists():
            print(f"Error: File not found: {args.file}")
            return 1
        files = [file_path]
    elif args.domain:
        files = find_agent_files(base_dir, args.domain)
    elif args.all:
        files = find_agent_files(base_dir)
    else:
        parser.print_help()
        return 1

    if not files:
        print("No files found to validate")
        return 1

    print(f"Validating {len(files)} agent file(s)...")

    # Validate
    if len(files) == 1:
        validator = AgentValidator(files[0], base_dir)
        result = validator.validate()

        if args.json:
            output = json.dumps(result.to_dict(), indent=2)
            if args.output:
                Path(args.output).write_text(output)
                print(f"Wrote report to: {args.output}")
            else:
                print(output)
        else:
            print_result(result, verbose=args.verbose)

        return 0 if result.valid else 1

    else:
        batch = validate_batch(files, base_dir)

        if args.json:
            output = json.dumps(batch.to_dict(), indent=2)
            if args.output:
                Path(args.output).write_text(output)
                print(f"Wrote report to: {args.output}")
            else:
                print(output)
        else:
            if not args.quiet:
                for r in batch.results:
                    if not r.valid or args.verbose:
                        print_result(r, verbose=args.verbose)

            print_batch_summary(batch)

        return 0 if batch.invalid == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
