#!/usr/bin/env python3
"""
Lattice Lock Framework - Agent Prompts Library

This module contains prompts for different AI tools (Claude Code, Gemini Antimatter,
Gemini CLI) organized by task ID. These prompts are designed to be copy-pasted into
the respective tools.

Usage:
    from agent_prompts import get_prompt, list_tasks

    # Get a specific prompt
    prompt = get_prompt("claude_code", "2.2.1")
    print(prompt)

    # List all available tasks for a tool
    tasks = list_tasks("gemini_cli")
"""


# Claude Code prompts - for IDE-based code generation
CLAUDE_CODE_PROMPTS = {
    "2.2.1": """You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 2.2.1 - Design and draft AWS CodePipeline templates

Context:
- Repository: lattice-lock-framework (governance-first AI framework)
- Key directories: `src/lattice_lock_cli/templates/`, `scripts/`, `tests/`
- Python 3.10+, uses pytest for testing
- Package version managed via `version.txt` (currently 2.1.0)

Goals:
1. Draft `buildspec.yml.j2` for AWS CodeBuild with these phases:
   - Install: Python 3.10+, pip dependencies from pyproject.toml
   - Pre-build: Run `lattice-lock validate`
   - Build: Run `lattice-lock sheriff` and `lattice-lock gauntlet`
   - Post-build: Run pytest with coverage
   - Artifacts: test results, coverage reports

2. Draft `pipeline.yml.j2` CloudFormation template:
   - Source stage: GitHub connection (parameterized)
   - Build stage: CodeBuild project reference
   - Optional deploy stage placeholder

3. Draft `codebuild-project.yml.j2`:
   - Python 3.10 runtime environment
   - Service role with least-privilege IAM
   - Pip cache configuration

Constraints:
- Use Jinja2 templating for variable substitution
- No hardcoded secrets or account IDs (use placeholders)
- Follow AWS CloudFormation best practices
- Templates must be valid YAML

Output:
- Code blocks for each file with clear filenames and paths
- Brief explanation of pipeline stages
- List of required IAM permissions""",
    "2.3.1": """You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 2.3.1 - Design and draft GCP Cloud Build templates

Context:
- Repository: lattice-lock-framework
- Key directories: `src/lattice_lock_cli/templates/`, `scripts/`, `tests/`
- Python 3.10+, uses pytest for testing

Goals:
1. Draft `cloudbuild.yaml.j2` with these steps:
   - Install Python dependencies
   - Run `lattice-lock validate`
   - Run `lattice-lock sheriff`
   - Run `lattice-lock gauntlet`
   - Run pytest with coverage
   - Store artifacts in Cloud Storage

2. Draft `trigger.yaml.j2` for Cloud Build triggers:
   - GitHub repository connection
   - Branch filter configuration
   - Substitution variables

Constraints:
- Use Jinja2 templating for variable substitution
- No hardcoded secrets (use Secret Manager references)
- Follow GCP Cloud Build best practices
- Templates must be valid YAML

Output:
- Code blocks for each file with clear filenames and paths
- Brief explanation of build steps
- List of required IAM permissions""",
    "3.1.1": '''You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 3.1.1 - Implement Error Classification System

Context:
- Repository: lattice-lock-framework
- Create new module: `src/lattice_lock/errors/`
- Python 3.10+, use dataclasses and enums

Goals:
1. Create `src/lattice_lock/errors/__init__.py`:
   - Export all error types and utilities

2. Create `src/lattice_lock/errors/types.py`:
   ```python
   class LatticeError(Exception):
       """Base exception for all Lattice Lock errors."""
       error_code: str
       severity: Severity
       category: Category

   class SchemaValidationError(LatticeError): ...
   class SheriffViolationError(LatticeError): ...
   class GauntletFailureError(LatticeError): ...
   class ConfigurationError(LatticeError): ...
   class OrchestratorError(LatticeError): ...
   ```

3. Create `src/lattice_lock/errors/classification.py`:
   ```python
   class Severity(Enum):
       CRITICAL = "critical"
       HIGH = "high"
       MEDIUM = "medium"
       LOW = "low"

   class Category(Enum):
       VALIDATION = "validation"
       RUNTIME = "runtime"
       CONFIGURATION = "configuration"
       NETWORK = "network"

   class Recoverability(Enum):
       RECOVERABLE = "recoverable"
       MANUAL_INTERVENTION = "manual_intervention"
       FATAL = "fatal"
   ```

4. Create `src/lattice_lock/errors/remediation.py`:
   - Map error types to remediation steps
   - Include documentation URLs
   - Generate actionable messages

Constraints:
- Follow Python exception best practices
- Include error codes for machine parsing (e.g., "LL-VAL-001")
- All errors must be serializable to JSON

Output:
- Complete code for all files
- Example usage snippets''',
    "3.1.2": '''You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 3.1.2 - Implement Error Handling Middleware

Context:
- Repository: lattice-lock-framework
- Depends on: 3.1.1 Error Classification System
- Integrate with: `src/lattice_lock_orchestrator/`

Goals:
1. Create `src/lattice_lock/errors/middleware.py`:
   ```python
   class ErrorMiddleware:
       def __init__(self, logger=None, telemetry=None):
           ...

       def catch_and_classify(self, func):
           """Decorator to catch and classify errors."""
           ...

       def handle_error(self, error: Exception) -> ErrorContext:
           """Classify error and generate context."""
           ...

       def log_error(self, context: ErrorContext):
           """Log error with appropriate level."""
           ...
   ```

2. Create `src/lattice_lock/errors/context.py`:
   ```python
   @dataclass
   class ErrorContext:
       error_type: str
       error_code: str
       severity: Severity
       category: Category
       recoverability: Recoverability
       message: str
       remediation: list[str]
       documentation_url: str | None
       timestamp: datetime
       stack_trace: str | None
   ```

3. Integrate with ModelOrchestrator:
   - Wrap API calls with error middleware
   - Add telemetry hooks for error tracking

Constraints:
- Must not break existing functionality
- Errors must be logged before re-raising
- Support async and sync functions

Output:
- Complete code for middleware
- Integration example with orchestrator''',
    "4.3.1": """You are Claude Code running inside an IDE.

Task ID: 4.3.1 - Pilot Project 1 Scaffolding (API Service)

Context:
- Create a pilot project to validate the Lattice Lock Framework
- Use the lattice-lock CLI to scaffold the project

Goals:
1. Pilot Project 1 - Simple API Service:
   - FastAPI backend with 3-5 endpoints
   - SQLModel for database
   - Full Lattice Lock integration

Generate:
- Project structure
- lattice.yaml schema definition
- Basic implementation code
- Test suite skeleton
- CI/CD configuration

Output:
- Directory structure
- Key file contents
- Setup instructions""",
    "4.3.2": """You are Claude Code running inside an IDE.

Task ID: 4.3.2 - Pilot Project 2 Scaffolding (CLI Tool)

Context:
- Create a second pilot project with different use case
- Validate framework flexibility

Goals:
1. Pilot Project 2 - CLI Tool:
   - Click-based CLI application
   - Multiple commands
   - Configuration management

Generate:
- Project structure
- lattice.yaml schema definition
- Basic implementation code
- Test suite skeleton
- CI/CD configuration

Output:
- Directory structure
- Key file contents
- Setup instructions""",
    "5.1.1": """You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 5.1.1 - Prompt Architect Agent Core Implementation

Context:
- Repository: lattice-lock-framework
- Agent definitions in: `docs/agent_definitions/`
- Memory protocol in: `docs/agent_memory/universal_memory_directive.md`

Goals:
1. Create `docs/agent_definitions/prompt_architect_agent/`:
   ```
   prompt_architect_agent/
   ├── agent_prompt_architect.md
   ├── capabilities.md
   ├── workflows/
   │   ├── generate_prompt.md
   │   └── update_prompt.md
   └── examples/
   ```

2. Implement agent capabilities:
   - Parse specification documents
   - Generate prompts from specs
   - Validate prompts against v2.1 format
   - Update existing prompts

3. Create memory file:
   `docs/agent_memory/agents/agent_prompt_architect_memory.md`

Output:
- Complete agent definition files
- Memory file template""",
    "5.1.2": """You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 5.1.2 - Prompt Architect Agent Integration

Context:
- Depends on: 5.1.1 Prompt Architect Core
- Integrate with: prompt_tracker.py

Goals:
1. Integration with Project Agent
2. Connect to prompt_tracker.py
3. Implement prompt generation workflow
4. Write integration tests

Output:
- Integration code snippets
- Test file skeleton""",
}

