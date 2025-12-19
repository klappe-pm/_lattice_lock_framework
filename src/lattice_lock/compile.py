"""
Lattice Lock Schema Compiler

This module provides the compile_lattice function that transforms lattice.yaml
schemas into enforcement artifacts including Pydantic models, SQLModel ORM
classes, and Gauntlet test contracts.
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from lattice_lock_validator.schema import ValidationResult, validate_lattice_schema


@dataclass
class GeneratedFile:
    """Represents a generated file."""

    path: Path
    file_type: str  # 'pydantic', 'sqlmodel', 'gauntlet'
    entity_name: str | None = None


@dataclass
class CompilationResult:
    """
    Result of compiling a lattice.yaml schema.

    Attributes:
        success: Whether compilation succeeded
        generated_files: List of generated file paths and types
        warnings: List of warning messages
        errors: List of error messages
        validation_result: The validation result from schema validation
    """

    success: bool = True
    generated_files: list[GeneratedFile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    validation_result: ValidationResult | None = None

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Add an error message and mark compilation as failed."""
        self.success = False
        self.errors.append(message)

    def add_generated_file(self, path: Path, file_type: str, entity_name: str | None = None):
        """Add a generated file to the result."""
        self.generated_files.append(
            GeneratedFile(path=path, file_type=file_type, entity_name=entity_name)
        )


def compile_lattice(
    schema_path: str | Path,
    output_dir: str | Path | None = None,
    generate_pydantic: bool = True,
    generate_sqlmodel: bool = False,
    generate_gauntlet: bool = True,
) -> CompilationResult:
    """
    Compile a lattice.yaml schema into enforcement artifacts.

    Args:
        schema_path: Path to lattice.yaml file
        output_dir: Directory for generated files (default: same as schema)
        generate_pydantic: Generate Pydantic models
        generate_sqlmodel: Generate SQLModel ORM classes
        generate_gauntlet: Generate Gauntlet test contracts

    Returns:
        CompilationResult with paths to generated files and any warnings/errors

    Example:
        >>> result = compile_lattice("examples/basic/lattice.yaml", output_dir="./generated")
        >>> if result.success:
        ...     for f in result.generated_files:
        ...         print(f"Generated: {f.path}")
    """
    result = CompilationResult()

    # Convert to Path objects - users can compile schemas to any directory they specify
    schema_path = Path(schema_path).expanduser().resolve()
    if output_dir is None:
        output_dir = schema_path.parent
    else:
        output_dir = Path(output_dir).expanduser().resolve()

    # Step 1: Validate schema exists
    if not schema_path.exists():
        result.add_error(f"Schema file not found: {schema_path}")
        return result

    # Step 2: Validate schema
    validation_result = validate_lattice_schema(str(schema_path))
    result.validation_result = validation_result

    if not validation_result.valid:
        for error in validation_result.errors:
            result.add_error(f"Schema validation error: {error.message}")
        return result

    # Add any validation warnings
    for warning in validation_result.warnings:
        result.add_warning(f"Schema validation warning: {warning.message}")

    # Step 3: Load schema data
    try:
        with open(schema_path) as f:
            schema_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.add_error(f"Failed to parse YAML: {e}")
        return result

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get module name from schema
    module_name = schema_data.get("generated_module", "types_generated")

    # Step 4: Generate Pydantic models (if requested)
    if generate_pydantic:
        try:
            pydantic_path = _generate_pydantic_models(schema_data, output_dir, module_name)
            if pydantic_path:
                result.add_generated_file(pydantic_path, "pydantic")
        except Exception as e:
            result.add_warning(f"Failed to generate Pydantic models: {e}")

    # Step 5: Generate SQLModel ORM classes (if requested)
    if generate_sqlmodel:
        try:
            sqlmodel_path = _generate_sqlmodel_classes(schema_data, output_dir, module_name)
            if sqlmodel_path:
                result.add_generated_file(sqlmodel_path, "sqlmodel")
        except Exception as e:
            result.add_warning(f"Failed to generate SQLModel classes: {e}")

    # Step 6: Generate Gauntlet test contracts (if requested)
    if generate_gauntlet:
        try:
            # Lazy import to avoid circular dependency
            from lattice_lock_gauntlet.generator import GauntletGenerator

            gauntlet_dir = output_dir / "tests"
            generator = GauntletGenerator(str(schema_path), str(gauntlet_dir))
            generator.generate()

            # Add generated test files to result
            for entity in generator.parser.entities:
                test_file = gauntlet_dir / f"test_contract_{entity.name}.py"
                if test_file.exists():
                    result.add_generated_file(test_file, "gauntlet", entity.name)
        except Exception as e:
            result.add_warning(f"Failed to generate Gauntlet tests: {e}")

    return result


