#!/usr/bin/env python3
"""
Lattice Lock Schema Compiler CLI

Command-line interface for compiling lattice.yaml schemas into enforcement artifacts.

Usage:
    python scripts/compile_lattice.py examples/basic/lattice.yaml --output-dir ./generated
    python scripts/compile_lattice.py examples/advanced/lattice.yaml --pydantic --sqlmodel --gauntlet
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.compile import compile_lattice


def main():
    parser = argparse.ArgumentParser(
        description="Compile lattice.yaml schemas into enforcement artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Compile with default options (Pydantic + Gauntlet)
    python scripts/compile_lattice.py examples/basic/lattice.yaml

    # Compile to specific output directory
    python scripts/compile_lattice.py examples/basic/lattice.yaml --output-dir ./generated

    # Generate all artifact types
    python scripts/compile_lattice.py examples/advanced/lattice.yaml --pydantic --sqlmodel --gauntlet

    # Generate only Gauntlet tests
    python scripts/compile_lattice.py examples/basic/lattice.yaml --no-pydantic --gauntlet
        """,
    )

    parser.add_argument("schema_path", type=str, help="Path to the lattice.yaml schema file")

    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=None,
        help="Output directory for generated files (default: same directory as schema)",
    )

    parser.add_argument(
        "--pydantic",
        action="store_true",
        default=True,
        help="Generate Pydantic models (default: enabled)",
    )

    parser.add_argument(
        "--no-pydantic", action="store_true", help="Disable Pydantic model generation"
    )

    parser.add_argument(
        "--sqlmodel",
        action="store_true",
        default=False,
        help="Generate SQLModel ORM classes (default: disabled)",
    )

    parser.add_argument(
        "--gauntlet",
        action="store_true",
        default=True,
        help="Generate Gauntlet test contracts (default: enabled)",
    )

    parser.add_argument(
        "--no-gauntlet", action="store_true", help="Disable Gauntlet test generation"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Handle negation flags
    generate_pydantic = args.pydantic and not args.no_pydantic
    generate_gauntlet = args.gauntlet and not args.no_gauntlet

    # Validate schema path
    schema_path = Path(args.schema_path)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Compiling schema: {schema_path}")
        print(f"Output directory: {args.output_dir or schema_path.parent}")
        print(f"Generate Pydantic: {generate_pydantic}")
        print(f"Generate SQLModel: {args.sqlmodel}")
        print(f"Generate Gauntlet: {generate_gauntlet}")
        print()

    # Compile the schema
    result = compile_lattice(
        schema_path=schema_path,
        output_dir=args.output_dir,
        generate_pydantic=generate_pydantic,
        generate_sqlmodel=args.sqlmodel,
        generate_gauntlet=generate_gauntlet,
    )

    # Report results
    if result.success:
        print("Compilation successful!")
        print()

        if result.generated_files:
            print("Generated files:")
            for f in result.generated_files:
                entity_info = f" ({f.entity_name})" if f.entity_name else ""
                print(f"  [{f.file_type}] {f.path}{entity_info}")

        if result.warnings:
            print()
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        sys.exit(0)
    else:
        print("Compilation failed!", file=sys.stderr)
        print()

        if result.errors:
            print("Errors:", file=sys.stderr)
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
