#!/usr/bin/env python3
"""
Validates MODELS.md against models.yaml registry.

This script ensures that all model IDs referenced in MODELS.md
actually exist in the canonical models.yaml registry.

Usage:
    python scripts/validate_models_md.py

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import re
import sys
from pathlib import Path

import yaml


def load_registry(registry_path: Path) -> set[str]:
    """Load model IDs from the registry YAML file."""
    if not registry_path.exists():
        print(f"Error: Registry file not found at {registry_path}")
        sys.exit(1)

    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "models" not in data:
        print(f"Error: Invalid registry format in {registry_path}")
        sys.exit(1)

    return {m["id"] for m in data["models"]}


def extract_model_references(models_md_path: Path) -> dict[str, set[str]]:
    """Extract all model references from MODELS.md."""
    if not models_md_path.exists():
        print(f"Error: MODELS.md not found at {models_md_path}")
        sys.exit(1)

    with open(models_md_path, encoding="utf-8") as f:
        content = f.read()

    references: dict[str, set[str]] = {
        "code_tasks": set(),
        "fallback_chains": set(),
        "blocked_models": set(),
    }

    # Extract from Code Tasks section (uses > delimiter)
    code_tasks_match = re.search(r"### Code Tasks(.*?)(?:###|---|\Z)", content, re.DOTALL)
    if code_tasks_match:
        section = code_tasks_match.group(1)
        for line in section.split("\n"):
            if "**" in line and ":" in line and ">" in line:
                match = re.match(r"- \*\*(.+?)\*\*: (.+)", line)
                if match:
                    models = [m.strip() for m in match.group(2).split(">")]
                    references["code_tasks"].update(models)

    # Extract from Fallback Chains section (uses -> or -> delimiter)
    fallback_match = re.search(r"### Fallback Chains(.*?)(?:###|---|\Z)", content, re.DOTALL)
    if fallback_match:
        section = fallback_match.group(1)
        for line in section.split("\n"):
            if "->" in line or "→" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    delimiter = "→" if "→" in parts[1] else "->"
                    models = [m.strip() for m in parts[1].split(delimiter)]
                    references["fallback_chains"].update(models)

    # Extract from Blocked Models section
    blocked_match = re.search(
        r"### Blocked Models(.*?)(?:^##|^---|\Z)", content, re.DOTALL | re.MULTILINE
    )
    if blocked_match:
        section = blocked_match.group(1)
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("- ") and not line.startswith("- **"):
                model = line[2:].strip()
                if model and not model.startswith("#"):
                    references["blocked_models"].add(model)

    return references


def validate_models(
    valid_ids: set[str], references: dict[str, set[str]]
) -> tuple[list[str], list[str]]:
    """Validate model references against registry."""
    errors: list[str] = []
    warnings: list[str] = []

    for section_name, model_ids in references.items():
        for model_id in model_ids:
            if not model_id:
                continue
            if model_id not in valid_ids:
                errors.append(f"[{section_name}] Invalid model ID: '{model_id}'")

    return errors, warnings


def check_consistency(references: dict[str, set[str]]) -> list[str]:
    """Check for consistency issues between sections."""
    warnings: list[str] = []

    # Check if all code_tasks models have corresponding fallback chains
    code_task_models = references["code_tasks"]
    fallback_models = references["fallback_chains"]

    # Models in code tasks but not in any fallback chain
    missing_fallbacks = code_task_models - fallback_models
    if missing_fallbacks:
        for model in list(missing_fallbacks)[:5]:  # Limit to first 5
            warnings.append(f"Model '{model}' in code_tasks but not in any fallback chain")

    return warnings


def main() -> int:
    """Main validation function."""
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    registry_path = project_root / "src" / "lattice_lock" / "orchestrator" / "models.yaml"
    models_md_path = project_root / "MODELS.md"

    print("=" * 60)
    print("MODELS.md Validation")
    print("=" * 60)
    print(f"Registry: {registry_path}")
    print(f"MODELS.md: {models_md_path}")
    print()

    # Load registry
    valid_ids = load_registry(registry_path)
    print(f"Loaded {len(valid_ids)} models from registry")

    # Extract references
    references = extract_model_references(models_md_path)
    total_refs = sum(len(v) for v in references.values())
    print(f"Found {total_refs} model references in MODELS.md")
    print(f"  - Code Tasks: {len(references['code_tasks'])} unique models")
    print(f"  - Fallback Chains: {len(references['fallback_chains'])} unique models")
    print(f"  - Blocked Models: {len(references['blocked_models'])} models")
    print()

    # Validate
    errors, warnings = validate_models(valid_ids, references)
    consistency_warnings = check_consistency(references)
    warnings.extend(consistency_warnings)

    # Report results
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")
        print()

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    # Summary
    print("=" * 60)
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        print()
        print("To fix these errors:")
        print("  1. Check model IDs in MODELS.md match exactly with models.yaml")
        print("  2. Add missing models to models.yaml if they should be supported")
        print("  3. Remove invalid model references from MODELS.md")
        return 1
    elif warnings:
        print(f"PASSED with {len(warnings)} warning(s)")
        return 0
    else:
        print("PASSED: All model references are valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
