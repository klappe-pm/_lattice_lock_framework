# Multi-Agent Orchestration Playbook

**Last Updated:** 2025-12-04
**Purpose:** Coordinate multiple AI tools (Devin, Claude Code, Gemini in Antimatter, Gemini CLI) to accelerate Phase 2-5 completion.

## Overview

This playbook defines how different AI tools collaborate on the Lattice Lock Framework roadmap. Each tool has specific strengths:

| Tool | Strengths | Primary Use |
|------|-----------|-------------|
| **Devin AI** | Multi-step tasks, repo context, CI integration, testing, PRs | Implementation, integration, debugging |
| **Claude Code** | Code generation, refactoring, IDE context | Drafting code, templates, scaffolds |
| **Gemini (Antimatter)** | Architecture docs, design decisions, specifications | Design docs, ADRs, specs |
| **Gemini CLI** | Shell commands, quick scripts, boilerplate | CLI commands, bootstrap scripts |

## Tool Ownership Matrix

From `work_breakdown_structure.md`:

| Tool | Primary Files | Do NOT Touch |
|------|---------------|--------------|
| Devin AI | `pyproject.toml`, `version.txt`, `src/lattice_lock/__init__.py`, `scripts/orchestrator_cli.py`, CI templates (AWS/GCP), error boundaries | `src/lattice_lock_cli/`, `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, `developer_documentation/` |
| Gemini CLI | `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, Sheriff CLI, rollback system | `src/lattice_lock_validator/agents.py`, `src/lattice_lock_validator/structure.py`, `pyproject.toml`, `src/lattice_lock_cli/` |
| Codex CLI | `src/lattice_lock_validator/agents.py`, `src/lattice_lock_validator/structure.py`, `.pre-commit-config.yaml`, Gauntlet, dashboard | `src/lattice_lock_validator/schema.py`, `src/lattice_lock_validator/env.py`, `pyproject.toml`, `src/lattice_lock_cli/commands/` |
| Claude Code CLI | `src/lattice_lock_cli/__main__.py`, `src/lattice_lock_cli/commands/init.py`, `src/lattice_lock_cli/templates/`, GitHub Actions | `src/lattice_lock_cli/commands/validate.py`, `src/lattice_lock_cli/commands/doctor.py`, `src/lattice_lock_validator/`, `pyproject.toml` |
| Claude Code App | `src/lattice_lock_cli/commands/validate.py`, `src/lattice_lock_cli/commands/doctor.py`, `tests/integration/`, Admin API | `src/lattice_lock_cli/__main__.py`, `src/lattice_lock_cli/commands/init.py`, `src/lattice_lock_cli/templates/`, `pyproject.toml` |

---

## Devin AI Task Backlog

### Phase 2: CI/CD Integration

#### 2.2.1 - AWS CodePipeline Template
**Prompt file:** `phase2_cicd/2.2.1_devin_aws_codepipeline.md`
**Status:** Pending
**Subtasks:**
- 2.2.1.a: Review current test commands and build requirements
- 2.2.1.b: Create `src/lattice_lock_cli/templates/ci/aws/` directory structure
- 2.2.1.c: Implement `buildspec.yml.j2` for CodeBuild
- 2.2.1.d: Implement `pipeline.yml.j2` CloudFormation template
- 2.2.1.e: Add `--ci aws` flag to init command
- 2.2.1.f: Write unit tests in `tests/test_aws_templates.py`

#### 2.3.1 - GCP Cloud Build Template
**Prompt file:** `phase2_cicd/2.3.1_devin_gcp_cloudbuild.md`
**Status:** Pending
**Subtasks:**
- 2.3.1.a: Create `src/lattice_lock_cli/templates/ci/gcp/` directory structure
- 2.3.1.b: Implement `cloudbuild.yaml.j2` template
- 2.3.1.c: Add `--ci gcp` flag to init command
- 2.3.1.d: Write unit tests in `tests/test_gcp_templates.py`

### Phase 3: Error Handling & Admin

#### 3.1.1 - Error Classification System
**Prompt file:** `phase3_error_handling/3.1.1_devin_error_classification.md`
**Status:** Pending
**Subtasks:**
- 3.1.1.a: Create `src/lattice_lock/errors/` module structure
- 3.1.1.b: Implement error type hierarchy in `types.py`
- 3.1.1.c: Implement classification system in `classification.py`
- 3.1.1.d: Implement remediation mapping in `remediation.py`
- 3.1.1.e: Write unit tests

#### 3.1.2 - Error Handling Middleware
**Prompt file:** `phase3_error_handling/3.1.2_devin_error_middleware.md`
**Status:** Pending
**Subtasks:**
- 3.1.2.a: Create middleware for catching and classifying errors
- 3.1.2.b: Integrate with existing orchestrator
- 3.1.2.c: Add logging and telemetry hooks
- 3.1.2.d: Write integration tests

