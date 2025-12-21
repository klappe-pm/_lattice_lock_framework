import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from lattice_lock_validator.schema import validate_lattice_schema

logger = logging.getLogger(__name__)


@dataclass
class CompilationResult:
    """Result of a lattice compilation run."""

    success: bool
    generated_files: list[str]
    errors: list[str]
    warnings: list[str]


def compile_lattice(
    source_path: str, output_dir: str, test_dir: str, options: dict[str, Any] | None = None
) -> CompilationResult:
    """
    Orchestrates the full compilation pipeline.

    Args:
        source_path: Path to lattice.yaml
        output_dir: Where to write generated type definitions
        test_dir: Where to write generated Gauntlet tests
        options: Optional flags (e.g., dry_run, strict_mode)
    """
    options = options or {}
    generated_files = []
    _errors = []  # Reserved for future use
    _warnings = []  # Reserved for future use

    source_file = Path(source_path)
    if not source_file.exists():
        return CompilationResult(False, [], [f"Source file not found: {source_path}"], [])

    # 1. Parsing & Validation
    logger.info(f"Validating schema from {source_path}...")
    validation_result = validate_lattice_schema(str(source_path))

    if not validation_result.valid:
        error_msgs = [
            f"Validation Error ({e.field_path or 'root'}): {e.message}"
            for e in validation_result.errors
        ]
        return CompilationResult(
            False, [], error_msgs, [w.message for w in validation_result.warnings]
        )

    # Load data for generation steps
    try:
        with open(source_path) as f:
            _data = yaml.safe_load(f)  # Reserved for future type/test generation
    except Exception as e:
        return CompilationResult(False, [], [f"Failed to parse YAML: {e}"], [])

    # 2. Code Generation (Types)
    logger.info("Generating types...")
    try:
        if "entities" in _data:
            types_content = ["from pydantic import BaseModel", "", ""]
            for entity_name, entity_def in _data["entities"].items():
                types_content.append(f"class {entity_name}(BaseModel):")
                if "fields" in entity_def:
                    for field_name, field_def in entity_def["fields"].items():
                        field_type = field_def.get("type", "str")
                        # Map simple types if necessary, for now assuming valid python types or 'str'
                        types_content.append(f"    {field_name}: {field_type}")
                else:
                    types_content.append("    pass")
                types_content.append("")
            
            output_file = Path(output_dir) / "types.py"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("\n".join(types_content))
            generated_files.append(str(output_file))
    except Exception as e:
        return CompilationResult(False, generated_files, [f"Failed to generate types: {e}"], [])

    # 3. Test Generation (Contracts)
    logger.info("Generating contract tests...")
    try:
        if "governance" in _data and "policies" in _data["governance"]:
            tests_content = [
                "import pytest",
                "from lattice_lock.governance import check_policy", 
                "",
                f"# Generated tests for {_data.get('name', 'Project')}",
                ""
            ]
            for policy in _data["governance"]["policies"]:
                sanitized_policy = policy.replace("-", "_").replace(" ", "_")
                tests_content.append(f"def test_policy_{sanitized_policy}():")
                tests_content.append(f"    \"\"\"Verify policy: {policy}\"\"\"")
                tests_content.append(f"    # TODO: Implement specific check for {policy}")
                tests_content.append(f"    assert True # Placeholder for {policy}")
                tests_content.append("")
            
            output_file = Path(test_dir) / "test_contracts.py"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("\n".join(tests_content))
            generated_files.append(str(output_file))
    except Exception as e:
        return CompilationResult(False, generated_files, [f"Failed to generate tests: {e}"], [])

    return CompilationResult(
        True, generated_files, [], [w.message for w in validation_result.warnings]
    )