# Gemini Antimatter prompts - for design docs and specifications
GEMINI_ANTIMATTER_PROMPTS = {
    "2.2.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 2.2.1 - Design Document for AWS CodePipeline Integration

Write a design document in markdown with these sections:

1. **Background**
   - Why AWS CodePipeline integration is needed
   - Current CI/CD state (GitHub Actions exists)
   - Target users (teams on AWS infrastructure)

2. **Requirements**
   - Functional: validation, Sheriff, Gauntlet checks
   - Non-functional: <5 min build time, cost optimization
   - Security: no secrets in code, least-privilege IAM

3. **Proposed Pipeline Architecture**
   - Diagram description (Source -> Build -> Test -> Deploy)
   - Stage responsibilities
   - Artifact flow

4. **Stages & Jobs**
   - Source stage: trigger configuration
   - Build stage: CodeBuild project details
   - Test stage: pytest integration
   - Deploy stage: optional, placeholder

5. **Security & Secrets**
   - IAM role requirements
   - Secrets Manager integration
   - Cross-account considerations

6. **Open Questions**
   - Multi-region support?
   - Cost allocation tags?
   - Notification integration?

7. **Implementation Tasks**
   List concrete tasks for Devin AI and Claude Code to implement.

Context:
- Framework has 63 AI models from 8 providers
- Uses pytest for testing, rich for CLI output
- Existing templates in `src/lattice_lock_cli/templates/`""",
    "2.3.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 2.3.1 - Design Document for GCP Cloud Build Integration

Write a design document in markdown with these sections:

1. **Background**
   - Why GCP Cloud Build integration is needed
   - Comparison with AWS CodePipeline approach
   - Target users (teams on GCP infrastructure)

2. **Requirements**
   - Functional: validation, Sheriff, Gauntlet checks
   - Non-functional: <5 min build time, cost optimization
   - Security: Secret Manager integration

3. **Proposed Build Architecture**
   - Build steps sequence
   - Artifact storage strategy
   - Caching approach

4. **Build Steps**
   - Step 1: Dependency installation
   - Step 2: Validation
   - Step 3: Sheriff checks
   - Step 4: Gauntlet tests
   - Step 5: pytest execution

5. **Security & Secrets**
   - Service account requirements
   - Secret Manager integration
   - Workload identity considerations

6. **Open Questions**
   - Multi-project support?
   - Build caching strategy?
   - Artifact Registry integration?

7. **Implementation Tasks**
   List concrete tasks for Devin AI and Claude Code to implement.""",
    "3.1.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 3.1.1 - Design Document for Error Classification System

Write a design document in markdown with these sections:

1. **Background**
   - Current error handling state
   - Problems with unstructured errors
   - Goals for the new system

2. **Error Taxonomy**
   - Error categories and their meanings
   - Severity levels and when to use each
   - Recoverability classification

3. **Error Code Scheme**
   - Format: LL-{CATEGORY}-{NUMBER}
   - Category codes: VAL, SHF, GAU, CFG, ORC, NET
   - Number ranges per category

4. **Remediation Strategy**
   - How remediation steps are determined
   - Documentation link generation
   - User-facing vs developer-facing messages

5. **Integration Points**
   - CLI error display
   - API error responses
   - Logging and telemetry

6. **Error Catalog**
   Table of all error codes with:
   - Code, Name, Severity, Category, Recoverability, Remediation

7. **Implementation Tasks**
   List concrete tasks for Devin AI to implement.""",
    "3.1.2": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 3.1.2 - Design Document for Error Handling Middleware

Write a design document covering:

1. **Middleware Architecture**
   - Request/response flow with error handling
   - Decorator pattern for wrapping functions
   - Context propagation

2. **Error Flow**
   - Exception caught -> Classification -> Logging -> Telemetry -> Re-raise/Handle
   - Decision tree for error handling strategies

3. **Telemetry Integration**
   - What metrics to capture
   - Error rate tracking
   - Latency impact measurement

4. **Logging Strategy**
   - Log levels per severity
   - Structured logging format
   - Sensitive data redaction

5. **Recovery Strategies**
   - Retry logic for recoverable errors
   - Circuit breaker pattern
   - Graceful degradation

6. **Implementation Tasks**
   List concrete tasks for Devin AI.""",
    "4.3.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 4.3.1 - Pilot Project 1 Design Document (API Service)

Write a design document for the first pilot project:

1. **Project Goals**
   - Validate Lattice Lock Framework integration
   - Test scaffolding workflow
   - Measure onboarding time

2. **Technical Requirements**
   - FastAPI backend
   - SQLModel for database
   - 3-5 REST endpoints
   - Full test coverage

3. **Schema Design**
   - Entities and relationships
   - Field constraints
   - Semantic contracts

4. **API Endpoints**
   - CRUD operations
   - Authentication (optional)
   - Error responses

5. **Success Metrics**
   - Scaffolding time < 5 minutes
   - All validation passes
   - CI/CD works on first try

6. **Onboarding Checklist**
   Step-by-step guide for new users""",
    "4.3.2": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 4.3.2 - Pilot Project 2 Design Document (CLI Tool)

Write a design document for the second pilot project:

1. **Project Goals**
   - Validate framework flexibility
   - Test different project type
   - Collect user feedback

2. **Technical Requirements**
   - Click-based CLI
   - Multiple commands
   - Configuration management
   - Full test coverage

3. **Command Structure**
   - Main commands
   - Subcommands
   - Options and arguments

4. **Configuration Schema**
   - Config file format
   - Environment variables
   - Default values

5. **Success Metrics**
   - Different use case validated
   - Framework adapts well
   - User satisfaction > 4/5

6. **Feedback Collection**
   - What to measure
   - How to collect
   - Analysis approach""",
    "5.1.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 5.1.1 - Prompt Architect Agent Specification

Write a comprehensive specification:

1. **Agent Purpose**
   - Role in the multi-agent system
   - Relationship to other agents
   - Value proposition

2. **Capabilities**
   - Specification parsing
   - Prompt generation
   - Prompt validation
   - Prompt updating

3. **Inputs & Outputs**
   - Input: Specification documents, roadmap items
   - Output: Formatted prompts, validation reports

4. **Workflows**
   - Generate new prompt workflow
   - Update existing prompt workflow
   - Batch generation workflow

5. **Memory Structure**
   - What to track
   - Update frequency
   - Interaction logging

6. **Integration Points**
   - Project Agent
   - prompt_tracker.py
   - Work breakdown structure

7. **Success Criteria**
   - Generated prompts pass validation
   - 90%+ accuracy on spec interpretation
   - <30 second generation time""",
    "5.1.2": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 5.1.2 - Prompt Architect Integration Specification

Write a specification for integrating the Prompt Architect Agent:

1. **Integration Architecture**
   - How it connects to Project Agent
   - Data flow between agents
   - Event triggers

2. **Tracker Integration**
   - How to read from prompt_tracker.py
   - How to update tracker state
   - Conflict resolution

3. **Prompt Generation Workflow**
   - Input: task specification
   - Processing: template selection, variable substitution
   - Output: formatted prompt file

4. **Testing Strategy**
   - Unit tests for generation
   - Integration tests with tracker
   - End-to-end workflow tests

5. **Error Handling**
   - Invalid specifications
   - Missing templates
   - Tracker conflicts""",
    "6.1.1": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 6.1.1 - Orchestrator Capabilities Contract Design

Write a design document in markdown with these sections:

1. **Contract Definition**
   - Which fields MUST exist on `ModelCapabilities` for CLI output and routing?
   - Define the complete field list with types
   - Specify which fields are required vs optional with defaults

2. **Field Semantics**
   - Should we use explicit booleans (`supports_reasoning`, `code_specialized`) or derive from numeric scores?
   - How should `task_scores` be represented? Options:
     - Explicit `dict[TaskType, float]` on each model
     - Derived at runtime from scoring functions
     - Hybrid approach
   - Recommendation with rationale

3. **TaskType Enum Updates**
   - Should `VISION` be added to the enum?
   - If yes: define semantics and which models support it
   - If no: how to handle/remove existing references?
   - Any other missing task types?

4. **Migration Strategy**
   - Safe defaults for new fields (backwards compatibility)
   - How existing model definitions should be updated
   - Validation to ensure all models have required fields

5. **Implementation Tasks**
   List concrete tasks for Devin AI to implement, including:
   - Specific files to modify
   - Field names and types to add
   - Tests to write

Context:
- Current `ModelCapabilities` is missing fields used by CLI (`supports_reasoning`, `code_specialized`, `task_scores`)
- `TaskType` enum is missing `VISION`
- This causes `AttributeError` at runtime""",
    "6.1.3": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 6.1.3 - Provider Client and Fallback Strategy Design

Write a design document covering:

1. **Provider Maturity Classification**
   - Define tiers: Production, Beta, Experimental, Planned
   - Classify each of the 8 providers
   - Define what each tier means for users

2. **Bedrock Decision**
   - Option A: Implement minimal working Bedrock client
   - Option B: Mark as "experimental" and gate behind feature flag
   - Option C: Remove from registry until implemented
   - Recommendation with rationale

3. **Required Environment Variables**
   - For each provider, list required credentials
   - Define validation behavior when credentials missing
   - Error messages for misconfiguration

4. **Fallback Behavior**
   - What happens when a provider is unavailable?
   - What happens when credentials are missing?
   - How does this interact with fallback chains in `core.py`?
   - Should unavailable providers be silently skipped or hard-fail?

5. **Provider Health Checks**
   - How to detect if a provider is available at startup
   - Caching strategy for health status
   - Retry behavior for transient failures

6. **Implementation Tasks**
   List concrete tasks for Devin AI:
   - Files to modify
   - Feature flags to add
   - Tests to write
   - Documentation updates

Context:
- `BedrockClient` currently raises `NotImplementedError`, causing runtime failures
- Mixed maturity levels across providers (OpenAI fully supported, others partial)
- Need robust fallback when providers are missing credentials""",
    "6.3.3": """You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 6.3.3 - Cost & Telemetry Strategy Design

Write a design document covering:

1. **Cost Tracking Scope**
   - Per-call tracking: tokens in, tokens out, cost
   - Per-session aggregation: total cost for session
   - Per-model breakdown: cost by model
   - Per-provider breakdown: cost by provider
   - Time-based reporting: daily, weekly, monthly

2. **Data Model**
   - UsageRecord dataclass with timestamp, model_id, provider, tokens, cost
   - CostReport for aggregated reports
   - SessionSummary for current session

3. **Storage Strategy**
   - Evaluate: In-memory, JSON, SQLite, PostgreSQL
   - Recommendation with rationale

4. **API Surface**
   - CostTracker class with record_usage, get_session_cost, get_cost_by_model, etc.
   - CLI commands: cost, cost --detailed, cost --export

5. **Integration Points**
   - Where in core.py to record usage
   - How to get token counts from API responses
   - Handling providers that don't return token counts

6. **Implementation Tasks**
   List concrete tasks for Devin AI

Context:
- `show_cost_report()` in CLI returns "not yet implemented in v3.1"
- Model costs are defined but not tracked
- No storage for usage data""",
}

