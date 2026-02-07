"""
Lattice Lock Bidirectional Compiler

This module provides a comprehensive compilation pipeline for converting between
YAML, TOON, and JSON formats with full round-trip fidelity.

The compiler is designed for future-proofing at scale (10,000-100,000% growth)
while maintaining JSON as the hedge format for interoperability.

Architecture:
    Source (YAML/TOON) → Canonical AST (dict) → Target (TOON/JSON/YAML)

Key Features:
    - Bidirectional compilation (YAML ↔ TOON ↔ JSON)
    - Normalization for token-efficient TOON tables
    - Denormalization for hierarchical reconstruction
    - Format versioning and metadata
    - Comprehensive validation and round-trip testing
    - Token usage tracking and cost estimation

Usage:
    from lattice_lock.compiler import LatticeCompiler, CompilerConfig

    compiler = LatticeCompiler()

    # Compile YAML to TOON
    toon_output = compiler.compile("config.yaml", target_format="toon")

    # Compile TOON to JSON (hedge format)
    json_output = compiler.compile("config.toon", target_format="json")

    # Get token usage statistics
    stats = compiler.get_token_stats("config.yaml")

"""

from lattice_lock.compiler.core import (
    CompilationResult,
    CompilerConfig,
    LatticeCompiler,
)
from lattice_lock.compiler.formats import (
    FormatType,
    detect_format,
)
from lattice_lock.compiler.normalizer import (
    NormalizationStrategy,
    Normalizer,
)
from lattice_lock.compiler.token_tracker import (
    TokenStats,
    TokenTracker,
)

__all__ = [
    # Core compiler
    "LatticeCompiler",
    "CompilerConfig",
    "CompilationResult",
    # Formats
    "FormatType",
    "detect_format",
    # Normalization
    "Normalizer",
    "NormalizationStrategy",
    # Token tracking
    "TokenTracker",
    "TokenStats",
]
