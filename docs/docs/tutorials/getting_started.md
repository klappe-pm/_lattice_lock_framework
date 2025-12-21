# Getting Started with Lattice Lock

Welcome to Lattice Lock! This guide walks you through setting up your development environment and running your first Lattice Lock commands.

## Prerequisites Checklist

Before you begin, ensure you have the following installed:

### Required

- [ ] **Python 3.10 or higher**
  ```bash
  python3 --version
  # Expected: Python 3.10.x or higher
  ```

- [ ] **pip** (Python package manager)
  ```bash
  pip --version
  # Expected: pip 21.x or higher
  ```

- [ ] **Git** (version control)
  ```bash
  git --version
  # Expected: git version 2.x.x
  ```

### Optional (for AI features)

- [ ] **Ollama** (for local AI models)
  ```bash
  ollama --version
  # Expected: ollama version x.x.x
  ```

- [ ] **API Keys** for cloud AI providers:
  - `OPENAI_API_KEY` - For OpenAI models
  - `ANTHROPIC_API_KEY` - For Claude models

## Step 1: Install Lattice Lock

Choose your preferred installation method:

### Option A: Install from PyPI (Recommended)

```bash
pip install lattice-lock
```

### Option B: Install from Source

```bash
# Clone the repository
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Step 2: Verify Installation

Run the following command to verify Lattice Lock is installed correctly:

```bash
lattice-lock --version
```

**Expected output:**
```
lattice-lock, version X.X.X
```

## Step 3: Run the Doctor Command

The `doctor` command checks your environment for common issues:

```bash
lattice-lock doctor
```

**Expected output:**
```
Lattice Lock Environment Health Check
==================================================

System:
  ✓ Python Version: Python 3.11.4 (>= 3.10 required)
  ✓ Git: git version 2.39.0

Dependencies:
  ✓ Dependency: click: CLI framework v8.1.x
  ✓ Dependency: jinja2: Template engine v3.1.x
  ✓ Dependency: pyyaml: YAML parser v6.0.x
  ✓ Dependency: pytest: Testing framework v7.x.x
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
  Required: 5/5 checks passed
  Optional: 3/8 checks passed

✓ Environment is healthy!
```

### Understanding the Output

| Symbol | Meaning |
|--------|---------|
| ✓ (green) | Required check passed |
| ✓ (cyan) | Optional check passed |
| ○ (yellow) | Optional check not passed (warning) |
| ✗ (red) | Required check failed (error) |

If you see `✓ Environment is healthy!` at the bottom, you're ready to proceed!

### Troubleshooting Common Issues

#### Python Version Too Low

```
✗ Python Version: Python 3.8.10 is below minimum 3.10
```

**Fix:** Install Python 3.10 or higher from [python.org](https://www.python.org/downloads/) or use a version manager like `pyenv`:

```bash
# Using pyenv
pyenv install 3.11.4
pyenv global 3.11.4
```

#### Missing Required Dependencies

```
✗ Dependency: click: CLI framework - NOT INSTALLED
```

**Fix:** Reinstall Lattice Lock:

```bash
pip uninstall lattice-lock
pip install lattice-lock
```

#### Git Not Found

```
✗ Git: Git not found in PATH
```

**Fix:** Install Git from [git-scm.com](https://git-scm.com/downloads)

## Step 4: Explore Available Commands

List all available Lattice Lock commands:

```bash
lattice-lock --help
```

**Expected output:**
```
Usage: lattice-lock [OPTIONS] COMMAND [ARGS]...

  Lattice Lock Framework CLI

Options:
  --version      Show the version and exit.
  -v, --verbose  Enable verbose output.
  --help         Show this message and exit.

Commands:
  doctor    Check environment health for Lattice Lock.
  gauntlet  Generate and run semantic tests from lattice.yaml.
  init      Initialize a new Lattice Lock project.
  sheriff   Validates Python files for import discipline and type hints.
  validate  Validate a Lattice Lock project.
```

## Step 5: Set Up Environment Variables (Optional)

For advanced features, you can configure environment variables:

```bash
# Create a .env file or export directly
export LOG_LEVEL=INFO
export LATTICE_LOCK_CONFIG=/path/to/lattice.yaml

# For AI features (optional)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

**Tip:** Add these to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to persist them.

## What's Next?

Now that your environment is set up, you're ready to create your first project!

**Continue to:** [Creating Your First Project](first_project.md)

## Quick Reference

| Command | Description |
|---------|-------------|
| `lattice-lock --version` | Show version |
| `lattice-lock --help` | Show help |
| `lattice-lock doctor` | Check environment health |
| `lattice-lock init` | Create new project |
| `lattice-lock validate` | Validate project |
| `lattice-lock sheriff` | Run AST validation |
| `lattice-lock gauntlet` | Run semantic tests |

## See Also

- [CLI Reference](../reference/cli/index.md) - Complete command documentation
- [Configuration Reference](../reference/configuration.md) - lattice.yaml schema
- [Development Guide](../development/development_guide.md) - Contributing to Lattice Lock
