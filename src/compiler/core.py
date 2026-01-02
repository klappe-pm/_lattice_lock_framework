"""
Lattice Lock Compiler - Core Implementation

This module provides the core LatticeCompiler class that orchestrates
bidirectional compilation between YAML, TOON, and JSON formats.

Design Principles:
    1. Canonical AST as intermediate representation (Python dict)
    2. Format detection and validation at boundaries
    3. Metadata preservation for versioning and provenance
    4. Pluggable normalization strategies
    5. JSON as guaranteed hedge format

Migration Safety:
    - All TOON output can be converted to JSON losslessly
    - Normalized tables can be denormalized to hierarchical structures
    - Format version metadata enables future migrations
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class CompilerMode(str, Enum):
    """Compilation modes for different use cases."""

    STANDARD = "standard"  # Direct format conversion
    NORMALIZED = "normalized"  # Flatten for TOON efficiency
    MINIFIED = "minified"  # Compact JSON output
    PRETTY = "pretty"  # Human-readable output


@dataclass
class CompilerConfig:
    """
    Configuration for the Lattice Compiler.

    Attributes:
        mode: Compilation mode (standard, normalized, minified, pretty)
        normalize_for_toon: Enable table normalization for TOON output
        include_metadata: Include _meta block in output
        validate_roundtrip: Verify lossless conversion
        fallback_to_json: Use JSON if TOON compilation fails
        json_first_mode: Bypass TOON entirely (emergency hedge)
        indent: Indentation for pretty output
        toon_delimiter: Delimiter for TOON tables (comma, tab, pipe)
        track_tokens: Enable token usage tracking
    """

    mode: CompilerMode = CompilerMode.STANDARD
    normalize_for_toon: bool = True
    include_metadata: bool = True
    validate_roundtrip: bool = True
    fallback_to_json: bool = True
    json_first_mode: bool = False
    indent: int = 2
    toon_delimiter: str = ","
    track_tokens: bool = True

    # Version info for format migrations
    format_version: str = "2.1"
    compiler_version: str = "1.0.0"


@dataclass
class CompilationResult:
    """
    Result of a compilation operation.

    Attributes:
        success: Whether compilation succeeded
        output: The compiled output string
        source_format: Detected source format
        target_format: Target output format
        source_path: Path to source file (if applicable)
        metadata: Compilation metadata
        warnings: List of warning messages
        errors: List of error messages
        token_stats: Token usage statistics (if tracking enabled)
        roundtrip_validated: Whether roundtrip was validated
    """

    success: bool = True
    output: str = ""
    source_format: str = ""
    target_format: str = ""
    source_path: Path | None = None
    metadata: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    token_stats: dict | None = None
    roundtrip_validated: bool = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add an error message and mark as failed."""
        self.success = False
        self.errors.append(message)