### Phase 4: Documentation & Pilot

#### 4.3.1 - Pilot Project 1 Setup
**Prompt file:** `phase4_documentation/4.3.1_devin_pilot_project_1.md`
**Status:** Pending
**Subtasks:**
- 4.3.1.a: Define pilot project requirements and scope
- 4.3.1.b: Scaffold project using lattice-lock CLI
- 4.3.1.c: Configure CI/CD pipeline
- 4.3.1.d: Document onboarding experience

#### 4.3.2 - Pilot Project 2 Setup
**Prompt file:** `phase4_documentation/4.3.2_devin_pilot_project_2.md`
**Status:** Pending
**Subtasks:**
- 4.3.2.a: Define second pilot project (different use case)
- 4.3.2.b: Scaffold and configure
- 4.3.2.c: Validate framework flexibility
- 4.3.2.d: Collect feedback

### Phase 5: Prompt Automation

#### 5.1.1 - Prompt Architect Agent Core Setup
**Prompt file:** `phase5_prompt_automation/5.1.1_devin_prompt_architect_core.md`
**Status:** Pending
**Subtasks:**
- 5.1.1.a: Create agent definition in `agent_definitions/prompt_architect_agent/`
- 5.1.1.b: Define agent memory structure
- 5.1.1.c: Implement core agent logic
- 5.1.1.d: Write unit tests

#### 5.1.2 - Prompt Architect Integration
**Prompt file:** `phase5_prompt_automation/5.1.2_devin_prompt_architect_integration.md`
**Status:** Pending
**Subtasks:**
- 5.1.2.a: Integrate with Project Agent
- 5.1.2.b: Connect to prompt_tracker.py
- 5.1.2.c: Implement prompt generation workflow
- 5.1.2.d: Write integration tests

---

## Cross-Tool Prompts by Task

### 2.2.1 - AWS CodePipeline Template

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

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
- List of required IAM permissions
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

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
- Existing templates in `src/lattice_lock_cli/templates/`
```

#### Prompt for Gemini CLI

```
You are assisting from a terminal context.

Task ID: 2.2.1 - AWS CodePipeline Bootstrap Commands

Given that CodePipeline YAML templates have been drafted, generate:

1. AWS CLI commands to create the pipeline infrastructure:

# Create S3 bucket for artifacts (replace ACCOUNT_ID and REGION)
aws s3 mb s3://lattice-lock-pipeline-artifacts-ACCOUNT_ID-REGION

# Create IAM role for CodePipeline (use provided trust policy)
aws iam create-role --role-name LatticeCodePipelineRole \
  --assume-role-policy-document file://trust-policy.json

# Create IAM role for CodeBuild
aws iam create-role --role-name LatticeCodeBuildRole \
  --assume-role-policy-document file://codebuild-trust-policy.json

# Attach policies (replace with actual policy ARNs)
aws iam attach-role-policy --role-name LatticeCodeBuildRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create CodeBuild project from template
aws cloudformation create-stack --stack-name lattice-codebuild \
  --template-body file://codebuild-project.yml \
  --parameters ParameterKey=ProjectName,ParameterValue=lattice-lock \
  --capabilities CAPABILITY_IAM

# Create CodePipeline from template
aws cloudformation create-stack --stack-name lattice-pipeline \
  --template-body file://pipeline.yml \
  --parameters ParameterKey=GitHubRepo,ParameterValue=klappe-pm/lattice-lock-framework \
  --capabilities CAPABILITY_IAM

2. Local validation commands:
# Validate CloudFormation templates
aws cloudformation validate-template --template-body file://pipeline.yml
aws cloudformation validate-template --template-body file://codebuild-project.yml

# Test buildspec locally with codebuild-local
docker run -it -v $(pwd):/project amazon/aws-codebuild-local \
  --image aws/codebuild/standard:7.0 \
  --buildspec buildspec.yml

3. Cleanup commands:
aws cloudformation delete-stack --stack-name lattice-pipeline
aws cloudformation delete-stack --stack-name lattice-codebuild

Note: Replace all placeholders (ACCOUNT_ID, REGION, etc.) with actual values.
Do not commit any real secrets or credentials.
```

---

### 2.3.1 - GCP Cloud Build Template

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

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
- List of required IAM permissions
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

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
   List concrete tasks for Devin AI and Claude Code to implement.
```

#### Prompt for Gemini CLI

