# Configuration Guide

This guide covers all configuration options for the Lattice Lock Framework, including environment variables, the `lattice.yaml` schema file, API key setup, and database configuration.

---

## Configuration Overview

The Lattice Lock Framework uses a layered configuration approach:

1. **Environment Variables** - Runtime settings and API credentials
2. **lattice.yaml** - Schema definitions and governance rules
3. **Provider Configuration** - Cloud and local model settings
4. **Database Configuration** - Persistence layer settings

---

## Environment Variables Reference

Environment variables can be set in a `.env` file in the `credentials/` directory or exported directly in your shell.

### Core Framework Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_STRATEGY` | `balanced` | Model selection strategy: `balanced`, `cost_optimize`, `quality_first`, `speed_priority` |
| `MAX_CONCURRENT_MODELS` | `5` | Maximum number of concurrent model requests |
| `ENABLE_COST_TRACKING` | `true` | Enable/disable cost tracking for API calls |
| `DEFAULT_MODEL` | `llama3.1:8b` | Default model for routing when no specific model is selected |
| `LOG_LEVEL` | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `VERBOSE` | `false` | Enable verbose output for debugging |

### Orchestration Strategies

The `ORCHESTRATOR_STRATEGY` variable controls how the Model Orchestrator selects models:

**balanced** (default): Optimizes across all factors equally. Best for general use.

**cost_optimize**: Prioritizes local and cheaper models. Best for development and testing.

**quality_first**: Prioritizes accuracy and capability over cost. Best for production-critical tasks.

**speed_priority**: Prioritizes response time. Best for interactive applications.

Example:
```bash
export ORCHESTRATOR_STRATEGY=cost_optimize
```

---

## API Key Setup

### Cloud Provider API Keys

Configure API keys for cloud AI providers in your environment:

```bash
# OpenAI (GPT-4, GPT-4o, O1)
export OPENAI_API_KEY=sk-...

# Anthropic (Claude 4.1 Opus, Claude Sonnet)
export ANTHROPIC_API_KEY=sk-ant-...

# Google AI (Gemini 2.0)
export GOOGLE_API_KEY=...

# xAI (Grok)
export XAI_API_KEY=xai-...
```

### Enterprise Cloud Providers

```bash
# Azure OpenAI
export AZURE_OPENAI_KEY=...
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# AWS Bedrock
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

# DIAL Enterprise Gateway
export DIAL_API_KEY=...
export DIAL_ENDPOINT=https://dial.your-company.com/
```

### Development Tool Integration (Optional)

```bash
# GitHub integration
export GITHUB_TOKEN=ghp_...

# Linear integration
export LINEAR_API_KEY=lin_api_...
```

### Secure Credential Storage

For production environments, we recommend using secure credential management:

**macOS Keychain:**
```bash
# Store credential
security add-generic-password -s "OPENAI_API_KEY" -a "lattice-lock" -w "sk-..."

# Retrieve credential
security find-generic-password -s "OPENAI_API_KEY" -a "lattice-lock" -w
```

**Environment File:**
```bash
# Create credentials directory (if not exists)
mkdir -p credentials

# Create .env file
cat > credentials/.env << 'EOF'
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
EOF

# Secure the file
chmod 600 credentials/.env
```

**Important**: Never commit credentials to version control. The `credentials/` directory is excluded via `.gitignore`.

---

## Local Model Setup (Ollama)

### Ollama Configuration

```bash
# Ollama API endpoint (default)
export OLLAMA_BASE_URL=http://localhost:11434/v1

# Custom port (if running on different port)
export OLLAMA_BASE_URL=http://localhost:8080/v1

# Remote Ollama server
export OLLAMA_BASE_URL=http://your-server:11434/v1
```

### Starting Ollama

```bash
# Start Ollama service
ollama serve

# Or use the provided script
./scripts/setup/start_ollama.sh
```

### Model Warmup

Pre-load models into memory for faster response times:

```bash
# Warm up recommended models
./scripts/setup/warmup_models.sh

# Or warm up specific models
ollama run llama3.1:8b "warmup"
ollama run codellama:13b "warmup"
```

For detailed local model configuration, see [local_models_setup.md](local_models_setup.md).

---

## lattice.yaml Configuration

The `lattice.yaml` file is the schema definition file that drives code generation and governance.

### Basic Structure

```yaml
# Schema version (semantic versioning)
version: v2.1

# Output module name for generated code
generated_module: types_v2

# Configuration section
config:
  # Libraries that agents MUST NOT use
  forbidden_imports:
    - requests      # Use aiohttp instead
    - psycopg2      # Use SQLModel
    - sqlite3       # Use SQLModel
    - float         # Use Decimal for money
  
  # ORM backend selection
  orm_engine: sqlmodel

# Entity definitions
entities:
  User:
    description: "User account entity"
    persistence: table
    fields:
      id: { type: uuid, primary_key: true }
      email: { type: str, unique: true }
      age: { type: int, gt: 0 }
      status: { enum: [active, inactive, suspended], default: active }
    ensures:
      - "age >= 18"

# Interface definitions
interfaces:
  IUserService:
    file: src/services/user_service.py
    scaffold: repository_pattern
    depends_on: []
    methods:
      create_user:
        params:
          email: str
          age: int
        returns: User
        ensures:
          - "result.status == 'active'"
```

