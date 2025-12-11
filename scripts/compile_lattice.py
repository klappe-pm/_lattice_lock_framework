#!/usr/bin/env python3
"""
Lattice Lock Schema Compiler CLI.

Compiles lattice.yaml schema files into enforcement artifacts.

Usage:
    python scripts/compile_lattice.py examples/basic/lattice.yaml
    python scripts/compile_lattice.py schema.yaml --output-dir ./generated
    python scripts/compile_lattice.py schema.yaml --pydantic --gauntlet
"""
import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.compile import compile_lattice


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Compile lattice.yaml schemas into enforcement artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s examples/basic/lattice.yaml
  %(prog)s schema.yaml --output-dir ./generated
  %(prog)s schema.yaml --pydantic --sqlmodel --gauntlet
  %(prog)s schema.yaml --no-pydantic
        """
    )

    parser.add_argument(
        "schema",
        type=str,
        help="Path to the lattice.yaml schema file"
    )

    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Output directory for generated files (default: <schema_dir>/generated)"
    )

    parser.add_argument(
        "--pydantic",
        action="store_true",
        default=True,
        help="Generate Pydantic validation models (default: True)"
    )

    parser.add_argument(
        "--no-pydantic",
        action="store_true",
        help="Disable Pydantic model generation"
    )

    parser.add_argument(
        "--sqlmodel",
        action="store_true",
        default=False,
        help="Generate SQLModel ORM classes (default: False)"
    )

    parser.add_argument(
        "--gauntlet",
        action="store_true",
        default=True,
        help="Generate Gauntlet test contracts (default: True)"
    )

    parser.add_argument(
        "--no-gauntlet",
        action="store_true",
        help="Disable Gauntlet test generation"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )

    args = parser.parse_args()

    # Resolve flags
    generate_pydantic = args.pydantic and not args.no_pydantic
    generate_gauntlet = args.gauntlet and not args.no_gauntlet
    generate_sqlmodel = args.sqlmodel

    # Validate schema file exists
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"Compiling schema: {schema_path}")
        if args.verbose:
            print(f"  Pydantic: {'enabled' if generate_pydantic else 'disabled'}")
            print(f"  SQLModel: {'enabled' if generate_sqlmodel else 'disabled'}")
            print(f"  Gauntlet: {'enabled' if generate_gauntlet else 'disabled'}")

    # Run compilation
    result = compile_lattice(
        schema_path=schema_path,
        output_dir=args.output_dir,
        generate_pydantic=generate_pydantic,
        generate_sqlmodel=generate_sqlmodel,
        generate_gauntlet=generate_gauntlet,
    )

    # Report results
    if result.warnings and not args.quiet:
        for warning in result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

    if result.errors:
        for error in result.errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"Successfully compiled {len(result.entities)} entities")
        if args.verbose or len(result.generated_files) > 0:
            print(f"Generated {len(result.generated_files)} files:")
            for path in result.generated_files:
                print(f"  - {path}")

    sys.exit(0)


if __name__ == "__main__":
    main()
