# lattice-lock validate

Validate a Lattice Lock project against schemas and governance rules.

## Synopsis

```bash
lattice-lock validate [OPTIONS]
```

## Description

The `validate` command runs multiple validators against a Lattice Lock project to ensure compliance with framework standards. By default, it runs all validators; specific validators can be selected using flags.

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--path` | `-p` | path | `.` | Path to project directory to validate |
| `--fix` | | flag | | Auto-fix issues where possible (trailing whitespace, missing EOF newline) |
| `--schema-only` | | flag | | Run only schema validation (lattice.yaml) |
| `--env-only` | | flag | | Run only environment file validation (.env) |
| `--agents-only` | | flag | | Run only agent manifest validation |
| `--structure-only` | | flag | | Run only repository structure validation |

## Validators

### Schema Validation

Validates `lattice.yaml` and `lattice.yml` files against the Lattice Lock schema.

**Checks:**
- Valid YAML syntax
- Required fields present
- Correct field types
- Valid entity definitions
- Constraint syntax

**Files checked:** `**/lattice.yaml`, `**/lattice.yml`

### Environment Validation

Validates environment configuration files for security and completeness.

**Checks:**
- No sensitive values in committed `.env` files
- Required variables defined
- Valid syntax and formatting

**Files checked:** `.env`, `.env.example`, `.env.template`

### Agent Manifest Validation

Validates AI agent definition files.

**Checks:**
- Valid agent configuration
- Required fields present
- Correct structure

**Files checked:** `*_definition.yaml`, `*_definition.yml`, `agent.yaml`

### Structure Validation

Validates the repository directory structure against Lattice Lock conventions.

**Checks:**
- Required directories exist
- Proper file organization
- Naming conventions followed

## Auto-Fix Feature

The `--fix` flag automatically corrects common issues:

- **Trailing whitespace**: Removes whitespace at the end of lines
- **Missing EOF newline**: Ensures files end with a newline character

**Supported file extensions:** `.py`, `.yaml`, `.yml`, `.md`, `.txt`, `.json`, `.toml`

**Excluded directories:** `.git`, `__pycache__`, `node_modules`, `.venv`

## Examples

### Validate Current Directory

```bash
lattice-lock validate
```

### Validate Specific Directory

```bash
lattice-lock validate --path ~/projects/my_project
```

### Auto-Fix Issues

```bash
lattice-lock validate --fix
```

### Schema Validation Only

```bash
lattice-lock validate --schema-only
```

### Environment Validation Only

```bash
lattice-lock validate --env-only
```

### Verbose Output

Show detailed validation results including warnings:

```bash
lattice-lock -v validate
```

### Combine Path and Fix

```bash
lattice-lock validate --path ./src --fix
```

## Output Format

### Success Output

```
Validating project at: /path/to/project

Schema Validation:
  ✓ lattice.yaml: passed

Environment Validation:
  ⚠ No .env file found

Agent Manifest Validation:
  ⚠ No agent definitions found

Structure Validation:
  ✓ Repository structure: passed

==================================================
✓ All validations passed!
```

### Warning Output

```
Schema Validation:
  ⚠ lattice.yaml: passed with warnings
    ⚠ Field 'description' is recommended (line 12)

==================================================
⚠ Validation passed with 1 warning(s)
```

### Failure Output

```
Schema Validation:
  ✗ lattice.yaml: failed
    ✗ Missing required field 'version' (line 1)
    ✗ Invalid entity type 'unknown' (line 15)

==================================================
✗ Validation failed: 2 error(s), 0 warning(s)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All validations passed (may include warnings) |
| `1` | One or more validation errors |

## CI/CD Integration

The validate command is designed for CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Validate Project
  run: lattice-lock validate --path .

# Fail on any validation error
- name: Strict Validation
  run: lattice-lock validate
```

## See Also

- [CLI Overview](docs/reference/cli/index.md)
- [sheriff](docs/reference/cli/sheriff.md) - AST-based code validation
- [doctor](doctor.md) - Environment health check
- [Configuration Reference](docs/reference/configuration.md) - lattice.yaml schema
