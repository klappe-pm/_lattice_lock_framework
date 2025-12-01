# Agent System & Model Orchestrator Glossary

This document serves as the definitive reference for all variables, types, configuration options, and protocols used in the Lattice Lock Framework Agent System (v2.1) and Model Orchestrator.

---

## 1. Agent Configuration Variables

### Identity

- **`agent.identity.name`**: Unique identifier for the agent (kebab-case). Example: `model-orchestration-agent`.
- **`agent.identity.role`**: Human-readable job title. Example: "Chief Model Architect".
- **`agent.identity.version`**: Semantic versioning string. Example: "2.1.0".
- **`agent.identity.description`**: Brief description of the agent's purpose and capabilities.
- **`agent.identity.tags`**: List of keywords for discovery and categorization.

### Configuration

- **`agent.configuration.max_steps`**: Hard limit on the number of execution steps per task to prevent infinite loops. Default: `50`.
- **`agent.configuration.timeout_seconds`**: Maximum execution time before forced termination. Default: `300`.
- **`agent.configuration.log_level`**: Verbosity of logs. Options: `DEBUG`, `INFO`, `WARN`, `ERROR`. Default: `INFO`.
- **`agent.configuration.language`**: Language code for agent responses. Default: `en-US`.
- **`agent.configuration.timezone`**: Timezone for timestamp operations. Default: `UTC`.

---

## 2. Agent Core Protocols

### Planning (`planning`)

- **`enabled`**: Whether the agent performs formal planning before execution. Default: `true`.
- **`default_strategy`**: The approach to task execution.
	- **`linear`**: Steps executed one after another (sequential).
	- **`parallel`**: Independent steps executed concurrently.
	- **`recursive`**: Task broken down into smaller identical sub-tasks.
- **`phases`**: The standard lifecycle of a complex task.
	- **`intent_analysis`**: Deciphering what the user actually wants.
	- **`information_gathering`**: Collecting necessary context.
	- **`strategy_formulation`**: Deciding the high-level approach.
	- **`plan_generation`**: Creating the step-by-step execution plan.
	- **`validation`**: Checking the plan against constraints.
	- **`execution`**: Running the plan.
	- **`threat_modeling`**: (Security-specific) Identifying potential security threats.
	- **`analysis`**: Deep analysis of the problem space.
	- **`verification`**: Validating outputs and results.
	- **`reporting`**: Generating reports and summaries.
- **`constraints`**:
	- **`max_depth`**: Maximum recursion depth for nested planning. Default: `3`.
	- **`max_steps_per_phase`**: Maximum steps allowed within a single phase. Default: `10`.

### Estimation (`estimation`)

- **`enabled`**: Whether cost and complexity estimation is performed. Default: `true`.
- **`currency`**: Currency for cost calculations. Default: `USD`.
- **`complexity_weights`**: Multipliers for estimating effort.
	- **`code_modification`**: 1.5x base effort.
	- **`new_file_creation`**: 1.2x base effort.
	- **`read_only_analysis`**: 0.8x base effort.
- **`cost_limits`**:
	- **`warning_threshold`**: Cost level that triggers a user alert. Example: `0.1` ($0.10).
	- **`hard_limit`**: Cost level that stops execution immediately. Example: `1.0` ($1.00).
	- **`approval_required_above`**: Cost level requiring explicit user approval. Example: `0.5` ($0.50).

### Delegation (`delegation`)

- **`enabled`**: Whether the agent can delegate tasks to sub-agents. Default: `false`.
- **`max_depth`**: Maximum delegation chain depth. Default: `2`.
- **`allowed_subagents`**: List of sub-agent names that can be delegated to. Empty list means no delegation.
- **`delegation_triggers`**: Conditions that cause a task to be handed off.
	- **`complexity_threshold`**: If task complexity score exceeds threshold.
	- **`domain_mismatch`**: If task requires knowledge outside agent's domain.
	- **`resource_constraint`**: If agent is too busy or lacks context window.
	- **`confidence < threshold`**: If confidence score falls below acceptable level (e.g., 0.8).
	- **`task_requires_specialization`**: If specific expertise is needed.

### Scope

- **`can_access`**: List of file paths or directories the agent is allowed to read. Example: `[/src, /config, /docs]`.
- **`can_modify`**: List of file paths or directories the agent is allowed to write to. Example: `[/src/security, /config/security]`.
- **`cannot_access`**: Explicitly blocked paths for reading. Example: `[/production-data, /secrets]`.
- **`cannot_modify`**: Explicitly blocked paths for writing. Example: `[/core-system-logic]`.
- **`escalation_triggers`**: Conditions that require escalation to a parent agent or human.
	- If critical vulnerability found
	- If confidence below threshold
	- If user intent is unclear

### Context

- **`required_context`**: Information the agent needs to function effectively. Example: `[Security Policies, Architecture Diagrams, Threat Model]`.
- **`memory_persistence`**:
	- **`short_term`**: Scope of temporary memory. Options: `session_only`, `task_only`.
	- **`long_term`**: Persistent knowledge storage. Example: `project_knowledge_base`.