# Gemini CLI prompts - for terminal commands and scripts
GEMINI_CLI_PROMPTS = {
    "2.2.1": """You are assisting from a terminal context.

Task ID: 2.2.1 - AWS CodePipeline Bootstrap Commands

Given that CodePipeline YAML templates have been drafted, generate:

1. AWS CLI commands to create the pipeline infrastructure:

# Create S3 bucket for artifacts (replace ACCOUNT_ID and REGION)
aws s3 mb s3://lattice-lock-pipeline-artifacts-ACCOUNT_ID-REGION

# Create IAM role for CodePipeline (use provided trust policy)
aws iam create-role --role-name LatticeCodePipelineRole \\
  --assume-role-policy-document file://trust-policy.json

# Create IAM role for CodeBuild
aws iam create-role --role-name LatticeCodeBuildRole \\
  --assume-role-policy-document file://codebuild-trust-policy.json

# Attach policies (replace with actual policy ARNs)
aws iam attach-role-policy --role-name LatticeCodeBuildRole \\
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create CodeBuild project from template
aws cloudformation create-stack --stack-name lattice-codebuild \\
  --template-body file://codebuild-project.yml \\
  --parameters ParameterKey=ProjectName,ParameterValue=lattice-lock \\
  --capabilities CAPABILITY_IAM

# Create CodePipeline from template
aws cloudformation create-stack --stack-name lattice-pipeline \\
  --template-body file://pipeline.yml \\
  --parameters ParameterKey=GitHubRepo,ParameterValue=klappe-pm/lattice-lock-framework \\
  --capabilities CAPABILITY_IAM

2. Local validation commands:
# Validate CloudFormation templates
aws cloudformation validate-template --template-body file://pipeline.yml
aws cloudformation validate-template --template-body file://codebuild-project.yml

# Test buildspec locally with codebuild-local
docker run -it -v $(pwd):/project amazon/aws-codebuild-local \\
  --image aws/codebuild/standard:7.0 \\
  --buildspec buildspec.yml

3. Cleanup commands:
aws cloudformation delete-stack --stack-name lattice-pipeline
aws cloudformation delete-stack --stack-name lattice-codebuild

Note: Replace all placeholders (ACCOUNT_ID, REGION, etc.) with actual values.
Do not commit any real secrets or credentials.""",
    "2.3.1": """You are assisting from a terminal context.

Task ID: 2.3.1 - GCP Cloud Build Bootstrap Commands

Generate gcloud CLI commands:

1. Enable required APIs:
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

2. Create Cloud Build trigger:
gcloud builds triggers create github \\
  --name="lattice-lock-pr" \\
  --repo-name="lattice-lock-framework" \\
  --repo-owner="klappe-pm" \\
  --branch-pattern="^main$" \\
  --build-config="cloudbuild.yaml"

3. Grant permissions to Cloud Build service account:
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \\
  --member="serviceAccount:${CLOUDBUILD_SA}" \\
  --role="roles/secretmanager.secretAccessor"

4. Local testing:
# Submit build manually
gcloud builds submit --config=cloudbuild.yaml .

# View build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')

Note: Replace placeholders with actual values.""",
    "3.1.1": '''You are assisting from a terminal context.

Task ID: 3.1.1 - Error Classification Testing Commands

Generate commands to test the error classification system:

1. Create test error scenarios:
# Test schema validation error
python -c "
from lattice_lock.errors import SchemaValidationError, Severity
raise SchemaValidationError('Invalid schema', error_code='LL-VAL-001')
"

# Test configuration error
python -c "
from lattice_lock.errors import ConfigurationError
raise ConfigurationError('Missing API key', error_code='LL-CFG-001')
"

2. Run error classification tests:
pytest tests/test_error_classification.py -v

3. Generate error documentation:
python -c "
from lattice_lock.errors.remediation import generate_error_catalog
print(generate_error_catalog())
" > docs/error_catalog.md

4. Validate error serialization:
python -c "
import json
from lattice_lock.errors import SchemaValidationError
e = SchemaValidationError('Test', error_code='LL-VAL-001')
print(json.dumps(e.to_dict(), indent=2))
"''',
    "3.1.2": '''You are assisting from a terminal context.

Task ID: 3.1.2 - Error Middleware Testing Commands

Generate commands to test the error handling middleware:

1. Test middleware decorator:
python -c "
from lattice_lock.errors.middleware import ErrorMiddleware

middleware = ErrorMiddleware()

@middleware.catch_and_classify
def test_function():
    raise ValueError('Test error')

try:
    test_function()
except Exception as e:
    print(f'Caught: {e}')
"

2. Run middleware tests:
pytest tests/test_error_middleware.py -v

3. Test async middleware:
python -c "
import asyncio
from lattice_lock.errors.middleware import ErrorMiddleware

middleware = ErrorMiddleware()

@middleware.catch_and_classify
async def async_test():
    raise RuntimeError('Async error')

asyncio.run(async_test())
"

4. Check logging output:
LOG_LEVEL=DEBUG python -c "
from lattice_lock.errors.middleware import ErrorMiddleware
middleware = ErrorMiddleware()
# Test error logging
"''',
    "4.3.1": """You are assisting from a terminal context.

Task ID: 4.3.1 - Pilot Project 1 Setup Commands

Generate commands to scaffold and set up the first pilot project:

1. Scaffold the project:
lattice-lock init pilot-api-service --type service --ci github

2. Navigate and set up:
cd pilot-api-service
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

3. Run validation:
lattice-lock validate
lattice-lock sheriff
lattice-lock gauntlet

4. Run tests:
pytest -v

5. Start development server:
uvicorn main:app --reload

6. Verify CI:
git add .
git commit -m "Initial scaffold"
git push origin main
# Check GitHub Actions""",
    "4.3.2": """You are assisting from a terminal context.

Task ID: 4.3.2 - Pilot Project 2 Setup Commands

Generate commands to scaffold and set up the second pilot project:

1. Scaffold the project:
lattice-lock init pilot-cli-tool --type library --ci github

2. Navigate and set up:
cd pilot-cli-tool
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

3. Run validation:
lattice-lock validate
lattice-lock sheriff
lattice-lock gauntlet

4. Run tests:
pytest -v

5. Test CLI:
python -m pilot_cli_tool --help
python -m pilot_cli_tool command1 --option value

6. Verify CI:
git add .
git commit -m "Initial scaffold"
git push origin main""",
    "5.1.1": '''You are assisting from a terminal context.

Task ID: 5.1.1 - Prompt Architect Agent Setup Commands

Generate commands to set up the Prompt Architect Agent:

1. Create agent directory structure:
mkdir -p docs/agent_definitions/prompt_architect_agent/workflows
mkdir -p docs/agent_definitions/prompt_architect_agent/examples

2. Create agent files:
touch docs/agent_definitions/prompt_architect_agent/agent_prompt_architect.md
touch docs/agent_definitions/prompt_architect_agent/capabilities.md
touch docs/agent_definitions/prompt_architect_agent/workflows/generate_prompt.md
touch docs/agent_definitions/prompt_architect_agent/workflows/update_prompt.md

3. Create memory file:
touch docs/agent_memory/agents/agent_prompt_architect_memory.md

4. Validate agent structure:
python scripts/validate_agents.py

5. Test agent definition:
python -c "
import yaml
with open('docs/agent_definitions/prompt_architect_agent/agent_prompt_architect.md') as f:
    print('Agent definition loaded successfully')
"''',
    "5.1.2": '''You are assisting from a terminal context.

Task ID: 5.1.2 - Prompt Architect Integration Commands

Generate commands to integrate the Prompt Architect Agent:

1. Test tracker integration:
python scripts/prompt_tracker.py status

2. Generate a test prompt:
python -c "
# Simulate prompt generation
task_id = '2.2.1'
tool = 'devin'
print(f'Generating prompt for {task_id} ({tool})')
"

3. Update tracker with generated prompt:
python scripts/prompt_tracker.py update --id 2.2.1 --done

4. Run integration tests:
pytest tests/test_prompt_architect_integration.py -v

5. Validate all prompts:
python -c "
import json
with open('project_prompts/project_prompts_state.json') as f:
    state = json.load(f)
    print(f'Total prompts: {len(state[\"prompts\"])}')
"''',
}


