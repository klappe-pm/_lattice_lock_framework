# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Expanded model registry with GPT-4o-mini, o1-mini, Claude 3.5 Haiku, and Claude 3.5 Opus.
- Thread-safe singleton pattern for `ProviderAvailability`.
- Robust resource cleanup using `asyncio.shield`.

### Fixed
- Corrected CI paths in example workflows from `pilot_projects/` to `docs/examples/`.