### Configuration Options

#### version
Schema version identifier using semantic versioning. Multiple versions can coexist.

```yaml
version: v2.1
```

#### generated_module
Python module name for generated artifacts. Should align with schema version.

```yaml
generated_module: types_v2
```

#### config.forbidden_imports
List of Python modules that generated code must not import. Enforced by Sheriff.

```yaml
config:
  forbidden_imports:
    - requests
    - psycopg2
    - sqlite3
```

#### config.orm_engine
ORM backend for database persistence. Currently supports `sqlmodel`.

```yaml
config:
  orm_engine: sqlmodel
```

### Entity Definition Options

| Option | Type | Description |
|--------|------|-------------|
| `description` | string | Human-readable description |
| `persistence` | `table` or `none` | Database backing |
| `fields` | object | Field definitions |
| `ensures` | list | Semantic contracts (post-conditions) |

### Field Type Options

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer | `age: { type: int }` |
| `str` | String | `name: { type: str }` |
| `bool` | Boolean | `active: { type: bool }` |
| `uuid` | UUID | `id: { type: uuid }` |
| `decimal` | Decimal (for money) | `price: { type: decimal, scale: 8 }` |
| `datetime` | DateTime | `created_at: { type: datetime }` |
| `enum` | Enumeration | `status: { enum: [a, b, c] }` |

### Field Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `primary_key` | Primary key field | `{ primary_key: true }` |
| `unique` | Unique constraint | `{ unique: true }` |
| `gt` | Greater than | `{ gt: 0 }` |
| `gte` | Greater than or equal | `{ gte: 0 }` |
| `lt` | Less than | `{ lt: 100 }` |
| `lte` | Less than or equal | `{ lte: 100 }` |
| `default` | Default value | `{ default: "pending" }` |
| `nullable` | Allow null values | `{ nullable: true }` |

---

## Database Configuration

### Connection String

Configure the database connection via the `DATABASE_URL` environment variable:

**PostgreSQL (Production):**
```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/lattice_lock
```

**SQLite (Development):**
```bash
export DATABASE_URL=sqlite:///./lattice_lock.db
```

### PostgreSQL Setup

```bash
# Create database
createdb lattice_lock

# Or via psql
psql -c "CREATE DATABASE lattice_lock;"

# Set connection string
export DATABASE_URL=postgresql://user:pass@localhost:5432/lattice_lock
```

### Running Migrations

After configuring the database, run Alembic migrations:

```bash
# Apply all migrations
alembic upgrade head

# Check current migration status
alembic current

# Generate new migration (after schema changes)
alembic revision --autogenerate -m "description"
```

---

## Configuration File Locations

| File | Location | Purpose |
|------|----------|---------|
| Environment variables | `credentials/.env` | API keys and runtime settings |
| Schema definition | `lattice.yaml` | Entity and interface definitions |
| Alembic config | `alembic.ini` | Database migration settings |
| pytest config | `pytest.ini` | Test configuration |
| Pre-commit hooks | `.pre-commit-config.yaml` | Code quality hooks |

---

## Configuration Validation

Validate your configuration before running:

```bash
# Validate lattice.yaml schema
python3 -c "import yaml; yaml.safe_load(open('lattice.yaml'))"

# Validate environment variables
./scripts/orchestrator_cli.py list

# Validate agent definitions
python3 scripts/validate_agents.py

# Test database connection
python3 -c "from sqlmodel import create_engine; import os; create_engine(os.environ['DATABASE_URL'])"
```

---

## Example Configuration

Complete example `.env` file for development:

```bash
# credentials/.env

# Orchestration
ORCHESTRATOR_STRATEGY=balanced
MAX_CONCURRENT_MODELS=5
ENABLE_COST_TRACKING=true
DEFAULT_MODEL=llama3.1:8b
LOG_LEVEL=INFO
VERBOSE=false

# Cloud Providers (add your keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Local Models
OLLAMA_BASE_URL=http://localhost:11434/v1

# Database
DATABASE_URL=sqlite:///./lattice_lock.db
```

---

## Next Steps

After configuration:

1. **Quick start**: See [quick_start.md](quick_start.md) to create your first project
2. **Local models**: See [local_models_setup.md](local_models_setup.md) for detailed Ollama setup
3. **Troubleshooting**: See [troubleshooting.md](troubleshooting.md) for common issues

---

**Configuration Guide Version**: 1.0  
**Last Updated**: 2025-12-04  
**Framework Version**: 2.1.0
