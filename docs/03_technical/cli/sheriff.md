---
title: Sheriff CLI
type: reference
status: stable
categories:
  - Technical
  - CLI
sub_categories:
  - Governance
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids:
  - cli-sheriff-001
tags:
  - sheriff
  - cli
  - validation
---

# sheriff

AST-based validation for import discipline and type hint compliance.

## Synopsis

```bash
lattice-lock sheriff [OPTIONS] PATH
```

## Description

The `sheriff` command performs static analysis on Python files using Abstract Syntax Tree (AST) parsing. It enforces import discipline, type hint requirements, and other code governance rules defined in `lattice.yaml`.

Sheriff supports multiple output formats for CI/CD integration and includes file-based caching for improved performance on large codebases.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PATH` | Yes | Path to file or directory to validate |

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--lattice` | path | `lattice.yaml` | Path to the lattice.yaml configuration file. Auto-detected if not provided. |
| `--fix` | flag | | Attempt to auto-correct violations where possible (not yet implemented) |
| `--ignore` | string (multiple) | | Glob patterns for files or directories to ignore |
| `--format` | choice | `text` | Output format: `text`, `json`, `github`, `junit` |
| `--json` | flag | | **[DEPRECATED]** Use `--format json` instead |
| `--cache` / `--no-cache` | flag | `--cache` | Enable/disable file caching |
| `--cache-dir` | path | `.sheriff_cache` | Directory to store cache files |
| `--clear-cache` | flag | | Clear the cache before running validation |

## Output Formats

### text (default)

Human-readable terminal output with colored indicators.

```
Sheriff Validation Results for src/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

src/services/api.py:15 - LL001 - Forbidden import: os.system
src/services/api.py:42 - LL002 - Missing type hint on function 'process_data'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 2 violation(s)
```

### json

Machine-readable JSON output for programmatic processing.

```json
{
  "violations": [
    {
      "rule_id": "LL001",
      "message": "Forbidden import: os.system",
      "line_number": 15,
      "filename": "src/services/api.py"
    }
  ],
  "ignored_violations": [],
  "count": 1,
  "ignored_count": 0,
  "target": "src/",
  "success": false
}
```

### github

GitHub Actions annotations format for inline PR comments.

```
::error file=src/services/api.py,line=15::LL001 - Forbidden import: os.system
::error file=src/services/api.py,line=42::LL002 - Missing type hint on function 'process_data'
```

### junit

JUnit XML format for CI tools like Jenkins, Azure DevOps, CircleCI.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Sheriff" tests="2" failures="2">
  <testcase name="src/services/api.py:15" classname="LL001">
    <failure message="Forbidden import: os.system"/>
  </testcase>
</testsuite>
```

## Caching

Sheriff uses file-based caching to skip unchanged files, significantly improving performance on large codebases and in CI pipelines.

### How Caching Works

1. Each file's content is hashed
2. If the hash matches a cached entry, cached violations are returned
3. Cache is invalidated when `lattice.yaml` configuration changes
4. Cache is stored in `.sheriff_cache/` by default

### Cache Management

```bash
# Disable caching for a full scan
lattice-lock sheriff src/ --no-cache

# Clear cache before scanning
lattice-lock sheriff src/ --clear-cache

# Use custom cache directory
lattice-lock sheriff src/ --cache-dir /tmp/sheriff_cache
```

## Validation Rules

Sheriff enforces rules defined in your `lattice.yaml` configuration:

### Forbidden Imports (LL001)

```yaml
config:
  forbidden_imports:
    - os.system
    - subprocess.call
    - eval
    - exec
```

### Required Patterns (LL002)

```yaml
config:
  required_patterns:
    - type_hints
    - docstrings
```

## Ignore Patterns

Exclude files or directories from validation:

```bash
# Ignore test files
lattice-lock sheriff src/ --ignore "**/test_*.py"

# Ignore multiple patterns
lattice-lock sheriff . --ignore "**/migrations/*" --ignore "**/generated/*"

# Ignore temporary directories
lattice-lock sheriff . --ignore "*/temp_dir/*"
```

## Examples

### Basic Usage

Validate a directory:

```bash
lattice-lock sheriff src/
```

Validate a single file:

```bash
lattice-lock sheriff src/services/api.py
```

### Custom Configuration

Use a specific lattice.yaml:

```bash
lattice-lock sheriff src/ --lattice configs/strict-lattice.yaml
```

### CI/CD Integration

#### GitHub Actions

```yaml
- name: Run Sheriff
  run: lattice-lock sheriff src/ --format github
```

#### Jenkins / JUnit

```yaml
- name: Run Sheriff
  run: lattice-lock sheriff src/ --format junit > sheriff-results.xml

- name: Publish Results
  uses: mikepenz/action-junit-report@v3
  with:
    report_paths: 'sheriff-results.xml'
```

### JSON Processing

```bash
# Parse with jq
lattice-lock sheriff src/ --format json | jq '.violations | length'

# Check success status
if lattice-lock sheriff src/ --format json | jq -e '.success' > /dev/null; then
  echo "No violations found"
fi
```

### Performance Optimization

```bash
# First run - builds cache
lattice-lock sheriff src/

# Subsequent runs - uses cache (faster)
lattice-lock sheriff src/

# Force full scan
lattice-lock sheriff src/ --no-cache
```

## Ignored Violations

Sheriff tracks violations that are ignored via configuration (e.g., `# noqa` comments or lattice.yaml ignore rules). These are reported separately in the audit output.

### Text Format Audit Output

```
Sheriff audited 3 ignored violations in src/:
  src/legacy/old_api.py:15 - LL001 - Forbidden import: os.system (IGNORED)
```

### JSON Format

```json
{
  "violations": [],
  "ignored_violations": [
    {
      "rule_id": "LL001",
      "message": "Forbidden import: os.system",
      "line_number": 15,
      "filename": "src/legacy/old_api.py"
    }
  ],
  "count": 0,
  "ignored_count": 1,
  "success": true
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No violations found |
| `1` | One or more violations found, or path/configuration error |

## Configuration Auto-Detection

If `--lattice` is not specified, Sheriff searches for `lattice.yaml` in:
1. Current working directory
2. Parent directories (recursively up to root)

If no configuration is found, Sheriff uses default rules.

## See Also

- [CLI Overview](docs/reference/cli/index.md)
- [validate](validate.md) - Schema and structure validation
- [gauntlet](docs/reference/cli/gauntlet.md) - Semantic test generation
- [Configuration Reference](docs/reference/configuration.md) - lattice.yaml schema
