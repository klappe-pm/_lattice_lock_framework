#!/usr/bin/env python3
"""
Automated Agent Definition Fixer

Applies bulk fixes to agent YAML files based on validation results.

Usage:
    # Preview all fixes (dry run)
    python3 fix_agents.py --all --dry-run

    # Apply all safe fixes
    python3 fix_agents.py --all

    # Fix specific issue types
    python3 fix_agents.py --fix tags --all
    python3 fix_agents.py --fix names --all
    python3 fix_agents.py --fix scope --all

    # Fix specific domain
    python3 fix_agents.py --domain engineering

    # Generate fix report
    python3 fix_agents.py --all --report fixes.json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: pyyaml required. Install with: pip3 install pyyaml")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

# Domain mappings
DOMAIN_TAGS = {
    "business_review": ["business_review", "business", "review"],
    "cloud": ["cloud", "infrastructure"],
    "content": ["content", "writing"],
    "context": ["context", "memory"],
    "education": ["education", "training"],
    "engineering": ["engineering", "development"],
    "financial": ["financial", "finance"],
    "google_apps_script": ["google_apps_script", "gas", "automation"],
    "model_orchestration": ["model_orchestration", "orchestration", "llm"],
    "product_management": ["product_management", "product"],
    "project_management": ["project_management", "project"],
    "prompt_architect": ["prompt_architect", "prompt"],
    "public_relations": ["public_relations", "pr", "communications"],
    "research": ["research", "analysis"],
    "ux": ["ux", "design", "user_experience"],
}

# Default scope for subagents
DEFAULT_SUBAGENT_SCOPE = {
    "can_access": ["/docs", "/src"],
}

# Default scope for main agents
DEFAULT_MAIN_AGENT_SCOPE = {
    "can_access": ["/agents/definitions", "/docs", "/src"],
    "can_modify": ["/agents/outputs"],
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Fix:
    file: str
    fix_type: str
    description: str
    before: Any = None
    after: Any = None
    applied: bool = False


@dataclass
class FixReport:
    total_files: int = 0
    files_modified: int = 0
    fixes_applied: int = 0
    fixes_skipped: int = 0
    fixes: list[Fix] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "summary": {
                "total_files": self.total_files,
                "files_modified": self.files_modified,
                "fixes_applied": self.fixes_applied,
                "fixes_skipped": self.fixes_skipped,
            },
            "fixes": [
                {
                    "file": f.file,
                    "type": f.fix_type,
                    "description": f.description,
                    "applied": f.applied,
                }
                for f in self.fixes
            ],
        }


# =============================================================================
# YAML Handling (preserve formatting)
# =============================================================================


class PreservingDumper(yaml.SafeDumper):
    """Custom YAML dumper that preserves formatting."""

    pass


def str_representer(dumper, data):
    """Handle multiline strings properly."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


PreservingDumper.add_representer(str, str_representer)


def load_yaml(file_path: Path) -> tuple[dict | None, str | None]:
    """Load YAML file and return data and raw content."""
    try:
        content = file_path.read_text()
        data = yaml.safe_load(content)
        return data, content
    except Exception:
        return None, None