def _generate_pydantic_models(schema_data: dict, output_dir: Path, module_name: str) -> Path | None:
    """
    Generate Pydantic models from schema data.

    Args:
        schema_data: Parsed schema data
        output_dir: Output directory
        module_name: Name for the generated module

    Returns:
        Path to generated file, or None if no entities
    """
    entities = schema_data.get("entities", {})
    if not entities:
        return None

    output_path = output_dir / f"{module_name}_pydantic.py"

    lines = [
        '"""',
        "Pydantic models generated from lattice.yaml",
        f"Module: {module_name}",
        "Generated by Lattice Lock Compiler",
        '"""',
        "",
        "from decimal import Decimal",
        "from enum import Enum",
        "from typing import Optional, List",
        "from uuid import UUID",
        "from pydantic import BaseModel, Field",
        "",
        "",
    ]

    for entity_name, entity_def in entities.items():
        fields = entity_def.get("fields", {})

        # Generate enum classes for enum fields
        for field_name, field_def in fields.items():
            if "enum" in field_def:
                enum_values = field_def["enum"]
                enum_class_name = f"{entity_name}{field_name.title().replace('_', '')}Enum"
                lines.append(f"class {enum_class_name}(str, Enum):")
                for value in enum_values:
                    lines.append(f'    {value.upper()} = "{value}"')
                lines.append("")
                lines.append("")

        # Generate model class
        lines.append(f"class {entity_name}(BaseModel):")
        description = entity_def.get("description", f"{entity_name} model")
        lines.append(f'    """{description}"""')
        lines.append("")

        for field_name, field_def in fields.items():
            field_type = _get_pydantic_type(field_def, entity_name, field_name)
            field_kwargs = _get_pydantic_field_kwargs(field_def)

            if field_kwargs:
                lines.append(f"    {field_name}: {field_type} = Field({field_kwargs})")
            else:
                lines.append(f"    {field_name}: {field_type}")

        lines.append("")
        lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return output_path


def _get_pydantic_type(field_def: dict, entity_name: str, field_name: str) -> str:
    """Convert lattice field type to Pydantic type."""
    field_type = field_def.get("type", "str")

    if "enum" in field_def:
        enum_class_name = f"{entity_name}{field_name.title().replace('_', '')}Enum"
        return enum_class_name

    type_mapping = {
        "uuid": "UUID",
        "str": "str",
        "int": "int",
        "decimal": "Decimal",
        "bool": "bool",
    }

    return type_mapping.get(field_type, "str")


def _get_pydantic_field_kwargs(field_def: dict) -> str:
    """Generate Pydantic Field kwargs from field definition."""
    kwargs = []

    if "gt" in field_def:
        kwargs.append(f'gt={field_def["gt"]}')
    if "lt" in field_def:
        kwargs.append(f'lt={field_def["lt"]}')
    if "gte" in field_def:
        kwargs.append(f'ge={field_def["gte"]}')
    if "lte" in field_def:
        kwargs.append(f'le={field_def["lte"]}')
    if "default" in field_def:
        default_val = field_def["default"]
        if isinstance(default_val, str):
            kwargs.append(f'default="{default_val}"')
        else:
            kwargs.append(f"default={default_val}")

    return ", ".join(kwargs)


def _generate_sqlmodel_classes(
    schema_data: dict, output_dir: Path, module_name: str
) -> Path | None:
    """
    Generate SQLModel ORM classes from schema data.

    Args:
        schema_data: Parsed schema data
        output_dir: Output directory
        module_name: Name for the generated module

    Returns:
        Path to generated file, or None if no entities
    """
    entities = schema_data.get("entities", {})
    if not entities:
        return None

    output_path = output_dir / f"{module_name}_sqlmodel.py"

    lines = [
        '"""',
        "SQLModel ORM classes generated from lattice.yaml",
        f"Module: {module_name}",
        "Generated by Lattice Lock Compiler",
        '"""',
        "",
        "from decimal import Decimal",
        "from enum import Enum",
        "from typing import Optional",
        "from uuid import UUID, uuid4",
        "from sqlmodel import SQLModel, Field",
        "",
        "",
    ]

    for entity_name, entity_def in entities.items():
        fields = entity_def.get("fields", {})
        persistence = entity_def.get("persistence", None)

        # Generate enum classes for enum fields
        for field_name, field_def in fields.items():
            if "enum" in field_def:
                enum_values = field_def["enum"]
                enum_class_name = f"{entity_name}{field_name.title().replace('_', '')}Enum"
                lines.append(f"class {enum_class_name}(str, Enum):")
                for value in enum_values:
                    lines.append(f'    {value.upper()} = "{value}"')
                lines.append("")
                lines.append("")

        # Generate model class
        table_arg = ", table=True" if persistence == "table" else ""
        lines.append(f"class {entity_name}(SQLModel{table_arg}):")
        description = entity_def.get("description", f"{entity_name} model")
        lines.append(f'    """{description}"""')
        lines.append("")

        for field_name, field_def in fields.items():
            field_type = _get_sqlmodel_type(field_def, entity_name, field_name)
            field_kwargs = _get_sqlmodel_field_kwargs(field_def)

            if field_kwargs:
                lines.append(f"    {field_name}: {field_type} = Field({field_kwargs})")
            else:
                lines.append(f"    {field_name}: {field_type}")

        lines.append("")
        lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return output_path


def _get_sqlmodel_type(field_def: dict, entity_name: str, field_name: str) -> str:
    """Convert lattice field type to SQLModel type."""
    field_type = field_def.get("type", "str")

    if "enum" in field_def:
        enum_class_name = f"{entity_name}{field_name.title().replace('_', '')}Enum"
        return enum_class_name

    type_mapping = {
        "uuid": "UUID",
        "str": "str",
        "int": "int",
        "decimal": "Decimal",
        "bool": "bool",
    }

    return type_mapping.get(field_type, "str")


def _get_sqlmodel_field_kwargs(field_def: dict) -> str:
    """Generate SQLModel Field kwargs from field definition."""
    kwargs = []

    if field_def.get("primary_key"):
        kwargs.append("primary_key=True")
        kwargs.append("default_factory=uuid4")
    if field_def.get("unique"):
        kwargs.append("unique=True")
    if "default" in field_def:
        default_val = field_def["default"]
        if isinstance(default_val, str):
            kwargs.append(f'default="{default_val}"')
        else:
            kwargs.append(f"default={default_val}")

    return ", ".join(kwargs)
