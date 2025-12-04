# Quick Start Guide

Get up and running with the Lattice Lock Framework in 5 minutes. This guide walks you through creating your first project, running your first validation, and understanding the expected output.

---

## Prerequisites

Before starting, ensure you have:

- Python 3.10+ installed ([installation guide](installation.md))
- Git installed
- Basic familiarity with command line

**Optional but recommended:**
- Ollama installed for local models (zero cost)
- At least one cloud API key (OpenAI, Anthropic, or Google)

---

## 5-Minute Quick Start

### Step 1: Clone and Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/klappe-pm/lattice-lock-framework.git
cd lattice-lock-framework

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 2: Configure Credentials (1 minute)

```bash
# Create credentials directory
mkdir -p credentials

# Create minimal configuration
cat > credentials/.env << 'EOF'
ORCHESTRATOR_STRATEGY=balanced
LOG_LEVEL=INFO
OLLAMA_BASE_URL=http://localhost:11434/v1
EOF
```

For cloud models, add your API keys:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> credentials/.env
```

### Step 3: Verify Installation (30 seconds)

```bash
# Check the orchestrator is working
./scripts/orchestrator_cli.py list

# Expected output: List of available models
```

### Step 4: Run Your First Task (1 minute)

```bash
# Analyze a simple prompt
./scripts/orchestrator_cli.py analyze "Write a Python function to calculate factorial"
```

**Expected Output:**
```
Task Analysis:
  Type: CODE_GENERATION
  Complexity: Low
  Recommended Models:
    1. codellama:13b (local, free)
    2. gpt-4o-mini (cloud, $0.001)
    3. claude-sonnet-4.5 (cloud, $0.003)
```

### Step 5: Route a Request (1.5 minutes)

```bash
# Route a request to the optimal model
./scripts/orchestrator_cli.py route "Write a Python function to calculate factorial" --strategy cost_optimize
```

**Expected Output:**
```
Routing to: codellama:13b (local)
Strategy: cost_optimize

Response:
def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

---

## Create Your First Project

### Define a Schema

Create a `lattice.yaml` file in your project root:

```yaml
version: v2.1
generated_module: types_v2

config:
  forbidden_imports:
    - requests
    - sqlite3
  orm_engine: sqlmodel

entities:
  Task:
    description: "A task item for tracking work"
    persistence: table
    fields:
      id: { type: uuid, primary_key: true }
      title: { type: str }
      description: { type: str, nullable: true }
      completed: { type: bool, default: false }
      priority: { enum: [low, medium, high], default: medium }
      created_at: { type: datetime }
    ensures:
      - "len(title) > 0"
```

### Compile the Schema

```bash
# Compile lattice.yaml into governance artifacts
python3 compile_lattice.py
```

**Generated Files:**
- `types_v2/models.py` - Pydantic models for validation
- `types_v2/orm.py` - SQLModel ORM for database
- `tests/contracts/test_task_contracts.py` - pytest semantic contracts

### Validate Generated Code

```bash
# Run Sheriff (AST validation)
python3 sheriff.py types_v2/models.py

# Run The Gauntlet (semantic tests)
pytest tests/contracts/
```

**Expected Output:**
```
Sheriff: PASSED
  - Import discipline: OK
  - Type hints: OK
  - Forbidden imports: OK

pytest: 3 passed in 0.42s
```

---

## Using the Model Orchestrator

### List Available Models

```bash
./scripts/orchestrator_cli.py list --verbose
```

Shows all 63 models across 8 providers with their capabilities and costs.

### Analyze a Task

```bash
./scripts/orchestrator_cli.py analyze "Review this code for security vulnerabilities"
```

The analyzer detects task type (CODE_REVIEW) and recommends optimal models.

### Route with Different Strategies

```bash
# Cost-optimized (prefers local models)
./scripts/orchestrator_cli.py route "Explain decorators" --strategy cost_optimize

# Quality-first (prefers premium models)
./scripts/orchestrator_cli.py route "Review critical security code" --strategy quality_first

# Speed-priority (prefers fast models)
./scripts/orchestrator_cli.py route "Quick syntax check" --strategy speed_priority
```