def save_yaml(file_path: Path, data: dict):
    """Save YAML file with proper formatting."""
    content = yaml.dump(
        data,
        Dumper=PreservingDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    file_path.write_text(content)


# =============================================================================
# Fix Functions
# =============================================================================


def extract_domain(file_path: Path) -> str | None:
    """Extract domain from file path."""
    parts = str(file_path).split("/")
    for part in parts:
        if part.startswith("agents_"):
            return part.replace("agents_", "")
    return None


def is_subagent(file_path: Path) -> bool:
    """Check if file is a subagent."""
    return "/subagents/" in str(file_path)


def fix_tags(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Fix missing or incorrect tags."""
    fixes = []
    agent = data.get("agent", {})
    identity = agent.get("identity", {})

    domain = extract_domain(file_path)
    is_sub = is_subagent(file_path)

    current_tags = identity.get("tags", [])
    if current_tags is None:
        current_tags = []

    new_tags = list(current_tags)  # Copy
    tags_added = []

    # Add domain tag if missing
    if domain:
        domain_tag = domain.replace("-", "_")
        tag_variants = [t.lower().replace("-", "_") for t in new_tags]
        if domain_tag not in tag_variants:
            new_tags.insert(0, domain_tag)
            tags_added.append(domain_tag)

    # Add 'subagent' tag if applicable
    if is_sub:
        if "subagent" not in [t.lower() for t in new_tags]:
            new_tags.append("subagent")
            tags_added.append("subagent")

    if tags_added:
        fix = Fix(
            file=str(file_path),
            fix_type="tags",
            description=f"Added tags: {', '.join(tags_added)}",
            before=current_tags,
            after=new_tags,
        )

        if not dry_run:
            if "identity" not in agent:
                agent["identity"] = {}
            agent["identity"]["tags"] = new_tags
            fix.applied = True

        fixes.append(fix)

    return fixes


def fix_names(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Fix identity.name to match filename pattern."""
    fixes = []
    agent = data.get("agent", {})
    identity = agent.get("identity", {})

    current_name = identity.get("name", "")
    filename = file_path.stem.replace("_definition", "")

    if current_name != filename:
        fix = Fix(
            file=str(file_path),
            fix_type="names",
            description=f"Updated name from '{current_name}' to '{filename}'",
            before=current_name,
            after=filename,
        )

        if not dry_run:
            if "identity" not in agent:
                agent["identity"] = {}
            agent["identity"]["name"] = filename
            fix.applied = True

        fixes.append(fix)

    return fixes


def fix_version(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Fix version format to be quoted semver."""
    fixes = []
    agent = data.get("agent", {})
    identity = agent.get("identity", {})

    current_version = identity.get("version")

    if current_version is None:
        # Add default version
        fix = Fix(
            file=str(file_path),
            fix_type="version",
            description="Added missing version: 1.0.0",
            before=None,
            after="1.0.0",
        )

        if not dry_run:
            if "identity" not in agent:
                agent["identity"] = {}
            agent["identity"]["version"] = "1.0.0"
            fix.applied = True

        fixes.append(fix)

    elif not isinstance(current_version, str):
        # Convert to string
        new_version = str(current_version)
        if not re.match(r"^\d+\.\d+\.\d+$", new_version):
            new_version = "1.0.0"

        fix = Fix(
            file=str(file_path),
            fix_type="version",
            description=f"Converted version to string: '{new_version}'",
            before=current_version,
            after=new_version,
        )

        if not dry_run:
            agent["identity"]["version"] = new_version
            fix.applied = True

        fixes.append(fix)

    return fixes


def fix_scope(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Add missing scope section."""
    fixes = []
    agent = data.get("agent", {})

    if "scope" not in agent or not agent.get("scope"):
        is_sub = is_subagent(file_path)
        default_scope = DEFAULT_SUBAGENT_SCOPE if is_sub else DEFAULT_MAIN_AGENT_SCOPE

        fix = Fix(
            file=str(file_path),
            fix_type="scope",
            description="Added default scope section",
            before=None,
            after=default_scope,
        )

        if not dry_run:
            agent["scope"] = default_scope.copy()
            fix.applied = True

        fixes.append(fix)

    return fixes


def fix_directive(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Add missing directive section."""
    fixes = []
    agent = data.get("agent", {})
    identity = agent.get("identity", {})

    if "directive" not in agent or not agent.get("directive"):
        role = identity.get("role", "Agent")
        domain = extract_domain(file_path) or "domain"
        default_goal = f"Manage {domain.replace('_', ' ')} operations as {role}."

        default_directive = {"primary_goal": default_goal}

        fix = Fix(
            file=str(file_path),
            fix_type="directive",
            description="Added default directive section",
            before=None,
            after=default_directive,
        )

        if not dry_run:
            agent["directive"] = default_directive.copy()
            fix.applied = True

        fixes.append(fix)

    return fixes


def fix_inheritance(data: dict, file_path: Path, dry_run: bool = True) -> list[Fix]:
    """Add missing inheritance section."""
    fixes = []
    agent = data.get("agent", {})

    if "inheritance" not in agent:
        default_inheritance = {"extends": "base_agent_v2.1"}

        fix = Fix(
            file=str(file_path),
            fix_type="inheritance",
            description="Added inheritance extending base_agent_v2.1",
            before=None,
            after=default_inheritance,
        )

        if not dry_run:
            agent["inheritance"] = default_inheritance.copy()
            fix.applied = True

        fixes.append(fix)

    return fixes


# =============================================================================
# Main Fixer
# =============================================================================


class AgentFixer:
    """Applies fixes to agent files."""

    def __init__(self, base_dir: Path, dry_run: bool = True, fix_types: list[str] = None):
        self.base_dir = base_dir
        self.dry_run = dry_run
        self.fix_types = fix_types or ["tags", "names", "version", "scope", "directive"]
        self.report = FixReport()

    def fix_file(self, file_path: Path) -> list[Fix]:
        """Apply fixes to a single file."""
        data, _ = load_yaml(file_path)
        if data is None:
            return []

        all_fixes = []

        # Apply requested fix types
        if "tags" in self.fix_types:
            all_fixes.extend(fix_tags(data, file_path, self.dry_run))

        if "names" in self.fix_types:
            all_fixes.extend(fix_names(data, file_path, self.dry_run))

        if "version" in self.fix_types:
            all_fixes.extend(fix_version(data, file_path, self.dry_run))

        if "scope" in self.fix_types:
            all_fixes.extend(fix_scope(data, file_path, self.dry_run))

        if "directive" in self.fix_types:
            all_fixes.extend(fix_directive(data, file_path, self.dry_run))

        if "inheritance" in self.fix_types:
            all_fixes.extend(fix_inheritance(data, file_path, self.dry_run))

        # Save if changes were made
        if all_fixes and not self.dry_run:
            save_yaml(file_path, data)

        return all_fixes

    def fix_all(self, files: list[Path]) -> FixReport:
        """Apply fixes to multiple files."""
        self.report.total_files = len(files)
        modified_files = set()

        for file_path in files:
            fixes = self.fix_file(file_path)

            for fix in fixes:
                self.report.fixes.append(fix)
                if fix.applied:
                    self.report.fixes_applied += 1
                    modified_files.add(fix.file)
                else:
                    self.report.fixes_skipped += 1

        self.report.files_modified = len(modified_files)
        return self.report


# =============================================================================
# CLI
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


def print_fixes(fixes: list[Fix], verbose: bool = False):
    """Print fix summary."""
    if not fixes:
        print("No fixes needed.")
        return

    by_type = {}
    for fix in fixes:
        if fix.fix_type not in by_type:
            by_type[fix.fix_type] = []
        by_type[fix.fix_type].append(fix)

    for fix_type, type_fixes in sorted(by_type.items()):
        applied = sum(1 for f in type_fixes if f.applied)
        print(f"\n{fix_type}: {len(type_fixes)} fixes ({applied} applied)")

        if verbose:
            for fix in type_fixes[:10]:
                status = "✅" if fix.applied else "🔍"
                print(f"  {status} {fix.file}")
                print(f"      {fix.description}")
            if len(type_fixes) > 10:
                print(f"  ... and {len(type_fixes) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Fix agent YAML validation issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("file", nargs="?", help="Single YAML file to fix")
    parser.add_argument("--domain", "-d", help="Fix entire domain")
    parser.add_argument("--all", "-a", action="store_true", help="Fix all agents")
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--fix",
        action="append",
        choices=["tags", "names", "version", "scope", "directive", "inheritance"],
        help="Specific fix types to apply (can use multiple)",
    )
    parser.add_argument("--report", "-r", help="Output JSON report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
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
        print("No files found to fix")
        return 1

    # Determine fix types
    fix_types = args.fix if args.fix else ["tags", "names", "version", "scope"]

    mode = "DRY RUN" if args.dry_run else "APPLYING FIXES"
    print(f"\n{'=' * 60}")
    print(f"Agent Fixer - {mode}")
    print(f"{'=' * 60}")
    print(f"Files: {len(files)}")
    print(f"Fix types: {', '.join(fix_types)}")
    print(f"{'=' * 60}")

    # Apply fixes
    fixer = AgentFixer(base_dir, dry_run=args.dry_run, fix_types=fix_types)
    report = fixer.fix_all(files)

    # Print results
    print_fixes(report.fixes, verbose=args.verbose)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total files scanned: {report.total_files}")
    print(f"Files modified:      {report.files_modified}")
    print(f"Fixes applied:       {report.fixes_applied}")
    print(f"Fixes pending:       {report.fixes_skipped}")

    if args.dry_run and report.fixes_skipped > 0:
        print(f"\nRun without --dry-run to apply {report.fixes_skipped} fixes")

    # Save report if requested
    if args.report:
        Path(args.report).write_text(json.dumps(report.to_dict(), indent=2))
        print(f"\nReport saved to: {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