- **`knowledge_sources`**: External sources the agent can query.
	- **`path`**: File path or directory to documentation/code.
	- **`description`**: Purpose of this knowledge source.

---

## 3. Model Orchestration Types

### TaskType (Enum)

Categorizes the nature of the request to optimize model selection.

- **`CODE_GENERATION`**: Generating code snippets, functions, or entire modules. Requires high precision and syntax correctness.
- **`DEBUGGING`**: Analyzing code for errors and suggesting fixes. Requires strong reasoning and code understanding.
- **`ARCHITECTURAL_DESIGN`**: High-level system design, pattern selection, and structure planning. Requires large context window and reasoning.
- **`DOCUMENTATION`**: Writing docstrings, READMEs, or technical guides.
- **`TESTING`**: Generating unit tests or integration tests.
- **`DATA_ANALYSIS`**: Interpreting data or logs.
- **`GENERAL`**: General purpose queries or conversation.
- **`REASONING`**: Complex logic puzzles or multi-step reasoning tasks.
- **`VISION`**: Image processing and analysis (requires vision-capable models).

### ModelProvider (Enum)

Supported model providers.

- **`OPENAI`**: OpenAI (GPT-4o, O1, GPT-4o-mini, etc.)
- **`ANTHROPIC`**: Anthropic (Claude 3.5 Sonnet, Claude Opus, Claude Haiku)
- **`GOOGLE`**: Google (Gemini 1.5 Pro, Gemini 2.0 Flash, etc.)
- **`XAI`**: xAI (Grok Beta, Grok models)
- **`OLLAMA`**: Local models via Ollama (Llama 3, Qwen, DeepSeek, CodeLlama)
- **`AZURE`**: Azure OpenAI Service (enterprise OpenAI deployment)

---

## 4. Model Configuration

### ModelCapabilities

Each model in the registry is defined by a `ModelCapabilities` object with the following fields:

| Field | Type | Description |
|:--- |:--- |:--- |
| `name` | `str` | The display name of the model (e.g., "GPT-4o"). |
| `api_name` | `str` | The exact string identifier used in API calls (e.g., "gpt-4o-2024-08-06"). |
| `provider` | `ModelProvider` | The provider of the model. |
| `context_window` | `int` | Maximum number of tokens the model can process (input + output). |
| `input_cost` | `float` | Cost per 1M input tokens (in USD). |
| `output_cost` | `float` | Cost per 1M output tokens (in USD). |
| `reasoning_score` | `float` | Internal benchmark score (0-100) for reasoning capabilities. |
| `coding_score` | `float` | Internal benchmark score (0-100) for coding capabilities. |
| `speed_rating` | `float` | Rating (0-10) of the model's generation speed (10 = fastest). |
| `supports_vision` | `bool` | Whether the model can process image inputs. |
| `supports_function_calling` | `bool` | Whether the model supports tool/function calling. |

### TaskRequirements

When a request is made, a `TaskRequirements` object is created to filter suitable models:

| Field | Type | Description |
|:--- |:--- |:--- |
| `task_type` | `TaskType` | The type of task being performed. |
| `min_context` | `int` | Minimum context window required. |
| `max_cost` | `float` | Maximum acceptable cost per 1M tokens (optional). |
| `min_reasoning` | `float` | Minimum reasoning score required. |
| `min_coding` | `float` | Minimum coding score required. |
| `priority` | `str` | Strategy preference: "speed", "cost", "quality", or "balanced". |

---

## 5. Model Selection Strategies

The orchestrator uses different strategies to select the best model based on `TaskRequirements.priority`:

- **`quality_first`** (or `quality`): Prioritizes `reasoning_score` and `coding_score` above all else. Ignores cost. Best for critical tasks requiring maximum accuracy.
- **`speed_priority`** (or `speed`): Prioritizes `speed_rating`. Good for simple, interactive tasks where responsiveness matters most.
- **`cost_optimize`** (or `cost`): Prioritizes low `input_cost` and `output_cost`. Good for bulk processing or budget-constrained scenarios. Prefers local models.
- **`balanced`**: A weighted score combining quality, speed, and cost. Default strategy that provides optimal trade-offs.

### Model Selection Configuration (`model_selection`)

- **`default_provider`**: Preferred provider if no specific requirements. Example: `anthropic`.
- **`default_model`**: Fallback model for general tasks. Example: `claude-3.5-sonnet`.
- **`strategies`**: Task-specific model preferences.
	- **`code_generation`**:
		- `primary`: First choice model. Example: `codellama:34b`.
		- `fallback`: Backup if primary unavailable. Example: `claude-3.5-sonnet`.
		- `selection_criteria`: Prioritization rule. Example: `accuracy > speed`.
	- **`reasoning`**:
		- `primary`: Example: `deepseek-r1:70b`.
		- `fallback`: Example: `claude-3.5-sonnet`.
		- `selection_criteria`: Example: `depth > speed`.
	- **`quick_response`**:
		- `primary`: Example: `llama3.1:8b`.
		- `fallback`: Example: `gpt-4o-mini`.
		- `selection_criteria`: Example: `speed > accuracy`.
