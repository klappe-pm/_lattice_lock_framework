# Installation Guide

This guide covers the installation process for the Lattice Lock Framework on supported platforms.

## System Requirements

Before installing, ensure your system meets the following requirements:

- **Operating System**: macOS 12+, Linux (Ubuntu 20.04+, Fedora 34+), or Windows 10/11 via WSL2.
- **Python**: Version 3.10 or higher.
- **Memory**: Minimum 4GB RAM (8GB+ recommended for local model execution).
- **Disk Space**: 2GB free space (more required for local models).

## Installation Methods

### Option 1: Install via Pip (Recommended)

The easiest way to install Lattice Lock is using `pip`:

```bash
pip install lattice-lock
```

We recommend installing in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install lattice-lock
```

### Option 2: Install from Source

For developers who want the latest changes or want to contribute:

```bash
git clone https://github.com/lattice-lock/lattice-lock-framework.git
cd lattice-lock-framework
pip install -e .
```

### Option 3: Docker Installation

You can run Lattice Lock in a Docker container without installing Python dependencies locally.

1.  **Pull the image:**

    ```bash
    docker pull latticelock/framework:latest
    ```

2.  **Run the container:**

    ```bash
    docker run -it -v $(pwd):/app latticelock/framework:latest lattice-lock --help
    ```

## Verification

To verify that the installation was successful, run the following command:

```bash
lattice-lock --version
```

You should see output similar to:

```text
Lattice Lock Framework v2.1.0
```

To run a system health check:

```bash
lattice-lock doctor
```

This will verify your Python version, dependencies, environment variables, and optional tools like Ollama.

## Next Steps

Once installed, proceed to [Configuration](docs/getting_started/configuration.md) to set up your environment and API keys.
