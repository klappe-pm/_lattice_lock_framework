#!/usr/bin/env python3
"""
Prepare agent files for LLM-based linting with Qwen3-Next-80B.

This script:
1. Gathers agent YAML files
2. Formats them for LLM input
3. Outputs ready-to-paste prompts or saves to file

Usage:
    # Validate single file
    python3 prepare_for_linting.py path/to/agent.yaml

    # Validate entire domain
    python3 prepare_for_linting.py --domain engineering

    # Validate all agents (outputs batched files)
    python3 prepare_for_linting.py --all --batch-size 10

    # Quick check mode (errors only)
    python3 prepare_for_linting.py --domain financial --quick

    # Output to file instead of stdout
    python3 prepare_for_linting.py --domain ux --output lint_ux.txt
"""

import argparse
from pathlib import Path

SYSTEM_PROMPT = """You are the Agent Linting Manager for the Lattice Lock Framework. Your role is to validate agent definition YAML files against the v2.1 specification and report violations.

You have 12 validation domains:
1. Schema Compliance - Required fields and types
2. Naming Conventions - File and identity naming patterns
3. Description Quality - Completeness and clarity
4. Scope Consistency - Valid access/modify paths
5. Inheritance Validation - Base template compliance
6. Dependency Checking - Subagent references valid
7. Duplicate Detection - No redundant definitions
8. Tag Consistency - Tags match domain
9. Version Compliance - Semver format
10. Best Practices - Design pattern adherence
11. YAML Syntax - Valid YAML structure
12. Rule Applicability - Constraints are enforceable

Always output structured JSON reports. Be thorough but concise."""


VALIDATION_RULES_SUMMARY = """
## Quick Reference - Required Fields

agent.identity.name: string (must match filename)
agent.identity.version: quoted semver "X.Y.Z"
agent.identity.description: non-empty string
agent.identity.role: non-empty string
agent.directive.primary_goal: starts with action verb
agent.scope.can_access: list of paths

## Naming Pattern
Main: {domain}_agent_{role}_definition.yaml
Sub:  {domain}_agent_{parent}_{role}_definition.yaml

## Output Format
Return JSON with: file, valid, score, errors[], warnings[], passed_checks[], summary
"""


def find_agent_files(base_dir: Path, domain: str | None = None) -> list[Path]:
    """Find all agent YAML files, optionally filtered by domain."""
    agent_defs = base_dir / "agent_definitions"

    if domain:
        # Find specific domain directory
        domain_dir = agent_defs / f"agents_{domain}"
        if not domain_dir.exists():
            # Try without 'agents_' prefix
            domain_dir = agent_defs / domain

        if not domain_dir.exists():
            print(f"Error: Domain directory not found: {domain}")
            print("Available domains:")
            for d in sorted(agent_defs.iterdir()):
                if d.is_dir():
                    print(f"  - {d.name.replace('agents_', '')}")
            return []

        return sorted(domain_dir.rglob("*.yaml"))

    # All agents
    return sorted(agent_defs.rglob("*.yaml"))


def read_file_content(file_path: Path) -> str:
    """Read and return file content."""
    try:
        with open(file_path) as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {e}"


def format_single_file(file_path: Path, base_dir: Path) -> str:
    """Format a single file for LLM input."""
    relative_path = file_path.relative_to(base_dir)
    content = read_file_content(file_path)

    return f"""Validate this agent definition:

<agent_file>
{content}
</agent_file>

File path: {relative_path}

Return JSON validation report with errors, warnings, and passed_checks."""


def format_batch(files: list[Path], base_dir: Path, quick: bool = False) -> str:
    """Format multiple files for batch validation."""
    parts = []

    mode = (
        "Quick check - only report errors (skip warnings):"
        if quick
        else "Validate these agent definitions and provide a batch summary:"
    )
    parts.append(mode)
    parts.append("")
    parts.append("<agent_files>")

    for f in files:
        relative_path = f.relative_to(base_dir)
        content = read_file_content(f)
        parts.append(f"--- FILE: {relative_path} ---")
        parts.append(content)
        parts.append("")

    parts.append("</agent_files>")
    parts.append("")
    parts.append(
        "Return JSON batch summary with total_files, valid, invalid, common_issues, and individual results array."
    )

    return "\n".join(parts)


