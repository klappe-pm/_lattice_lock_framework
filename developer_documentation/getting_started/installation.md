# Installation Guide

This guide covers all methods for installing the Lattice Lock Framework, from quick pip installation to building from source.

---

## System Requirements

### Minimum Requirements

The Lattice Lock Framework requires Python 3.10 or higher. The framework has been tested on Python 3.10, 3.11, and 3.12.

**Operating System Support:**
- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- macOS (12.0 Monterey or later)
- Windows 10/11 (with WSL2 recommended for local models)

**Hardware Requirements:**
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB+ recommended for local models
- Storage: 2GB for framework, 50-150GB additional for local models

### Python Version Check

```bash
python3 --version
# Should output: Python 3.10.x or higher
```

If you need to install or upgrade Python, visit [python.org](https://www.python.org/downloads/) or use your system's package manager.

---

## Installation Methods

### Option 1: Install via pip (Recommended)

The simplest way to install Lattice Lock is via pip:

```bash
pip install lattice-lock
```

To install with development dependencies:

```bash
pip install lattice-lock[dev]
```

To install with all optional dependencies:

```bash
pip install lattice-lock[all]
```

### Option 2: Install from Source

For the latest development version or to contribute to the project:

```bash
# Clone the repository
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Option 3: Docker Installation

For containerized deployments:

```bash
# Pull the official image
docker pull lattice-lock/lattice-lock-framework:latest

# Run with mounted configuration
docker run -v $(pwd)/config:/app/config \
           -v $(pwd)/credentials:/app/credentials \
           lattice-lock/lattice-lock-framework:latest
```

**Building from Dockerfile:**

```bash
# Clone the repository
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework

# Build the image
docker build -t lattice-lock-framework .

# Run the container
docker run -it lattice-lock-framework
```

---

## Dependencies

The framework has the following core dependencies (automatically installed):

| Package | Version | Purpose |
|---------|---------|---------|
| requests | >=2.31.0 | HTTP client for API calls |
| aiohttp | >=3.9.0 | Async HTTP client |
| pyyaml | >=6.0 | YAML configuration parsing |
| numpy | >=1.24.0 | Numerical operations |
| rich | >=13.0.0 | Terminal formatting |
| tenacity | >=8.2.0 | Retry logic |
| Jinja2 | >=3.1.0 | Template rendering |

**Development Dependencies** (installed with `[dev]`):
- pytest >=7.4.0
- pytest-asyncio >=0.21.0
- httpx >=0.25.0

**Optional Dependencies** (installed with `[all]`):
- uvloop >=0.19.0 (Linux/macOS only, for improved async performance)

---

## Verification Steps

After installation, verify everything is working correctly:

### 1. Check Package Installation

```bash
# Verify the package is installed
pip show lattice-lock

# Check the version
python3 -c "import lattice_lock_orchestrator; print('Installation successful')"
```

### 2. Verify CLI Access

```bash
# Check if the CLI is available
lattice-lock --help
```

### 3. Test the Model Orchestrator

```bash
# Navigate to the project directory (if installed from source)
cd lattice-lock-framework

# List available models (requires API keys for cloud models)
./scripts/orchestrator_cli.py list

# Run a basic analysis
./scripts/orchestrator_cli.py analyze "Hello, world"
```

### 4. Validate Agent Definitions

```bash
# Validate all agent definitions
python3 scripts/validate_agents.py
```

---

## Local Models Setup (Optional)

For zero-cost, privacy-preserving AI inference, install Ollama for local model support:

### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS (Homebrew):**
```bash
brew install ollama
```

**Windows:**
Download from [ollama.com/download](https://ollama.com/download)

### Start Ollama Service

```bash
# Start the Ollama service
ollama serve

# Or use the provided script
./scripts/setup/start_ollama.sh
```

### Pull Recommended Models

```bash
# Lightweight model (8GB RAM)
ollama pull llama3.1:8b

# Balanced code model (16GB RAM)
ollama pull codellama:13b

# High-quality reasoning (32GB+ RAM)
ollama pull deepseek-r1:70b
```

For detailed local model setup, see [local_models_setup.md](local_models_setup.md).

---

## Upgrading

### Upgrade via pip

```bash
pip install --upgrade lattice-lock
```

### Upgrade from Source

```bash
cd lattice-lock-framework
git pull origin main
pip install -e ".[dev]"
```

---

## Uninstallation

### Remove via pip

```bash
pip uninstall lattice-lock
```

### Remove from Source Installation

```bash
# Deactivate virtual environment
deactivate

# Remove the directory
rm -rf lattice-lock-framework
```

### Remove Docker Images

```bash
docker rmi lattice-lock/lattice-lock-framework:latest
```

---

## Next Steps

After successful installation:

1. **Configure the framework**: See [configuration.md](configuration.md) for environment setup
2. **Quick start guide**: See [quick_start.md](quick_start.md) for your first project
3. **Troubleshooting**: See [troubleshooting.md](troubleshooting.md) if you encounter issues

---

## Platform-Specific Notes

### Linux

On Ubuntu/Debian, you may need to install Python development headers:

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
```

### macOS

Ensure you have the Xcode command line tools installed:

```bash
xcode-select --install
```

### Windows

For the best experience on Windows, we recommend using WSL2 (Windows Subsystem for Linux):

1. Install WSL2 following [Microsoft's guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Install Ubuntu from the Microsoft Store
3. Follow the Linux installation instructions within WSL2

Native Windows installation is supported but local model performance may be reduced.

---

**Installation Guide Version**: 1.0  
**Last Updated**: 2025-12-04  
**Framework Version**: 2.1.0
