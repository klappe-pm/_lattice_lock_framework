---
title: "Doctor CLI"
type: reference
status: stable
categories: [Technical, CLI]
sub_categories: [Diagnostics]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [cli-doctor-001]
tags: [doctor, cli, diagnostics]
author: DevOps Agent
---

# lattice-lock doctor

Check environment health for Lattice Lock.

## Synopsis

```bash
lattice-lock doctor [OPTIONS]
```

## Description

The `doctor` command performs a comprehensive health check of your development environment. It verifies Python version, required dependencies, environment variables, and optional tools needed for Lattice Lock projects.

## Options

This command has no specific options beyond the global `--verbose` flag.

## Health Checks

### System Checks

| Check | Required | Description |
|-------|----------|-------------|
| Python Version | Yes | Verifies Python >= 3.10 is installed |
| Git | Yes | Verifies Git is available in PATH |

### Dependency Checks

#### Required Dependencies

| Package | Description |
|---------|-------------|
| `click` | CLI framework |
| `jinja2` | Template engine |
| `pyyaml` | YAML parser |

#### Optional Dependencies

| Package | Description |
|---------|-------------|
| `pytest` | Testing framework |
| `ruff` | Linting |
| `mypy` | Type checking |

### Environment Variables

All environment variable checks are optional but recommended:

| Variable | Description |
|----------|-------------|
| `LATTICE_LOCK_CONFIG` | Lattice Lock configuration path |
| `ORCHESTRATOR_STRATEGY` | AI orchestration strategy |
| `LOG_LEVEL` | Logging verbosity |
| `OPENAI_API_KEY` | OpenAI API key (masked in output) |
| `ANTHROPIC_API_KEY` | Anthropic API key (masked in output) |

### AI Tools

| Tool | Required | Description |
|------|----------|-------------|
| Ollama | No | Local LLM runtime - checks if installed and running |

## Output Indicators

| Symbol | Color | Meaning |
|--------|-------|---------|
| `✓` | Green | Required check passed |
| `✓` | Cyan | Optional check passed |
| `○` | Yellow | Optional check not passed |
| `✗` | Red | Required check failed |

## Examples

### Basic Health Check

```bash
lattice-lock doctor
```

### Verbose Output

```bash
lattice-lock -v doctor
```

## Sample Output

### Healthy Environment

```
Lattice Lock Environment Health Check
==================================================

System:
  ✓ Python Version: Python 3.11.4 (>= 3.10 required)
  ✓ Git: git version 2.42.0

Dependencies:
  ✓ Dependency: click: CLI framework v8.1.7
  ✓ Dependency: jinja2: Template engine v3.1.2
  ✓ Dependency: pyyaml: YAML parser v6.0.1
  ✓ Dependency: pytest: Testing framework v7.4.3
  ✓ Dependency: ruff: Linting v0.1.6
  ✓ Dependency: mypy: Type checking v1.7.1

Environment Variables:
  ✓ Env: LATTICE_LOCK_CONFIG: Lattice Lock configuration path = ./lattice.yaml
  ○ Env: ORCHESTRATOR_STRATEGY: AI orchestration strategy - not set
  ✓ Env: LOG_LEVEL: Logging verbosity = INFO
  ✓ Env: OPENAI_API_KEY: OpenAI API key = sk-p****jK9s
  ○ Env: ANTHROPIC_API_KEY: Anthropic API key - not set

AI Tools:
  ✓ Ollama: Ollama running with 3 model(s) available

==================================================
Summary:
  Required: 5/5 checks passed
  Optional: 7/10 checks passed

✓ Environment is healthy!
```

### Environment with Issues

```
Lattice Lock Environment Health Check
==================================================

System:
  ✗ Python Version: Python 3.9.7 is below minimum 3.10
  ✓ Git: git version 2.42.0

Dependencies:
  ✓ Dependency: click: CLI framework v8.1.7
  ✓ Dependency: jinja2: Template engine v3.1.2
  ✗ Dependency: pyyaml: YAML parser - NOT INSTALLED
  ○ Dependency: pytest: Testing framework - not installed (optional)
  ○ Dependency: ruff: Linting - not installed (optional)
  ○ Dependency: mypy: Type checking - not installed (optional)

Environment Variables:
  ○ Env: LATTICE_LOCK_CONFIG: Lattice Lock configuration path - not set
  ○ Env: ORCHESTRATOR_STRATEGY: AI orchestration strategy - not set
  ○ Env: LOG_LEVEL: Logging verbosity - not set
  ○ Env: OPENAI_API_KEY: OpenAI API key - not set
  ○ Env: ANTHROPIC_API_KEY: Anthropic API key - not set

AI Tools:
  ○ Ollama: Ollama CLI not found in PATH (optional)

==================================================
Summary:
  Required: 3/5 checks passed
  Optional: 0/10 checks passed

✗ Some required checks failed. Please fix the issues above.
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All required checks passed |
| `1` | One or more required checks failed |

## Troubleshooting

### Python Version Too Low

Upgrade Python to 3.10 or higher:

```bash
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3.11

# Windows
# Download from python.org
```

### Missing Dependencies

Install required dependencies:

```bash
pip install click jinja2 pyyaml
```

Install all optional dependencies:

```bash
pip install pytest ruff mypy
```

### Ollama Not Running

Start the Ollama server:

```bash
ollama serve
```

### Git Not Found

Install Git:

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from git-scm.com
```

## See Also

- [CLI Overview](docs/reference/cli/index.md)
- [validate](validate.md) - Project validation
- [Getting Started Guide](interactive_onboarding_guide.md)
