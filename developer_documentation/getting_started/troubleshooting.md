# Troubleshooting Guide

This guide covers common issues encountered when installing, configuring, and using the Lattice Lock Framework, along with their solutions.

---

## Installation Issues

### Python Version Errors

**Problem:** `Python version 3.10 or higher is required`

**Solution:**
```bash
# Check your Python version
python3 --version

# If below 3.10, install a newer version
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS (Homebrew)
brew install python@3.11

# Use the specific version
python3.11 -m venv venv
source venv/bin/activate
```

### pip Installation Failures

**Problem:** `ERROR: Could not find a version that satisfies the requirement lattice-lock`

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing again
pip install lattice-lock

# If still failing, install from source
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework
pip install -e ".[dev]"
```

### Missing System Dependencies

**Problem:** `error: command 'gcc' failed` or similar compilation errors

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# macOS
xcode-select --install

# RHEL/CentOS
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel
```

### Virtual Environment Issues

**Problem:** `ModuleNotFoundError` after installation

**Solution:**
```bash
# Ensure you're in the virtual environment
which python3
# Should show: /path/to/venv/bin/python3

# If not, activate it
source venv/bin/activate

# Reinstall dependencies
pip install -e ".[dev]"
```

---

## Configuration Problems

### Environment Variables Not Loading

**Problem:** API keys or settings not being recognized

**Solution:**
```bash
# Check if .env file exists
ls -la credentials/.env

# Verify file permissions
chmod 600 credentials/.env

# Load environment variables manually
export $(cat credentials/.env | xargs)

# Or source the file
set -a
source credentials/.env
set +a

# Verify variables are set
echo $OPENAI_API_KEY
```

### Invalid API Keys

**Problem:** `AuthenticationError` or `Invalid API key`

**Solution:**
```bash
# Verify the key format
# OpenAI: starts with sk-
# Anthropic: starts with sk-ant-
# Google: alphanumeric string

# Test the key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check for extra whitespace or newlines
cat -A credentials/.env | grep API_KEY
```

### Database Connection Errors

**Problem:** `OperationalError: could not connect to server`

**Solution:**
```bash
# For PostgreSQL
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Verify connection string format
# postgresql://user:password@host:port/database

# Test connection
psql -h localhost -U username -d lattice_lock

# For SQLite
# Ensure the directory exists and is writable
mkdir -p $(dirname $DATABASE_URL | sed 's|sqlite:///||')
```

### Ollama Connection Refused

**Problem:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
ollama serve

# Or use the provided script
./scripts/setup/start_ollama.sh

# Check if running on different port
ps aux | grep ollama

# Update OLLAMA_BASE_URL if needed
export OLLAMA_BASE_URL=http://localhost:11434/v1
```

---

## Network and Firewall Issues

### Timeout Errors

**Problem:** `TimeoutError` or `Connection timed out`

**Solution:**
```bash
# Check internet connectivity
ping api.openai.com

# Check if firewall is blocking
sudo ufw status
sudo iptables -L

# For corporate networks, check proxy settings
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Increase timeout in configuration
export REQUEST_TIMEOUT=60
```

### SSL Certificate Errors

**Problem:** `SSLCertVerificationError` or `certificate verify failed`

**Solution:**
```bash
# Update certificates
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates

# macOS
brew install ca-certificates

# If using corporate proxy with custom CA
export REQUESTS_CA_BUNDLE=/path/to/corporate-ca.crt

# As last resort (not recommended for production)
export CURL_CA_BUNDLE=""
```

### Rate Limiting

**Problem:** `RateLimitError` or `429 Too Many Requests`

**Solution:**
```bash
# Switch to cost_optimize strategy (uses local models)
export ORCHESTRATOR_STRATEGY=cost_optimize

# Reduce concurrent requests
export MAX_CONCURRENT_MODELS=2

# Wait and retry
sleep 60

# Use local models exclusively
./scripts/orchestrator_cli.py route "your prompt" --local-only
```

---

## Permission Problems

### Script Execution Errors

**Problem:** `Permission denied` when running scripts

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.py
chmod +x scripts/setup/*.sh

# If still failing, run with Python directly
python3 scripts/orchestrator_cli.py list
```

### File Write Errors

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Check directory permissions
ls -la

# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod -R u+rw .

# For credentials directory
chmod 700 credentials
chmod 600 credentials/.env
```

### Git Hook Failures

**Problem:** Pre-commit hooks failing with permission errors

**Solution:**
```bash
# Reinstall pre-commit hooks
pre-commit uninstall
pre-commit install