### Multi-Model Consensus

For critical decisions, use consensus voting:

```bash
./scripts/orchestrator_cli.py consensus "Is this implementation thread-safe?" --num 5
```

Five models independently evaluate and vote on the answer.

---

## Expected Output Examples

### Successful Schema Compilation

```
$ python3 compile_lattice.py

Compiling lattice.yaml (v2.1)...
  Generating Pydantic models: types_v2/models.py
  Generating SQLModel ORM: types_v2/orm.py
  Generating Alembic migration: alembic/versions/001_create_task.py
  Generating pytest contracts: tests/contracts/test_task_contracts.py

Compilation complete. Generated 4 artifacts.
```

### Successful Validation

```
$ python3 sheriff.py src/services/task_service.py

Sheriff AST Validation
======================
File: src/services/task_service.py

Checks:
  [PASS] Import discipline - all imports from approved modules
  [PASS] Type hints - all functions have return type hints
  [PASS] Forbidden imports - no forbidden modules used
  [PASS] Version compliance - using current lattice version

Result: PASSED
```

### Model Routing Output

```
$ ./scripts/orchestrator_cli.py route "Implement a REST endpoint" --strategy balanced

Model Selection
===============
Task Type: CODE_GENERATION
Strategy: balanced
Selected Model: claude-sonnet-4.5

Scoring:
  Task Affinity: 0.92 (weight: 40%)
  Performance: 0.88 (weight: 30%)
  Accuracy: 0.95 (weight: 20%)
  Cost Efficiency: 0.75 (weight: 10%)
  Final Score: 0.89

Response:
[Generated code here...]
```

---

## Common First-Time Issues

### "No models available"

Ensure Ollama is running or cloud API keys are configured:

```bash
# Start Ollama
ollama serve

# Or add cloud API key
echo "OPENAI_API_KEY=sk-..." >> credentials/.env
```

### "Module not found" errors

Ensure you're in the virtual environment:

```bash
source venv/bin/activate
pip install -e ".[dev]"
```

### "Permission denied" on scripts

Make scripts executable:

```bash
chmod +x scripts/*.py scripts/setup/*.sh
```

For more issues, see [troubleshooting.md](troubleshooting.md).

---

## Next Steps

Now that you have the basics working:

1. **Deep dive into configuration**: [configuration.md](configuration.md)
2. **Set up local models**: [local_models_setup.md](local_models_setup.md)
3. **Learn about agents**: [../architecture/model_orchestrator_architecture.md](../architecture/model_orchestrator_architecture.md)
4. **Explore tutorials**: [tutorial_1__basic_model_selection.md](tutorial_1__basic_model_selection.md)

---

## Quick Reference

### Essential Commands

```bash
# List models
./scripts/orchestrator_cli.py list

# Analyze task
./scripts/orchestrator_cli.py analyze "your prompt"

# Route request
./scripts/orchestrator_cli.py route "your prompt" --strategy balanced

# Compile schema
python3 compile_lattice.py

# Validate code
python3 sheriff.py <file>

# Run tests
pytest tests/
```

### Orchestration Strategies

| Strategy | Best For | Cost |
|----------|----------|------|
| `cost_optimize` | Development, testing | Lowest |
| `balanced` | General use | Medium |
| `quality_first` | Production, critical code | Higher |
| `speed_priority` | Interactive apps | Variable |

### Task Types

The orchestrator automatically detects these task types:

- `CODE_GENERATION` - Writing new code
- `CODE_REVIEW` - Reviewing existing code
- `DEBUGGING` - Finding and fixing bugs
- `REASONING` - Complex analysis
- `VISION` - Image analysis
- `QUICK_RESPONSE` - Simple queries

---

**Quick Start Guide Version**: 1.0  
**Last Updated**: 2025-12-04  
**Time to Complete**: 5 minutes
