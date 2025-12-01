# Lattice-Lock Versioning Strategy

## Overview

This document defines the versioning strategy for the Lattice-Lock Framework, a governance-first code generation system where version consistency is critical for maintaining the integrity of the "governance cage" architecture.

## Version Format

Lattice-Lock uses **Semantic Versioning 2.0.0** (semver.org) with the format:

```
MAJOR.MINOR.PATCH
```

Example: `2.1.0`

### Version Components

- **MAJOR**: Incompatible API changes, breaking schema changes, or architectural redesigns
- **MINOR**: New features, backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes, security patches, documentation updates

## Version Scope

Lattice-Lock maintains **dual versioning**:

1. **Framework Version**: Overall system version (in `version.txt`)
2. **Lattice Schema Version**: Individual schema versions (in `lattice.yaml` files)

### Framework Version

The framework version tracks the overall Lattice-Lock system including:

- Compiler (`compile_lattice.py`)
- Sheriff enforcement (`sheriff.py`)
- Orchestrator logic
- Core architecture components

**Location**: `version.txt` in repository root

### Lattice Schema Version

Each `lattice.yaml` file contains its own version identifier:

```yaml
version: v2.1
generated_module: types_v2
```

This allows multiple schema versions to coexist and enables controlled migrations.

## Versioning Rules

### MAJOR Version Increments (X.0.0)

Increment MAJOR when making incompatible changes such as:

- **Breaking schema format changes** that require existing `lattice.yaml` files to be rewritten
- **Compiler output format changes** that break existing generated code
- **Sheriff rule changes** that would reject previously valid code
- **Removal of core features** or supported patterns
- **Fundamental architecture changes** affecting the governance model

**Migration Required**: Yes
**Backward Compatibility**: No

**Example**: v2.0.0 → v3.0.0 when changing from JSON to YAML schema format

### MINOR Version Increments (x.Y.0)

Increment MINOR when adding functionality in a backward-compatible manner:

- **New schema features** (e.g., adding `ensures:` clauses, new field types)
- **Enhanced compiler capabilities** (e.g., generating additional artifacts)
- **New Sheriff rules** that don't reject existing valid code
- **New governance layers** (e.g., adding The Gauntlet)
- **Performance improvements** without API changes
- **New agent roles or patterns**

**Migration Required**: No (but new features available)
**Backward Compatibility**: Yes

**Example**: v2.0.0 → v2.1.0 when adding semantic contract support

### PATCH Version Increments (x.y.Z)

Increment PATCH for backward-compatible bug fixes:

- **Bug fixes** in compiler, sheriff, or orchestrator
- **Security patches** that don't change APIs
- **Documentation updates**
- **Dependency updates** (security or compatibility)
- **Error message improvements**
- **Performance optimizations** without behavior changes

**Migration Required**: No
**Backward Compatibility**: Yes

**Example**: v2.1.0 → v2.1.1 when fixing a sheriff AST parsing bug

## Schema Version Management

### Schema Versioning Pattern

Lattice schemas follow a simplified version pattern in `lattice.yaml`:

```yaml
version: v2.1
```

- Major schema changes: `v2` → `v3`
- Minor schema changes: `v2.0` → `v2.1`
- Patches typically don't affect schema version

### Generated Module Naming

The `generated_module` field must align with schema version:

```yaml
version: v2.1
generated_module: types_v2  # Uses major version only
```

This enables:

- Multiple schema versions to coexist in the same codebase
- Gradual migrations between versions
- Rollback capabilities

### Version Compatibility Matrix

| Framework | Schema v1 | Schema v2 | Schema v3 |
|-----------|-----------|-----------|-----------|
| v1.x | ✅ Full | ❌ Not supported | ❌ Not supported |
| v2.x | ⚠️ Deprecated | ✅ Full | ❌ Not supported |
| v3.x | ❌ Not supported | ✅ Full | ✅ Full |

## Release Process

### 1. Pre-Release Checklist