# Make hooks executable
chmod +x .git/hooks/*

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "message"
```

---

## Model Orchestrator Issues

### No Models Available

**Problem:** `No models available for routing`

**Solution:**
```bash
# Check if any API keys are configured
env | grep -E "(OPENAI|ANTHROPIC|GOOGLE|XAI)_API_KEY"

# Check if Ollama is running for local models
curl http://localhost:11434/api/version

# List available models
./scripts/orchestrator_cli.py list

# Pull a local model
ollama pull llama3.1:8b
```

### Model Selection Errors

**Problem:** `Model not found` or `Invalid model ID`

**Solution:**
```bash
# List available models
./scripts/orchestrator_cli.py list --verbose

# Check model name spelling
# Local models: llama3.1:8b, codellama:13b
# Cloud models: gpt-4o, claude-sonnet-4.5

# Use analyze to see recommended models
./scripts/orchestrator_cli.py analyze "your task"
```

### Out of Memory Errors

**Problem:** `OutOfMemoryError` when using local models

**Solution:**
```bash
# Check current memory usage
free -h

# Use smaller models
ollama pull llama3.2:3b  # Instead of 70b models

# Stop other models
ollama stop llama3.1:70b

# Restart Ollama to clear memory
pkill ollama
ollama serve
```

---

## Schema and Validation Issues

### Schema Compilation Errors

**Problem:** `Invalid schema` or `YAML parsing error`

**Solution:**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('lattice.yaml'))"

# Check for common issues:
# - Incorrect indentation (use spaces, not tabs)
# - Missing colons after keys
# - Unquoted special characters

# Use a YAML linter
pip install yamllint
yamllint lattice.yaml
```

### Sheriff Validation Failures

**Problem:** `Sheriff: FAILED - Import discipline violation`

**Solution:**
```bash
# Check which imports are forbidden
grep -A 10 "forbidden_imports" lattice.yaml

# Find the violating import
python3 sheriff.py your_file.py --verbose

# Replace forbidden imports:
# requests → aiohttp
# sqlite3 → sqlmodel
# psycopg2 → sqlmodel
```

### Gauntlet Test Failures

**Problem:** `pytest contracts failing`

**Solution:**
```bash
# Run tests with verbose output
pytest tests/contracts/ -v

# Check specific failure
pytest tests/contracts/test_entity_contracts.py -v --tb=long

# Verify ensures clauses in lattice.yaml match implementation
grep -A 5 "ensures:" lattice.yaml
```

---

## Frequently Asked Questions

### General Questions

**Q: Do I need all the API keys configured?**

A: No. You can use the framework with just local models (Ollama) or with a single cloud provider. The orchestrator will use whatever models are available.

**Q: How much does it cost to use cloud models?**

A: Costs vary by provider and model. Use `cost_optimize` strategy to minimize costs. Local models via Ollama are completely free.

**Q: Can I use this offline?**

A: Yes, with local models via Ollama. Install models while online, then use offline with `--local-only` flag.

### Installation Questions

**Q: Which Python version should I use?**

A: Python 3.10, 3.11, or 3.12 are all supported. We recommend 3.11 for the best balance of features and stability.

**Q: Do I need Docker?**

A: No, Docker is optional. You can install directly via pip or from source.

**Q: How much disk space do I need?**

A: The framework itself needs about 2GB. Local models require 2-50GB each depending on size.

### Configuration Questions

**Q: Where should I put my API keys?**

A: In `credentials/.env`. Never commit this file to version control.

**Q: How do I switch between strategies?**

A: Set `ORCHESTRATOR_STRATEGY` environment variable or use `--strategy` flag with CLI commands.

**Q: Can I use a remote Ollama server?**

A: Yes, set `OLLAMA_BASE_URL` to your remote server's address.

### Usage Questions

**Q: How do I know which model was used?**

A: The CLI output shows the selected model. Use `--verbose` for detailed scoring information.

**Q: Can I force a specific model?**

A: Yes, use `--model` flag: `./scripts/orchestrator_cli.py route "prompt" --model gpt-4o`

**Q: How do I reduce costs?**

A: Use `cost_optimize` strategy, install local models, and use smaller models for simple tasks.

---

## Getting Help

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
export VERBOSE=true
./scripts/orchestrator_cli.py list
```

### Log Files

Check logs for detailed error information:

```bash
# Application logs
cat logs/lattice-lock.log

# Ollama logs
journalctl -u ollama -f
```

### Reporting Issues

When reporting issues, include:

1. Python version: `python3 --version`
2. Framework version: `cat version.txt`
3. Operating system: `uname -a`
4. Error message (full traceback)
5. Steps to reproduce

Report issues at: [GitHub Issues](https://github.com/klappe-pm/lattice-lock-framework/issues)

---

## Quick Fixes Checklist

When something isn't working, try these steps in order:

1. **Activate virtual environment**: `source venv/bin/activate`
2. **Check Python version**: `python3 --version` (need 3.10+)
3. **Reinstall dependencies**: `pip install -e ".[dev]"`
4. **Check environment variables**: `env | grep -E "(API_KEY|OLLAMA|DATABASE)"`
5. **Start Ollama**: `ollama serve`
6. **Validate configuration**: `./scripts/orchestrator_cli.py list`
7. **Check logs**: `export LOG_LEVEL=DEBUG`

---

**Troubleshooting Guide Version**: 1.0  
**Last Updated**: 2025-12-04  
**Framework Version**: 2.1.0
