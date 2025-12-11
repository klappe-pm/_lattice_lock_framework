"""
Lattice Lock Compilation API.

Compiles lattice.yaml schema files into enforcement artifacts:
- Pydantic models for validation
- SQLModel classes for ORM
- Gauntlet tests for contract testing

Example:
    >>> from lattice_lock.compile import compile_lattice
    >>> result = compile_lattice("examples/basic/lattice.yaml")
    >>> print(result.generated_files)
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging

from lattice_lock_validator.schema import validate_lattice_schema, ValidationResult
from lattice_lock_gauntlet.generator import GauntletGenerator
from lattice_lock_gauntlet.parser import LatticeParser

logger = logging.getLogger(__name__)


@dataclass
class CompilationResult:
    """
    Result of compiling a lattice.yaml schema.

    Attributes:
        success: Whether compilation completed successfully
        generated_files: List of paths to generated files
        warnings: List of warning messages
        errors: List of error messages
        schema_path: Original schema path
        entities: List of entity names that were compiled
    """
    success: bool = True
    generated_files: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    schema_path: Optional[Path] = None
    entities: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        """Add an error and mark compilation as failed."""
        self.success = False
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add a warning (does not affect success status)."""
        self.warnings.append(message)


def compile_lattice(
    schema_path: Union[str, Path],
    output_dir: Union[str, Path, None] = None,
    generate_pydantic: bool = True,
    generate_sqlmodel: bool = False,
    generate_gauntlet: bool = True,
) -> CompilationResult:
    """
    Compile a lattice.yaml schema into enforcement artifacts.

    Args:
        schema_path: Path to the lattice.yaml schema file
        output_dir: Directory for generated files (default: same as schema)
        generate_pydantic: Generate Pydantic validation models
        generate_sqlmodel: Generate SQLModel ORM classes
        generate_gauntlet: Generate Gauntlet test contracts

    Returns:
        CompilationResult with paths to generated files and any warnings/errors

    Example:
        >>> result = compile_lattice("schema.yaml", output_dir="./generated")
        >>> if result.success:
        ...     print(f"Generated {len(result.generated_files)} files")
        >>> else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    result = CompilationResult()

    # Normalize paths
    schema_path = Path(schema_path)
    result.schema_path = schema_path

    if output_dir is None:
        output_dir = schema_path.parent / "generated"
    else:
        output_dir = Path(output_dir)

    # Step 1: Validate the schema
    logger.info(f"Validating schema: {schema_path}")
    validation = validate_lattice_schema(str(schema_path))

    if not validation.valid:
        for error in validation.errors:
            result.add_error(f"Validation error: {error.message}")
        return result

    # Add validation warnings
    for warning in validation.warnings:
        result.add_warning(f"Validation warning: {warning.message}")

    # Step 2: Parse the schema
    logger.info("Parsing schema...")
    try:
        parser = LatticeParser(str(schema_path))
        entities = parser.parse()
        result.entities = [entity.name for entity in entities]
    except Exception as e:
        result.add_error(f"Failed to parse schema: {str(e)}")
        return result

    if not entities:
        result.add_warning("No entities found in schema")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Generate Gauntlet tests
    if generate_gauntlet and entities:
        logger.info("Generating Gauntlet test contracts...")
        try:
            gauntlet_dir = output_dir / "gauntlet"
            generator = GauntletGenerator(str(schema_path), str(gauntlet_dir))
            generator.generate()

            # Record generated files
            for entity in entities:
                test_file = gauntlet_dir / f"test_contract_{entity.name}.py"
                if test_file.exists():
                    result.generated_files.append(test_file)
        except Exception as e:
            result.add_error(f"Failed to generate Gauntlet tests: {str(e)}")

    # Step 4: Generate Pydantic models
    if generate_pydantic and entities:
        logger.info("Generating Pydantic models...")
        try:
            pydantic_file = output_dir / "models.py"
            _generate_pydantic_models(entities, parser, pydantic_file)
            result.generated_files.append(pydantic_file)
        except Exception as e:
            result.add_error(f"Failed to generate Pydantic models: {str(e)}")

    # Step 5: Generate SQLModel classes
    if generate_sqlmodel and entities:
        logger.info("Generating SQLModel classes...")
        try:
            sqlmodel_file = output_dir / "orm.py"
            _generate_sqlmodel_classes(entities, parser, sqlmodel_file)
            result.generated_files.append(sqlmodel_file)
        except Exception as e:
            result.add_error(f"Failed to generate SQLModel classes: {str(e)}")

    logger.info(f"Compilation complete. Generated {len(result.generated_files)} files.")
    return result


def _generate_pydantic_models(entities, parser: LatticeParser, output_path: Path):
    """Generate Pydantic validation models."""
    lines = [
        '"""',
        'Auto-generated Pydantic models from lattice.yaml',
        '',
        'DO NOT EDIT - Generated by lattice-lock compile',
        '"""',
        'from pydantic import BaseModel, Field, field_validator',
        'from typing import Optional, List',
        'from uuid import UUID',
        'from decimal import Decimal',
        'from enum import Enum',
        '',
    ]

    for entity in entities:
        lines.append('')
        lines.append(f'class {entity.name}(BaseModel):')
        lines.append(f'    """Pydantic model for {entity.name} entity."""')

        if not entity.fields:
            lines.append('    pass')
            continue

        for field_name, field_def in entity.fields.items():
            field_type = _map_type_to_python(field_def)
            default = field_def.get('default')

            if default is not None:
                lines.append(f'    {field_name}: {field_type} = {repr(default)}')
            elif field_def.get('nullable', False):
                lines.append(f'    {field_name}: Optional[{field_type}] = None')
            else:
                lines.append(f'    {field_name}: {field_type}')

        # Add validators for constraints
        for clause in entity.ensures:
            if clause.constraint in ('gt', 'lt', 'gte', 'lte'):
                lines.append('')
                lines.append(f'    @field_validator("{clause.field}")')
                lines.append('    @classmethod')
                lines.append(f'    def validate_{clause.field}_{clause.constraint}(cls, v):')
                op = {'gt': '>', 'lt': '<', 'gte': '>=', 'lte': '<='}[clause.constraint]
                lines.append(f'        if v is not None and not (v {op} {clause.value}):')
                lines.append(f'            raise ValueError("{clause.field} must be {op} {clause.value}")')
                lines.append('        return v')

    lines.append('')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def _generate_sqlmodel_classes(entities, parser: LatticeParser, output_path: Path):
    """Generate SQLModel ORM classes."""
    lines = [
        '"""',
        'Auto-generated SQLModel ORM classes from lattice.yaml',
        '',
        'DO NOT EDIT - Generated by lattice-lock compile',
        '"""',
        'from sqlmodel import SQLModel, Field',
        'from typing import Optional',
        'from uuid import UUID, uuid4',
        'from decimal import Decimal',
        '',
    ]

    for entity in entities:
        lines.append('')
        lines.append(f'class {entity.name}(SQLModel, table=True):')
        lines.append(f'    """SQLModel ORM class for {entity.name} entity."""')

        if not entity.fields:
            lines.append('    pass')
            continue

        for field_name, field_def in entity.fields.items():
            field_type = _map_type_to_python(field_def)

            # Build Field() arguments
            field_args = []
            if field_def.get('primary_key'):
                field_args.append('primary_key=True')
            if field_def.get('unique'):
                field_args.append('unique=True')
            if field_def.get('default') is not None:
                field_args.append(f'default={repr(field_def["default"])}')
            elif field_def.get('nullable', False):
                field_args.append('default=None')

            # Handle UUID primary keys with default
            if field_def.get('type') == 'uuid' and field_def.get('primary_key'):
                field_args.append('default_factory=uuid4')

            if field_args:
                args_str = ', '.join(field_args)
                if field_def.get('nullable', False):
                    lines.append(f'    {field_name}: Optional[{field_type}] = Field({args_str})')
                else:
                    lines.append(f'    {field_name}: {field_type} = Field({args_str})')
            else:
                if field_def.get('nullable', False):
                    lines.append(f'    {field_name}: Optional[{field_type}] = None')
                else:
                    lines.append(f'    {field_name}: {field_type}')

    lines.append('')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def _map_type_to_python(field_def: Dict[str, Any]) -> str:
    """Map lattice.yaml types to Python types."""
    type_mapping = {
        'uuid': 'UUID',
        'str': 'str',
        'int': 'int',
        'decimal': 'Decimal',
        'bool': 'bool',
    }

    field_type = field_def.get('type', 'str')

    # Handle enum types
    if 'enum' in field_def:
        return 'str'  # Enums are treated as strings

    return type_mapping.get(field_type, 'str')
