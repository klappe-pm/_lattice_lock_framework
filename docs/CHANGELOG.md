# Changelog

All notable changes to the Lattice Lock Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Feature flags system
- Enhanced consensus engine with stance steering
- Chain orchestrator step tracking
- MCP server implementation

## [2.1.0] - 2026-01-01

### Added

- **Consensus Engine:** New multi-model voting and synthesis capabilities.
- **PAL MCP Analysis:** Comprehensive gap analysis against PAL MCP server.
- **Model Orchestrator:** Enhanced routing with providers for Grok, Gemini 2.5, and Claude 3.7.
- **Vision Support:** Full support for image inputs in TaskRequirements.

### Changed

- Refactored `models.yaml` to include reasoning and coding scores.
- Updated `ModelScorer` to use multi-dimensional scoring (speed, cost, quality).
- Improved CLI error handling and output formatting.

### Fixed

- Resolved fallback issues with `claude-3-5-sonnet`.
- Fixed Bedrock provider credential handling in tests.
- Addressed E2E test matrix failures.

## [2.0.0] - 2025-12-01

### Added

- **Sheriff:** Initial release of AST-based static analysis engine.
- **Gauntlet:** Runtime test generation from `lattice.yaml` policies.
- **Lattice CLI:** Unified command-line interface.

### Changed

- **Breaking:** Complete architecture overhaul from v1.x script collection to framework.
- Standardized configuration on `lattice.yaml`.

## [1.0.0] - 2025-10-15

- Initial release of core scripts and utilities.