def get_prompt(tool: str, task_id: str) -> str | None:
    """Get a prompt for a specific tool and task ID.

    Args:
        tool: One of 'claude_code', 'gemini_antimatter', 'gemini_cli'
        task_id: Task ID like '2.2.1', '3.1.1', etc.

    Returns:
        The prompt text, or None if not found.
    """
    prompts_map = {
        "claude_code": CLAUDE_CODE_PROMPTS,
        "gemini_antimatter": GEMINI_ANTIMATTER_PROMPTS,
        "gemini_cli": GEMINI_CLI_PROMPTS,
    }

    if tool not in prompts_map:
        return None

    return prompts_map[tool].get(task_id)


def list_tasks(tool: str) -> list[str]:
    """List all available task IDs for a tool.

    Args:
        tool: One of 'claude_code', 'gemini_antimatter', 'gemini_cli'

    Returns:
        List of task IDs.
    """
    prompts_map = {
        "claude_code": CLAUDE_CODE_PROMPTS,
        "gemini_antimatter": GEMINI_ANTIMATTER_PROMPTS,
        "gemini_cli": GEMINI_CLI_PROMPTS,
    }

    if tool not in prompts_map:
        return []

    return sorted(prompts_map[tool].keys())


def get_all_tools() -> list[str]:
    """Get list of all available tools."""
    return ["claude_code", "gemini_antimatter", "gemini_cli"]


if __name__ == "__main__":
    # Quick test
    print("Available tools:", get_all_tools())
    for tool in get_all_tools():
        print(f"\n{tool} tasks:", list_tasks(tool))