```
You are assisting from a terminal context.

Task ID: 2.3.1 - GCP Cloud Build Bootstrap Commands

Generate gcloud CLI commands:

1. Enable required APIs:
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

2. Create Cloud Build trigger:
gcloud builds triggers create github \
  --name="lattice-lock-pr" \
  --repo-name="lattice-lock-framework" \
  --repo-owner="klappe-pm" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"

3. Grant permissions to Cloud Build service account:
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/secretmanager.secretAccessor"

4. Local testing:
# Submit build manually
gcloud builds submit --config=cloudbuild.yaml .

# View build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')

Note: Replace placeholders with actual values.
```

---

### 3.1.1 - Error Classification System

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

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
- Example usage snippets
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

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
   List concrete tasks for Devin AI to implement.
```

#### Prompt for Gemini CLI

```
You are assisting from a terminal context.

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
"
```

---

### 3.1.2 - Error Handling Middleware

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

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
- Integration example with orchestrator
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

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
   List concrete tasks for Devin AI.
```

---

### 4.3.1 & 4.3.2 - Pilot Projects

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE.

Task ID: 4.3.1/4.3.2 - Pilot Project Scaffolding

Context:
- Create two pilot projects to validate the Lattice Lock Framework
- Use the lattice-lock CLI to scaffold projects

Goals:
1. Pilot Project 1 - Simple API Service:
   - FastAPI backend with 3-5 endpoints
   - SQLModel for database
   - Full Lattice Lock integration

2. Pilot Project 2 - CLI Tool:
   - Click-based CLI application
   - Multiple commands
   - Configuration management

For each project, generate:
- Project structure
- lattice.yaml schema definition
- Basic implementation code
- Test suite skeleton
- CI/CD configuration

Output:
- Directory structure for each project
- Key file contents
- Setup instructions
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 4.3.1/4.3.2 - Pilot Project Design Documents

Write design documents for two pilot projects:

**Pilot 1: API Service**
1. Project Goals
2. Technical Requirements
3. Schema Design (entities, relationships)
4. API Endpoints
5. Success Metrics
6. Onboarding Checklist

**Pilot 2: CLI Tool**
1. Project Goals
2. Technical Requirements
3. Command Structure
4. Configuration Schema
5. Success Metrics
6. Onboarding Checklist

Include feedback collection criteria for each.
```

---

### 5.1.1 & 5.1.2 - Prompt Architect Agent

#### Prompt for Claude Code

```
You are Claude Code running inside an IDE with the `lattice-lock-framework` repo open.

Task ID: 5.1.1/5.1.2 - Prompt Architect Agent Implementation

Context:
- Repository: lattice-lock-framework
- Agent definitions in: `agent_definitions/`
- Memory protocol in: `agent_memory/universal_memory_directive.md`

Goals:
1. Create `agent_definitions/prompt_architect_agent/`:
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
   `agent_memory/agents/agent_prompt_architect_memory.md`

4. Integration with prompt_tracker.py:
   - Auto-generate prompts for new tasks
   - Update tracker when prompts are created

Output:
- Complete agent definition files
- Memory file template
- Integration code snippets
```

#### Prompt for Gemini (Antimatter)

```
You are helping maintain architectural documentation for the lattice-lock-framework.

Task ID: 5.1.1/5.1.2 - Prompt Architect Agent Specification

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
   - <30 second generation time
```

---

## Execution Order

For optimal time to completion, execute in this order:

### Parallel Track A (Devin AI)
1. 2.2.1 - AWS CodePipeline (unblocks AWS users)
2. 2.3.1 - GCP Cloud Build (unblocks GCP users)
3. 3.1.1 - Error Classification (foundation for 3.1.2)
4. 3.1.2 - Error Middleware (depends on 3.1.1)
5. 5.1.1 - Prompt Architect Core
6. 5.1.2 - Prompt Architect Integration
7. 4.3.1 - Pilot Project 1
8. 4.3.2 - Pilot Project 2

### Parallel Track B (Claude Code / Gemini)
Use prompts above to generate:
1. Design docs (Gemini Antimatter) - can run immediately
2. Code drafts (Claude Code) - can run immediately
3. Bootstrap scripts (Gemini CLI) - after design docs

### Handoff Protocol
1. Gemini (Antimatter) generates design doc
2. Claude Code generates code draft based on design
3. Gemini CLI generates bootstrap/test commands
4. Devin AI integrates, tests, and creates PR

---

## Quick Reference

### Start Next Devin Task
```bash
# Check current status
python scripts/prompt_tracker.py status

# Pick up next task
python scripts/prompt_tracker.py next --tool devin --model "gpt-4"

# Mark as done
python scripts/prompt_tracker.py update --id 2.2.1 --done --pr "https://github.com/..."
```

### Prompt File Naming
`{phase}.{epic}.{task}_{tool}.md`

Example: `2.2.1_devin_aws_codepipeline.md`

---

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- `version.txt` and `pyproject.toml` must stay in sync (currently 2.1.0)
- Never commit secrets or credentials
- Follow tool ownership matrix strictly
