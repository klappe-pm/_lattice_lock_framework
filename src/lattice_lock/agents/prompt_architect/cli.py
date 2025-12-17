"""
CLI command for the Prompt Architect Agent.

Provides command-line interface for generating prompts from specifications.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from lattice_lock.agents.prompt_architect.models import GenerationRequest, GenerationResult
from lattice_lock.agents.prompt_architect.orchestrator import PromptArchitectOrchestrator
from lattice_lock.utils.safe_path import resolve_under_root

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="prompt-architect",
        description="Generate LLM prompts from project specifications",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate prompts from specifications",
    )
    generate_parser.add_argument(
        "project",
        help="Project name",
    )
    generate_parser.add_argument(
        "--phase",
        help="Generate prompts for a specific phase (e.g., 1, 2, 3)",
    )
    generate_parser.add_argument(
        "--epic",
        help="Generate prompts for a specific epic (e.g., 1.1, 2.3)",
    )
    generate_parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="Generate prompts for specific tasks (can be repeated)",
    )
    generate_parser.add_argument(
        "--spec",
        default="specifications/lattice_lock_framework_specifications.md",
        help="Path to specification file",
    )
    generate_parser.add_argument(
        "--roadmap-dir",
        default="developer_documentation",
        help="Directory containing roadmap files",
    )
    generate_parser.add_argument(
        "--output",
        default="project_prompts",
        help="Output directory for generated prompts",
    )
    generate_parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of existing prompts",
    )
    generate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files",
    )
    generate_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show prompt generation status",
    )
    status_parser.add_argument(
        "--state-file",
        default="project_prompts/project_prompts_state.json",
        help="Path to state file",
    )
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate generated prompts",
    )
    validate_parser.add_argument(
        "prompt_dir",
        nargs="?",
        default="project_prompts",
        help="Directory containing prompts to validate",
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    return parser


def cmd_generate(args: argparse.Namespace) -> int:
    """Handle the generate command."""
    orchestrator = PromptArchitectOrchestrator(
        spec_path=args.spec,
        roadmap_dir=args.roadmap_dir,
        output_dir=args.output,
    )

    request = GenerationRequest(
        project_name=args.project,
        phase=args.phase,
        epic=args.epic,
        task_ids=args.tasks or [],
        force_regenerate=args.force,
        dry_run=args.dry_run,
        output_directory=args.output,
    )

    result = orchestrator.generate_prompts(request)

    if args.json:
        print(format_result_json(result))
    else:
        print_result(result, args.dry_run)

    return 0 if result.success else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Handle the status command."""
    try:
        state_file = resolve_under_root(args.state_file)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    if not state_file.exists():
        if args.json:
            print(json.dumps({"error": "State file not found"}))
        else:
            print(f"State file not found: {state_file}")
        return 1

    try:
        state = json.loads(state_file.read_text())
    except json.JSONDecodeError as e:
        if args.json:
            print(json.dumps({"error": f"Invalid state file: {e}"}))
        else:
            print(f"Invalid state file: {e}")
        return 1

    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print_status(state)

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle the validate command."""
    try:
        prompt_dir = resolve_under_root(args.prompt_dir)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    if not prompt_dir.exists():
        if args.json:
            print(json.dumps({"error": "Prompt directory not found"}))
        else:
            print(f"Prompt directory not found: {prompt_dir}")
        return 1

    results = validate_prompts(prompt_dir)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_validation_results(results)

    return 0 if results["valid"] else 1


def validate_prompts(prompt_dir: Path) -> dict:
    """Validate prompts in a directory."""
    results = {
        "valid": True,
        "total": 0,
        "valid_count": 0,
        "invalid_count": 0,
        "errors": [],
    }

    required_sections = ["Context", "Requirements", "Acceptance Criteria"]

    for prompt_file in prompt_dir.rglob("*.md"):
        results["total"] += 1
        content = prompt_file.read_text()

        missing_sections = []
        for section in required_sections:
            if f"## {section}" not in content:
                missing_sections.append(section)

        if missing_sections:
            results["invalid_count"] += 1
            results["valid"] = False
            results["errors"].append(
                {
                    "file": str(prompt_file),
                    "missing_sections": missing_sections,
                }
            )
        else:
            results["valid_count"] += 1

    return results


def format_result_json(result: GenerationResult) -> str:
    """Format generation result as JSON."""
    return json.dumps(
        {
            "success": result.success,
            "prompts_generated": result.prompts_generated,
            "prompts_updated": result.prompts_updated,
            "prompts_skipped": result.prompts_skipped,
            "errors": result.errors,
            "warnings": result.warnings,
            "execution_time_seconds": result.execution_time_seconds,
            "prompts": [
                {
                    "prompt_id": p.prompt_id,
                    "task_id": p.task_id,
                    "tool": p.tool.value,
                    "file_path": p.file_path,
                }
                for p in result.generated_prompts
            ],
        },
        indent=2,
    )


def print_result(result: GenerationResult, dry_run: bool = False) -> None:
    """Print generation result to console."""
    if dry_run:
        print("DRY RUN - No files were written")
        print()

    if result.success:
        print("Prompt generation completed successfully!")
    else:
        print("Prompt generation completed with errors")

    print()
    print(f"Prompts generated: {result.prompts_generated}")
    print(f"Prompts updated: {result.prompts_updated}")
    print(f"Prompts skipped: {result.prompts_skipped}")
    print(f"Execution time: {result.execution_time_seconds:.2f}s")

    if result.errors:
        print()
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print()
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.generated_prompts:
        print()
        print("Generated prompts:")
        for prompt in result.generated_prompts:
            print(f"  - {prompt.file_path}")


def print_status(state: dict) -> None:
    """Print status information to console."""
    print("Prompt Generation Status")
    print("=" * 40)

    if "updated_at" in state:
        print(f"Last updated: {state['updated_at']}")

    prompts = state.get("prompts", {})
    print(f"Total prompts: {len(prompts)}")

    if "last_generation" in state:
        last = state["last_generation"]
        print()
        print("Last generation:")
        print(f"  Generated: {last.get('prompts_generated', 0)}")
        print(f"  Updated: {last.get('prompts_updated', 0)}")
        print(f"  Timestamp: {last.get('timestamp', 'N/A')}")

        if last.get("errors"):
            print(f"  Errors: {len(last['errors'])}")


def print_validation_results(results: dict) -> None:
    """Print validation results to console."""
    print("Prompt Validation Results")
    print("=" * 40)

    print(f"Total prompts: {results['total']}")
    print(f"Valid: {results['valid_count']}")
    print(f"Invalid: {results['invalid_count']}")

    if results["errors"]:
        print()
        print("Validation errors:")
        for error in results["errors"]:
            print(f"  {error['file']}:")
            for section in error["missing_sections"]:
                print(f"    - Missing section: {section}")


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