- **`overrides`**:
	- **`force_local_if_offline`**: Use local models when internet unavailable. Default: `true`.
	- **`force_cloud_if_complex`**: Use cloud models for complex tasks regardless of cost. Default: `false`.

---

## 6. Local Model Automation

Variables related to local model management (Ollama):

- **`RAM_BUFFER_MB`**: Amount of RAM to leave free for the system. Default: `1024` MB (1 GB).
- **`KEEP_ALIVE_MODELS`**: List of models to keep loaded in memory for faster response. Example: `[llama3.1:8b, codellama:13b]`.
- **`MAX_PARALLEL_MODELS`**: Maximum number of concurrent model instances. Default: `2`.
- **`OLLAMA_HOST`**: URL of the Ollama API. Default: `http://localhost:11434`.
- **`MODEL_SIZES`**: Dictionary mapping model names to their approximate VRAM/RAM usage in GB.
	- Example: `{"llama3.1:8b": 5.5, "codellama:34b": 20.0, "deepseek-r1:70b": 40.0}`

---

## 7. Agent Relationships

- **`Parent Agent`**: Coordinator responsible for planning, delegation, and final validation. Manages the overall task execution.
- **`Sub-Agent`**: Specialist responsible for executing specific scoped tasks delegated by the parent. Has narrow expertise.
- **`Sibling Agent`**: Agents at the same hierarchical level that can communicate via the parent agent for coordination.

---

## 8. Workflow

### Standard Workflow Phases

- **`init`**: Initialization phase.
	- Load configurations
	- Check dependencies
	- Verify access to resources
	- Load security policies (if applicable)
- **`execution_loop`**: Main execution cycle.
	- Receive task
	- Plan execution
	- Execute steps
	- Validate results
	- Report status
- **`cleanup`**: Teardown phase.
	- Close file handles
	- Clear temporary memory
	- Log summary
	- Archive artifacts

---

## 9. Output Formats & Templates

### Supported Output Formats

- **`JSON`**: Structured data for programmatic use. Best for API responses.
- **`Markdown`**: Human-readable text with formatting. Best for documentation and reports.
- **`YAML`**: Configuration data. Best for structured settings.
- **`Artifact`**: A file generated by the agent (code, image, document, config).

### Output Schema

Standard output structure:

```yaml
output:
  default_format: markdown
  schema:
    type: object
    properties:
      status:
        type: string
        enum: [success, failure, partial]
      result:
        type: object
      metrics:
        type: object
        properties:
          cost:
            type: number
          time:
            type: number
```

### Output Templates

- **`success`**: Template for successful task completion.
- **`failure`**: Template for task failures with error details and recovery suggestions.

---

## 10. Error Handling

### Error Handling Strategies

- **`ContextLimitExceeded`**: 
	- Action: `summarize_history`
	- Retry: `true`
- **`ApiRateLimit`**: 
	- Action: `exponential_backoff`
	- Retry: `true`
- **`ToolFailure`**: 
	- Action: `try_alternative_tool`
	- Retry: `true`

### Configuration

- **`max_retries`**: Maximum number of retry attempts. Default: `3`.
- **`fallback_mode`**: Behavior when all retries fail. Options: `graceful_degradation`, `fail_hard`.

---

## 11. Interaction Protocols

### User Interaction

- **`tone`**: Communication style. Options: `professional`, `casual`, `technical`. Default: `professional`.
- **`verbosity`**: Output detail level. Options: `concise`, `normal`, `verbose`. Default: `concise`.
- **`confirmation_required`**: Actions that require explicit user approval.
	- `delete_file`
	- `deploy_code`
	- `modify_production_config`

### Agent-to-Agent Communication

- **`protocol`**: Communication standard. Example: `json_rpc`.
- **`timeout`**: Maximum wait time for response. Example: `30s`.

---

## 12. Metrics & Monitoring

### Standard Metrics

- **`Task Success Rate`**: Percentage of successfully completed tasks. Target: `> 95%`.
- **`Average Execution Time`**: Mean time to complete tasks.
- **`Cost per Task`**: Average cost in USD per completed task.
- **`Model Selection Accuracy`**: How often the selected model was optimal.
- **`Delegation Rate`**: Percentage of tasks delegated to sub-agents.

---

## 13. Core Data Types (from `types.py`)

For developers working directly with the orchestrator codebase, the following types are defined in `types.py`:

- **`TaskType`**: Enum for task categorization
- **`ModelProvider`**: Enum for provider identification
- **`ModelCapabilities`**: Dataclass for model specifications
- **`TaskRequirements`**: Dataclass for filtering models
- **`AgentConfig`**: Dataclass for agent configuration
- **`ExecutionResult`**: Dataclass for task results
- **`DelegationRequest`**: Dataclass for sub-agent task delegation

---

## Version History

- **v2.1.0**: Unified agent system with model orchestration
- **v2.0.0**: Introduction of sub-agent delegation
- **v1.0.0**: Initial agent framework