- [ ] All tests pass (Sheriff validation, Gauntlet contracts)
- [ ] Documentation updated (README, context docs)
- [ ] CHANGELOG.md updated with version details
- [ ] Version numbers updated in all locations
- [ ] Breaking changes documented
- [ ] Migration guide prepared (for MAJOR/MINOR)

### 2. Version Update Locations

When releasing a new version, update:

1. `version.txt` - Framework version
2. `readme.md` - Badge and references
3. `CHANGELOG.md` - Release notes
4. Schema files (if applicable) - `lattice.yaml` version field
5. Documentation references

### 3. Git Tagging

Tag releases with the format: `vMAJOR.MINOR.PATCH`

```bash
git tag -a v2.1.0 -m "Release v2.1.0: Semantic contract support"
git push origin v2.1.0
```

### 4. Release Notes

Each release must include:

- **Version number**
- **Release date**
- **Type** (major/minor/patch)
- **Summary** of changes
- **Breaking changes** (if any)
- **Migration guide** (if required)
- **Known issues**

## Deprecation Policy

### Deprecation Timeline

Features marked for deprecation follow this timeline:

1. **Announcement**: Feature marked as deprecated in MINOR release
2. **Warning Period**: Minimum 2 MINOR versions or 6 months
3. **Removal**: Removed in next MAJOR version

### Deprecation Communication

Deprecated features are communicated through:

- Warning messages in Sheriff/Compiler output
- Documentation updates with migration paths
- CHANGELOG.md deprecation notices
- README.md update with alternatives

## Migration Guides

### Schema Migration

When upgrading schema versions:

1. **Create new schema file** with updated version
2. **Run compiler** to generate new types module
3. **Update imports** to use new generated module
4. **Validate with Sheriff** against new rules
5. **Run Gauntlet** to ensure semantic compliance
6. **Remove old schema** once migration complete

### Framework Migration

MAJOR version upgrades may require:

1. **Review CHANGELOG** for breaking changes
2. **Update tooling** (compiler, sheriff, orchestrator)
3. **Migrate schemas** following schema migration process
4. **Update agent prompts** if role definitions changed
5. **Validate all governance layers** work correctly

## Version History

### Current Version: 2.1.0

- **Status**: Production-ready
- **Release Date**: November 2025
- **Major Changes**:
  - Semantic contract enforcement via `ensures:` clauses
  - The Gauntlet auto-generated test suite
  - Enhanced schema expressiveness
  - Production deployment in regulated industries

### Version Roadmap

#### V2.2.0 (Planned)

- JSONSchema integration for meta-schema validation
- Enhanced ORM support (additional frameworks)
- Improved error messages and developer experience

#### V2.3.0 (Planned)

- Multi-language support (TypeScript, Go)
- Enhanced dependency management
- Performance optimizations

#### V3.0.0 (Future)

- Next-generation governance architecture
- Cloud-native orchestration
- Advanced semantic verification

## Best Practices

### For Framework Developers

1. **Never break backward compatibility** in MINOR/PATCH releases
2. **Write comprehensive migration guides** for MAJOR releases
3. **Maintain version compatibility matrix** documentation
4. **Test against multiple schema versions** before release
5. **Use feature flags** for experimental features

### For Lattice-Lock Users

1. **Pin framework version** in production environments
2. **Test schema upgrades** in staging before production
3. **Read CHANGELOG** before upgrading
4. **Follow migration guides** carefully for MAJOR versions
5. **Report version-related issues** promptly

## Governance Implications

Version changes affect the governance model differently:

| Change Type | Compiler | Sheriff | Gauntlet | Schema |
|-------------|----------|---------|----------|--------|
| PATCH | May update | May update | May update | No change |
| MINOR | May enhance | May add rules | May enhance | May extend |
| MAJOR | May redesign | May redesign | May redesign | May break |

The **governance cage** integrity must be maintained across all version changes to preserve Lattice-Lock's core value proposition.

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Lattice-Lock Project Context](../context/Lattice-Lock_Project_Context.md)
- [Framework Specification](../research/Lattice-Lock%20LLM%20Specification.txt)

---

**Document Version**: 1.0.0
**Last Updated**: November 28, 2025
**Author**: Kevin Lappe