class LatticeCompiler:
    """
    Bidirectional compiler for YAML, TOON, and JSON formats.

    This compiler provides the core infrastructure for converting between
    configuration formats with full round-trip fidelity. It's designed to
    support massive scale (10,000-100,000% growth) while maintaining
    JSON as a hedge format for interoperability.

    Architecture:
        Source → parse() → Canonical AST → serialize() → Target

    The Canonical AST is a Python dict that represents the semantic content
    of the configuration, independent of the source format.

    Example:
        compiler = LatticeCompiler()

        # YAML to TOON
        result = compiler.compile("agents.yaml", target_format="toon")

        # TOON to JSON (hedge format)
        result = compiler.compile("agents.toon", target_format="json")

        # Validate round-trip
        compiler.validate_roundtrip("agents.yaml")
    """

    def __init__(self, config: CompilerConfig | None = None):
        """
        Initialize the compiler with configuration.

        Args:
            config: Compiler configuration (uses defaults if None)
        """
        self.config = config or CompilerConfig()
        self._normalizer = None
        self._token_tracker = None

        # Lazy import to avoid circular dependencies
        self._toon_available = self._check_toon_available()

    def _check_toon_available(self) -> bool:
        """Check if TOON library is available."""
        try:
            import toon_format  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def normalizer(self):
        """Lazy-load normalizer."""
        if self._normalizer is None:
            from lattice_lock.compiler.normalizer import Normalizer

            self._normalizer = Normalizer()
        return self._normalizer

    @property
    def token_tracker(self):
        """Lazy-load token tracker."""
        if self._token_tracker is None:
            from lattice_lock.compiler.token_tracker import TokenTracker

            self._token_tracker = TokenTracker()
        return self._token_tracker

    # =========================================================================
    # Core Compilation Methods
    # =========================================================================

    def compile(
        self,
        source: str | Path | dict,
        target_format: str,
        source_format: str | None = None,
        normalize: bool | None = None,
    ) -> CompilationResult:
        """
        Compile source to target format.

        Args:
            source: Source file path, string content, or dict AST
            target_format: Target format ("yaml", "toon", "json")
            source_format: Source format (auto-detected if None)
            normalize: Override normalization setting

        Returns:
            CompilationResult with output and metadata
        """
        result = CompilationResult(target_format=target_format)

        try:
            # Step 1: Parse source to AST
            ast, detected_format, source_path = self._parse_source(source, source_format)
            result.source_format = detected_format
            result.source_path = source_path

            # Step 2: Apply normalization if requested
            should_normalize = (
                normalize
                if normalize is not None
                else (self.config.normalize_for_toon and target_format == "toon")
            )

            if should_normalize:
                ast = self.normalizer.normalize(ast)

            # Step 3: Add metadata
            if self.config.include_metadata:
                ast = self._add_metadata(ast, detected_format, target_format, source_path)

            # Step 4: Serialize to target format
            output = self._serialize(ast, target_format)
            result.output = output

            # Step 5: Validate round-trip if requested
            if self.config.validate_roundtrip:
                roundtrip_valid = self._validate_roundtrip(ast, output, target_format)
                result.roundtrip_validated = roundtrip_valid
                if not roundtrip_valid:
                    result.add_warning("Round-trip validation failed - output may not be lossless")

            # Step 6: Track tokens if enabled
            if self.config.track_tokens:
                result.token_stats = self.token_tracker.analyze(output, target_format)

            # Step 7: Store metadata in result
            result.metadata = ast.get("_meta", {}) if isinstance(ast, dict) else {}

        except Exception as e:
            result.add_error(f"Compilation failed: {str(e)}")

            # Fallback to JSON if configured
            if self.config.fallback_to_json and target_format == "toon":
                result.add_warning("Falling back to JSON format")
                try:
                    fallback_result = self.compile(source, "json", source_format)
                    if fallback_result.success:
                        return fallback_result
                except Exception:
                    pass

        return result

    def compile_to_all_formats(
        self,
        source: str | Path | dict,
        output_dir: Path | None = None,
    ) -> dict[str, CompilationResult]:
        """
        Compile source to all supported formats.

        Args:
            source: Source file path, string content, or dict AST
            output_dir: Directory to write output files (None for in-memory only)

        Returns:
            Dict mapping format names to CompilationResults
        """
        results = {}

        for fmt in ["yaml", "json", "toon"]:
            result = self.compile(source, fmt)
            results[fmt] = result

            if output_dir and result.success:
                source_path = result.source_path or Path("compiled")
                output_path = output_dir / f"{source_path.stem}.{fmt}"
                output_path.write_text(result.output)

        return results

    # =========================================================================
    # Parsing Methods
    # =========================================================================

    def _parse_source(
        self,
        source: str | Path | dict,
        source_format: str | None = None,
    ) -> tuple[dict, str, Path | None]:
        """
        Parse source into canonical AST.

        Args:
            source: Source file path, string content, or dict AST
            source_format: Source format (auto-detected if None)

        Returns:
            Tuple of (AST dict, detected format, source path)
        """
        source_path = None

        # Handle dict input (already an AST)
        if isinstance(source, dict):
            return source, "dict", None

        # Handle Path or string path
        if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
            source_path = Path(source)
            content = source_path.read_text()

            if source_format is None:
                source_format = self._detect_format_from_path(source_path)
        else:
            content = source
            if source_format is None:
                source_format = self._detect_format_from_content(content)

        # Parse based on format
        if source_format == "yaml":
            ast = yaml.safe_load(content)
        elif source_format == "json":
            ast = json.loads(content)
        elif source_format == "toon":
            ast = self._parse_toon(content)
        else:
            raise ValueError(f"Unknown source format: {source_format}")

        return ast, source_format, source_path

    def _detect_format_from_path(self, path: Path) -> str:
        """Detect format from file extension."""
        suffix = path.suffix.lower()
        format_map = {
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".toon": "toon",
        }
        return format_map.get(suffix, "yaml")

    def _detect_format_from_content(self, content: str) -> str:
        """Detect format from content heuristics."""
        content = content.strip()

        # JSON detection
        if content.startswith("{") or content.startswith("["):
            try:
                json.loads(content)
                return "json"
            except json.JSONDecodeError:
                pass

        # TOON detection (look for tabular headers)
        if "[" in content and "]{" in content and "}:" in content:
            return "toon"

        # Default to YAML
        return "yaml"

    def _parse_toon(self, content: str) -> dict:
        """Parse TOON content to AST."""
        if not self._toon_available:
            raise ImportError(
                "TOON format library not available. " "Install with: pip install toon-format"
            )

        import toon_format

        return toon_format.decode(content)

    # =========================================================================
    # Serialization Methods
    # =========================================================================

    def _serialize(self, ast: dict, target_format: str) -> str:
        """
        Serialize AST to target format.

        Args:
            ast: Canonical AST dict
            target_format: Target format ("yaml", "json", "toon")

        Returns:
            Serialized string output
        """
        if target_format == "yaml":
            return self._serialize_yaml(ast)
        elif target_format == "json":
            return self._serialize_json(ast)
        elif target_format == "toon":
            return self._serialize_toon(ast)
        else:
            raise ValueError(f"Unknown target format: {target_format}")

    def _serialize_yaml(self, ast: dict) -> str:
        """Serialize AST to YAML."""
        if self.config.mode == CompilerMode.MINIFIED:
            return yaml.dump(ast, default_flow_style=True)
        return yaml.dump(ast, default_flow_style=False, indent=self.config.indent)

    def _serialize_json(self, ast: dict) -> str:
        """Serialize AST to JSON."""
        if self.config.mode == CompilerMode.MINIFIED:
            return json.dumps(ast, separators=(",", ":"))
        return json.dumps(ast, indent=self.config.indent)

    def _serialize_toon(self, ast: dict) -> str:
        """Serialize AST to TOON."""
        if self.config.json_first_mode:
            # Emergency hedge - bypass TOON
            return self._serialize_json(ast)

        if not self._toon_available:
            if self.config.fallback_to_json:
                return self._serialize_json(ast)
            raise ImportError(
                "TOON format library not available. " "Install with: pip install toon-format"
            )

        import toon_format

        options = {
            "delimiter": self.config.toon_delimiter,
            "indent": self.config.indent,
        }

        return toon_format.encode(ast, options)

    # =========================================================================
    # Metadata and Validation
    # =========================================================================

    def _add_metadata(
        self,
        ast: dict,
        source_format: str,
        target_format: str,
        source_path: Path | None,
    ) -> dict:
        """Add compilation metadata to AST."""
        meta = {
            "_meta": {
                "format_version": self.config.format_version,
                "compiler_version": self.config.compiler_version,
                "source_format": source_format,
                "target_format": target_format,
                "source_path": str(source_path) if source_path else None,
                "compiled_at": datetime.now(timezone.utc).isoformat(),
                "normalized": self.config.normalize_for_toon and target_format == "toon",
            }
        }

        # Preserve existing metadata if present
        if "_meta" in ast:
            meta["_meta"].update(ast.get("_meta", {}))

        return {**meta, **{k: v for k, v in ast.items() if k != "_meta"}}

    def _validate_roundtrip(self, original_ast: dict, output: str, target_format: str) -> bool:
        """
        Validate that output can be parsed back to equivalent AST.

        Args:
            original_ast: Original AST before serialization
            output: Serialized output string
            target_format: Format of the output

        Returns:
            True if round-trip produces equivalent AST
        """
        try:
            # Parse output back to AST
            restored_ast, _, _ = self._parse_source(output, target_format)

            # Compare (ignoring _meta which may differ)
            original_clean = {k: v for k, v in original_ast.items() if k != "_meta"}
            restored_clean = {k: v for k, v in restored_ast.items() if k != "_meta"}

            return self._deep_equal(original_clean, restored_clean)
        except Exception:
            return False

    def _deep_equal(self, a: Any, b: Any) -> bool:
        """Deep equality check for AST comparison."""
        if type(a) is not type(b):
            return False

        if isinstance(a, dict):
            if set(a.keys()) != set(b.keys()):
                return False
            return all(self._deep_equal(a[k], b[k]) for k in a)

        if isinstance(a, list):
            if len(a) != len(b):
                return False
            return all(self._deep_equal(x, y) for x, y in zip(a, b, strict=True))

        return a == b

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def yaml_to_toon(self, source: str | Path) -> str:
        """Convert YAML to TOON format."""
        result = self.compile(source, "toon", "yaml")
        if not result.success:
            raise ValueError(f"Conversion failed: {result.errors}")
        return result.output

    def toon_to_json(self, source: str | Path) -> str:
        """Convert TOON to JSON format (hedge format)."""
        result = self.compile(source, "json", "toon")
        if not result.success:
            raise ValueError(f"Conversion failed: {result.errors}")
        return result.output

    def toon_to_yaml(self, source: str | Path) -> str:
        """Convert TOON to YAML format."""
        result = self.compile(source, "yaml", "toon")
        if not result.success:
            raise ValueError(f"Conversion failed: {result.errors}")
        return result.output

    def json_to_toon(self, source: str | Path) -> str:
        """Convert JSON to TOON format."""
        result = self.compile(source, "toon", "json")
        if not result.success:
            raise ValueError(f"Conversion failed: {result.errors}")
        return result.output

    def get_token_stats(self, source: str | Path) -> dict[str, dict]:
        """
        Get token statistics for source in all formats.

        Args:
            source: Source file path or content

        Returns:
            Dict mapping format names to token statistics
        """
        results = self.compile_to_all_formats(source)

        stats = {}
        for fmt, result in results.items():
            if result.success and result.token_stats:
                stats[fmt] = result.token_stats

        return stats

    def validate_roundtrip(self, source: str | Path) -> dict[str, bool]:
        """
        Validate round-trip conversion for all format pairs.

        Args:
            source: Source file path or content

        Returns:
            Dict mapping format pairs to validation results
        """
        ast, source_format, _ = self._parse_source(source)

        validations = {}
        formats = ["yaml", "json", "toon"]

        for target in formats:
            try:
                result = self.compile(ast, target)
                if result.success:
                    # Try to parse back
                    restored_ast, _, _ = self._parse_source(result.output, target)

                    # Compare
                    original_clean = {k: v for k, v in ast.items() if k != "_meta"}
                    restored_clean = {k: v for k, v in restored_ast.items() if k != "_meta"}

                    validations[f"{source_format}→{target}"] = self._deep_equal(
                        original_clean, restored_clean
                    )
                else:
                    validations[f"{source_format}→{target}"] = False
            except Exception:
                validations[f"{source_format}→{target}"] = False

        return validations