def create_full_prompt(user_content: str, include_rules: bool = True) -> str:
    """Create complete prompt with system message and rules."""
    parts = []

    parts.append("=" * 60)
    parts.append("SYSTEM PROMPT (paste as system message or prepend)")
    parts.append("=" * 60)
    parts.append(SYSTEM_PROMPT)
    parts.append("")

    if include_rules:
        parts.append("=" * 60)
        parts.append("VALIDATION RULES REFERENCE")
        parts.append("=" * 60)
        parts.append(VALIDATION_RULES_SUMMARY)
        parts.append("")

    parts.append("=" * 60)
    parts.append("USER PROMPT (paste as user message)")
    parts.append("=" * 60)
    parts.append(user_content)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare agent files for LLM-based linting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 prepare_for_linting.py agent_definitions/agents_engineering/engineering_agent_definition.yaml
  python3 prepare_for_linting.py --domain engineering
  python3 prepare_for_linting.py --domain financial --batch-size 15 --output batches/
  python3 prepare_for_linting.py --all --quick
        """,
    )

    parser.add_argument("file", nargs="?", help="Single YAML file to validate")
    parser.add_argument(
        "--domain", "-d", help="Validate entire domain (e.g., engineering, financial)"
    )
    parser.add_argument("--all", "-a", action="store_true", help="Validate all agents")
    parser.add_argument(
        "--batch-size", "-b", type=int, default=10, help="Files per batch (default: 10)"
    )
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode - errors only")
    parser.add_argument("--output", "-o", help="Output file or directory")
    parser.add_argument("--no-rules", action="store_true", help="Skip rules reference in output")
    parser.add_argument("--list-domains", "-l", action="store_true", help="List available domains")

    args = parser.parse_args()

    # Determine base directory
    script_dir = Path(__file__).parent
    base_dir = script_dir

    # List domains mode
    if args.list_domains:
        agent_defs = base_dir / "agent_definitions"
        print("Available domains:")
        for d in sorted(agent_defs.iterdir()):
            if d.is_dir() and d.name.startswith("agents_"):
                count = len(list(d.rglob("*.yaml")))
                print(f"  {d.name.replace('agents_', '')}: {count} agents")
        return

    # Determine files to process
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
        if not files:
            return 1
        print(f"Found {len(files)} files in domain: {args.domain}")

    elif args.all:
        files = find_agent_files(base_dir)
        print(f"Found {len(files)} total agent files")

    else:
        parser.print_help()
        return 1

    # Generate prompts
    if len(files) == 1:
        # Single file mode
        user_content = format_single_file(files[0], base_dir)
        output = create_full_prompt(user_content, include_rules=not args.no_rules)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Wrote prompt to: {args.output}")
        else:
            print(output)

    else:
        # Batch mode
        batches = [files[i : i + args.batch_size] for i in range(0, len(files), args.batch_size)]
        print(f"Created {len(batches)} batches of up to {args.batch_size} files each")

        if args.output:
            output_path = Path(args.output)
            if not output_path.suffix:
                # Directory mode
                output_path.mkdir(parents=True, exist_ok=True)
                for i, batch in enumerate(batches, 1):
                    user_content = format_batch(batch, base_dir, quick=args.quick)
                    output = create_full_prompt(user_content, include_rules=(i == 1))

                    batch_file = output_path / f"batch_{i:03d}.txt"
                    with open(batch_file, "w") as f:
                        f.write(output)
                    print(f"Wrote: {batch_file} ({len(batch)} files)")
            else:
                # Single file mode - combine all
                user_content = format_batch(files, base_dir, quick=args.quick)
                output = create_full_prompt(user_content, include_rules=not args.no_rules)
                with open(output_path, "w") as f:
                    f.write(output)
                print(f"Wrote prompt to: {output_path}")
        else:
            # Print first batch only
            print("\n" + "=" * 60)
            print(f"BATCH 1 of {len(batches)} (showing first batch only)")
            print("Use --output <dir> to save all batches to files")
            print("=" * 60 + "\n")

            user_content = format_batch(batches[0], base_dir, quick=args.quick)
            output = create_full_prompt(user_content, include_rules=not args.no_rules)
            print(output)

    return 0


if __name__ == "__main__":
    exit(main())
