# Model Orchestrator - Comprehensive Diagram Documentation

Detailed Mermaid.js diagrams documenting the Model Orchestrator subsystem, including request routing, model selection, fallback strategies, consensus voting, and cost tracking.

---

## Table of Contents

1. [Request Routing Sequence](#1-request-routing-sequence)
2. [Class Architecture](#2-class-architecture)
3. [Model Selection Logic](#3-model-selection-logic)
4. [Provider Fallback Strategy](#4-provider-fallback-strategy)
5. [Consensus Engine Voting](#5-consensus-engine-voting)
6. [Request Routing Pipeline](#6-request-routing-pipeline)
7. [Chain Execution Flow](#7-chain-execution-flow)
8. [Context Window Management](#8-context-window-management)
9. [Cost Tracking Data Flow](#9-cost-tracking-data-flow)

---

## 1. Request Routing Sequence

**Purpose**: Illustrates the complete request flow from user input through CLI to LLM provider response.

**Diagram Type**: Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI
    participant Orchestrator as ModelOrchestrator
    participant Analyzer as TaskAnalyzer
    participant Selector as ModelSelector
    participant Registry as ModelRegistry
    participant Pool as ClientPool
    participant Executor as ConversationExecutor
    participant Provider as LLM Provider

    User->>CLI: lattice ask "prompt"
    CLI->>Orchestrator: route_request(prompt)

    Note over Orchestrator,Analyzer: Task Analysis Phase
    Orchestrator->>Analyzer: analyze_async(prompt)
    Analyzer-->>Orchestrator: TaskRequirements(type, complexity)

    Note over Orchestrator,Registry: Model Selection Phase
    Orchestrator->>Selector: select_best_model(requirements)
    Selector->>Registry: get_capabilities()
    Selector-->>Orchestrator: model_id

    Orchestrator->>Registry: get_model(model_id)
    Registry-->>Orchestrator: ModelCapabilities

    Note over Orchestrator,Provider: Execution Phase
    Orchestrator->>Pool: get_client(provider_name)
    Pool-->>Orchestrator: APIClient

    Orchestrator->>Executor: execute(model, client, messages)
    Executor->>Provider: chat(messages)
    Provider-->>Executor: Response
    Executor-->>Orchestrator: APIResponse
    Orchestrator-->>CLI: APIResponse
    CLI-->>User: Display Output
```

### Node Descriptions

| Node | Description | Responsibility |
|------|-------------|----------------|
| **User** | End user interacting with CLI | Initiates requests via `lattice ask` |
| **CLI** | Command-line interface entry point | Parses commands, invokes orchestrator |
| **ModelOrchestrator** | Central coordination hub | Routes requests, manages lifecycle |
| **TaskAnalyzer** | Prompt analysis engine | Determines task type and complexity |
| **ModelSelector** | Model selection algorithm | Chooses optimal model based on requirements |
| **ModelRegistry** | Model metadata store | Provides model capabilities and configs |
| **ClientPool** | Provider client manager | Manages connections to LLM providers |
| **ConversationExecutor** | Request executor | Handles API calls and response processing |
| **LLM Provider** | External AI service | OpenAI, Anthropic, Google, etc. |

### Related Source Files

- [`src/orchestrator/core.py`](../../src/orchestrator/core.py) - ModelOrchestrator class
- [`src/orchestrator/analysis/analyzer.py`](../../src/orchestrator/analysis/analyzer.py) - TaskAnalyzer
- [`src/orchestrator/selection.py`](../../src/orchestrator/selection.py) - ModelSelector
- [`src/orchestrator/registry.py`](../../src/orchestrator/registry.py) - ModelRegistry
- [`src/orchestrator/execution.py`](../../src/orchestrator/execution.py) - ClientPool, ConversationExecutor
- [`src/cli/commands/ask.py`](../../src/cli/commands/ask.py) - CLI ask command

---

## 2. Class Architecture

**Purpose**: Shows the class structure and relationships within the Orchestrator module.

**Diagram Type**: UML Class Diagram

```mermaid
classDiagram
    class ModelOrchestrator {
        +ModelRegistry registry
        +ModelGuideParser guide
        +ModelScorer scorer
        +TaskAnalyzer analyzer
        +CostTracker cost_tracker
        +FunctionCallHandler function_call_handler
        +ModelSelector selector
        +ClientPool client_pool
        +ConversationExecutor executor
        +register_function(name, func)
        +route_request(prompt, model_id, task_type) APIResponse
        +shutdown()
        -_handle_fallback(requirements, prompt, failed_model) APIResponse
        -_initialize_analyzer_client()
        +get_available_providers() list
        +check_provider_status() dict
    }

    class ModelRegistry {
        -_models: dict
        +get_model(model_id) ModelCapability
        +list_models() list
        +register_model(model) void
    }

    class TaskAnalyzer {
        -router_client: BaseProvider
        -_cache: LRUCache
        +analyze_async(prompt) TaskRequirements
        -_analyze_heuristic(prompt) TaskRequirements
    }

    class ModelSelector {
        -registry: ModelRegistry
        -scorer: ModelScorer
        -guide: ModelGuideParser
        +select_best_model(requirements) string
        +get_fallback_chain(requirements, failed_model) list
    }

    class ClientPool {
        -_clients: dict
        +get_client(provider_name) BaseProvider
        +close_all() void
    }

    class ConversationExecutor {
        -function_handler: FunctionCallHandler
        -cost_tracker: CostTracker
        +execute(model_cap, client, messages) APIResponse
    }

    class CostTracker {
        -registry: ModelRegistry
        +track_usage(model_id, tokens) void
        +get_total_cost() float
    }

    class FunctionCallHandler {
        -_functions: dict
        +register_function(name, func) void
        +handle_call(name, args) Any
    }

    ModelOrchestrator --> ModelRegistry
    ModelOrchestrator --> TaskAnalyzer
    ModelOrchestrator --> ModelSelector
    ModelOrchestrator --> ClientPool
    ModelOrchestrator --> ConversationExecutor
    ModelOrchestrator --> CostTracker
    ModelOrchestrator --> FunctionCallHandler
    ModelSelector --> ModelRegistry
    ModelSelector --> ModelScorer
    ConversationExecutor --> FunctionCallHandler
    ConversationExecutor --> CostTracker
```

### Class Descriptions

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| **ModelOrchestrator** | Central coordinator for all orchestration | `route_request()`, `shutdown()` |
| **ModelRegistry** | Stores model metadata and capabilities | `get_model()`, `list_models()` |
| **TaskAnalyzer** | Analyzes prompts to determine requirements | `analyze_async()` |
| **ModelSelector** | Selects optimal model using scoring | `select_best_model()`, `get_fallback_chain()` |
| **ClientPool** | Manages provider client connections | `get_client()`, `close_all()` |
| **ConversationExecutor** | Executes requests with function calling | `execute()` |
| **CostTracker** | Tracks token usage and costs | `track_usage()`, `get_total_cost()` |
| **FunctionCallHandler** | Handles tool/function invocations | `register_function()`, `handle_call()` |

### Related Source Files

- [`src/orchestrator/core.py`](../../src/orchestrator/core.py) - ModelOrchestrator (lines 22-296)
- [`src/orchestrator/registry.py`](../../src/orchestrator/registry.py) - ModelRegistry (360 lines)
- [`src/orchestrator/analysis/analyzer.py`](../../src/orchestrator/analysis/analyzer.py) - TaskAnalyzer
- [`src/orchestrator/selection.py`](../../src/orchestrator/selection.py) - ModelSelector
- [`src/orchestrator/execution.py`](../../src/orchestrator/execution.py) - ClientPool, ConversationExecutor
- [`src/orchestrator/cost/tracker.py`](../../src/orchestrator/cost/tracker.py) - CostTracker
- [`src/orchestrator/function_calling.py`](../../src/orchestrator/function_calling.py) - FunctionCallHandler

---

## 3. Model Selection Logic

**Purpose**: Documents the algorithm for selecting the optimal model based on task requirements.

**Diagram Type**: Flowchart

```mermaid
flowchart TD
    Start([TaskRequirements Input]) --> Filter1[Filter by Capability]
    Filter1 --> Filter2[Filter by Context Window]

    Filter2 --> Candidates{Candidates > 0?}

    Candidates -- No --> Fallback[Relax Constraints]
    Fallback --> Filter1

    Candidates -- Yes --> Score[Score Candidates]

    subgraph Scoring["Weighted Scoring"]
        Score --> CostWeight[Apply Cost Weight]
        Score --> LatencyWeight[Apply Latency Weight]
        Score --> QualityWeight[Apply Quality Weight]
    end

    CostWeight & LatencyWeight & QualityWeight --> Aggregate[Calculate Final Score]

    Aggregate --> Sort[Sort Descending]
    Sort --> Pick[Select Top Model]

    Pick --> End([Selected Model ID])

    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style Scoring fill:#e3f2fd
```

### Node Descriptions

| Node | Description | Logic |
|------|-------------|-------|
| **Filter by Capability** | First-pass filter | Removes models lacking required capabilities (code, vision, etc.) |
| **Filter by Context Window** | Size filter | Ensures model can handle prompt length |
| **Relax Constraints** | Fallback logic | Reduces requirements if no candidates found |
| **Apply Cost Weight** | Cost scoring | Lower cost = higher score (configurable weight) |
| **Apply Latency Weight** | Speed scoring | Lower latency = higher score |
| **Apply Quality Weight** | Quality scoring | Higher benchmark scores = higher score |
| **Calculate Final Score** | Aggregation | Weighted sum of all factors |
| **Select Top Model** | Final selection | Returns highest-scoring model ID |

### Related Source Files

- [`src/orchestrator/selection.py`](../../src/orchestrator/selection.py) - ModelSelector.select_best_model()
- [`src/orchestrator/scoring.py`](../../src/orchestrator/scoring.py) - ModelScorer with weight configuration
- [`src/orchestrator/types.py`](../../src/orchestrator/types.py) - TaskRequirements dataclass

---

## 4. Provider Fallback Strategy

**Purpose**: Shows the multi-provider fallback mechanism when primary providers fail.

**Diagram Type**: Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Orch as ModelOrchestrator
    participant P1 as Primary Provider<br/>(e.g., GPT-4)
    participant P2 as Fallback 1<br/>(e.g., Claude 3)
    participant P3 as Fallback 2<br/>(e.g., Llama 3)
    participant User

    Orch->>P1: attempt_request(prompt)

    alt Success
        P1-->>Orch: 200 OK (Response)
        Orch-->>User: Return Response
    else Timeout / 5xx Error
        P1--xOrch: Error
        Note over Orch: Log Failure & Record Cost

        Orch->>P2: attempt_request(prompt)

        alt Success
            P2-->>Orch: 200 OK (Response)
            Orch-->>User: Return Response
        else Error
            P2--xOrch: Error
            Note over Orch: Log Failure & Record Cost

            Orch->>P3: attempt_request(prompt)
            alt Success
                P3-->>Orch: 200 OK (Response)
                Orch-->>User: Return Response
            else All Providers Exhausted
                Orch--xUser: ProviderExhaustedError
            end
        end
    end
```

### Node Descriptions

| Node | Description | Error Handling |
|------|-------------|----------------|
| **ModelOrchestrator** | Fallback coordinator | Maintains fallback chain, logs failures |
| **Primary Provider** | First-choice model | Usually highest quality (GPT-4, Claude 3.5) |
| **Fallback 1** | Second-choice model | Alternative provider or model |
| **Fallback 2** | Third-choice model | Often local/self-hosted (Ollama) |

### Failure Scenarios

| Scenario | Trigger | Recovery |
|----------|---------|----------|
| Timeout | Request exceeds timeout threshold | Try next provider |
| Rate Limit (429) | Provider quota exceeded | Try next provider |
| Server Error (5xx) | Provider internal error | Try next provider |
| Auth Error (401/403) | Invalid credentials | Skip provider, log warning |
| All Failed | No providers available | Raise ProviderExhaustedError |

### Related Source Files

- [`src/orchestrator/core.py`](../../src/orchestrator/core.py) - `_handle_fallback()` method (lines 168-265)
- [`src/orchestrator/selection.py`](../../src/orchestrator/selection.py) - `get_fallback_chain()`
- [`src/orchestrator/providers/__init__.py`](../../src/orchestrator/providers/__init__.py) - ProviderAvailability

---

## 5. Consensus Engine Voting

**Purpose**: Illustrates multi-model consensus voting for high-stakes decisions.

**Diagram Type**: Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Engine as ConsensusEngine
    participant Voter1 as Model A<br/>(GPT-4)
    participant Voter2 as Model B<br/>(Claude 3)
    participant Voter3 as Model C<br/>(Gemini)

    Client->>Engine: request_consensus(prompt, strategy='majority')

    Note over Engine: Parallel Vote Collection

    par Collect Votes
        Engine->>Voter1: get_response(prompt)
        Engine->>Voter2: get_response(prompt)
        Engine->>Voter3: get_response(prompt)
    end

    Voter1-->>Engine: Response A
    Voter2-->>Engine: Response B
    Voter3-->>Engine: Response A

    Engine->>Engine: tally_votes()
    Note right of Engine: A: 2 votes<br/>B: 1 vote

    Engine->>Engine: determine_winner(strategy)

    Engine-->>Client: Response A (Winner)
```

### Node Descriptions

| Node | Description | Role |
|------|-------------|------|
| **Client** | Consensus requester | Initiates consensus request with strategy |
| **ConsensusEngine** | Vote coordinator | Collects, tallies, and determines winner |
| **Model A/B/C** | Voting models | Provide independent responses |

### Consensus Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `majority` | Most common response wins | General consensus |
| `unanimous` | All must agree | High-stakes decisions |
| `weighted` | Votes weighted by model quality | Quality-sensitive tasks |
| `synthesis` | AI synthesizes best parts | Creative tasks |

### Related Source Files

- [`src/consensus/engine.py`](../../src/consensus/engine.py) - ConsensusEngine class
- [`src/consensus/types.py`](../../src/consensus/types.py) - ConsensusRequest, ConsensusStrategy

---

## 6. Request Routing Pipeline

**Purpose**: Shows the complete request processing pipeline with decision points.

**Diagram Type**: Flowchart

```mermaid
flowchart TD
    Input([User Prompt]) --> Analyzer[Task Analyzer]

    Analyzer --> Complexity{Complexity<br/>Assessment}

    Complexity -- High --> Planner[Create Subtasks]
    Complexity -- Low --> Direct[Direct Processing]

    Planner --> Router[Semantic Router]
    Direct --> Router

    Router --> ModelSelect[Model Selector]

    ModelSelect --> CheckQuota{Check Quota}
    CheckQuota -- Exceeded --> Error([Quota Error])
    CheckQuota -- OK --> Execute[Execute Request]

    Execute --> Stream{Stream<br/>Response?}
    Stream -- Yes --> Yield[Yield Chunks]
    Stream -- No --> Return[Return Complete]

    Yield --> Cost[Track Cost]
    Return --> Cost

    Cost --> End([Response])

    style Input fill:#e8f5e9
    style End fill:#e8f5e9
    style Error fill:#ffebee
```

### Node Descriptions

| Node | Description | Output |
|------|-------------|--------|
| **Task Analyzer** | Analyzes prompt complexity | TaskRequirements |
| **Create Subtasks** | Breaks complex tasks | List of subtasks |
| **Semantic Router** | Routes by task semantics | Routing decision |
| **Model Selector** | Chooses optimal model | Model ID |
| **Check Quota** | Validates usage limits | Pass/Fail |
| **Execute Request** | Calls LLM API | Raw response |
| **Track Cost** | Records usage metrics | Cost record |

### Related Source Files

- [`src/orchestrator/analysis/analyzer.py`](../../src/orchestrator/analysis/analyzer.py) - TaskAnalyzer
- [`src/orchestrator/analysis/semantic_router.py`](../../src/orchestrator/analysis/semantic_router.py) - SemanticRouter
- [`src/orchestrator/selection.py`](../../src/orchestrator/selection.py) - ModelSelector
- [`src/orchestrator/cost/tracker.py`](../../src/orchestrator/cost/tracker.py) - CostTracker

---

## 7. Chain Execution Flow

**Purpose**: Illustrates multi-step chain execution with parallel branches.

**Diagram Type**: Flowchart (LR)

```mermaid
flowchart LR
    Start([Chain<br/>Trigger]) --> Step1[Step 1:<br/>Research]

    Step1 --> |Output| Context1[Update<br/>Context]

    Context1 --> Step2[Step 2:<br/>Draft]

    Step2 --> |Output| Context2[Update<br/>Context]

    Context2 --> Parallel{Parallel<br/>Execution}

    Parallel --> Step3A[Step 3A:<br/>Review]
    Parallel --> Step3B[Step 3B:<br/>Format]

    Step3A & Step3B --> Join((Join))

    Join --> Final[Final<br/>Output]

    style Start fill:#e8f5e9
    style Final fill:#e8f5e9
    style Join fill:#fff3e0
```

### Node Descriptions

| Node | Description | Context Update |
|------|-------------|----------------|
| **Step 1: Research** | Initial research phase | Adds research findings |
| **Step 2: Draft** | Content drafting | Adds draft content |
| **Step 3A: Review** | Quality review (parallel) | Adds review notes |
| **Step 3B: Format** | Formatting (parallel) | Adds formatted content |
| **Join** | Merge parallel results | Combines all outputs |

### Related Source Files

- [`src/orchestrator/chains/`](../../src/orchestrator/chains/) - Chain execution module
- [`src/agents/prompt_architect/orchestrator.py`](../../src/agents/prompt_architect/orchestrator.py) - Pipeline orchestration

---

## 8. Context Window Management

**Purpose**: Shows state machine for managing conversation context and overflow.

**Diagram Type**: State Diagram

```mermaid
stateDiagram-v2
    [*] --> NewConversation

    NewConversation --> Active: Add Message

    state Active {
        [*] --> CheckLength
        CheckLength --> Fit: Tokens < Limit
        CheckLength --> Overflow: Tokens > Limit

        Fit --> WaitUser: Ready for Input
        WaitUser --> CheckLength: New Message

        state Overflow {
            [*] --> SelectStrategy
            SelectStrategy --> SlidingWindow: Keep Last N
            SelectStrategy --> Summarization: Compress History
            SelectStrategy --> VectorStore: Move to Long-Term

            SlidingWindow --> Reassemble
            Summarization --> Reassemble
            VectorStore --> Reassemble

            Reassemble --> [*]
        }

        Overflow --> CheckLength: Context Reduced
    }

    Active --> [*]: Conversation End
```

### State Descriptions

| State | Description | Transition |
|-------|-------------|------------|
| **NewConversation** | Fresh conversation started | → Active on first message |
| **CheckLength** | Token count validation | → Fit or Overflow |
| **Fit** | Context within limits | → WaitUser |
| **Overflow** | Context exceeds limits | → Strategy selection |
| **SlidingWindow** | Remove oldest messages | Keeps last N messages |
| **Summarization** | Compress older messages | AI-generated summary |
| **VectorStore** | Offload to vector DB | Semantic retrieval |

### Related Source Files

- [`src/orchestrator/context/`](../../src/orchestrator/context/) - Context management module
- [`src/database/vector/`](../../src/database/vector/) - Vector storage integration

---

## 9. Cost Tracking Data Flow

**Purpose**: Documents the cost tracking and budget monitoring pipeline.

**Diagram Type**: Data Flow Diagram

```mermaid
flowchart LR
    subgraph Source["Data Source"]
        Provider[LLM Provider]
    end

    subgraph Processing["Processing Pipeline"]
        Extractor[Token<br/>Extractor]
        Calculator[Cost<br/>Calculator]
        Aggregator[Cost<br/>Aggregator]
    end

    subgraph Storage["Persistence"]
        DB[(Database)]
        Budget[Budget<br/>Tracker]
    end

    subgraph Alerting["Alerting"]
        Check{Over<br/>Budget?}
        Admin[Notify<br/>Admin]
    end

    Provider --> |Response<br/>Metadata| Extractor
    Extractor --> |Input/Output<br/>Tokens| Calculator
    Calculator --> |USD Cost| Aggregator

    Aggregator --> |Write| DB
    Aggregator --> |Update| Budget

    Budget --> Check
    Check -- Yes --> Admin
    Check -- No --> Done([Continue])

    style Provider fill:#e1f5fe
    style DB fill:#fff3e0
    style Admin fill:#ffebee
```

### Node Descriptions

| Node | Description | Data Flow |
|------|-------------|-----------|
| **LLM Provider** | External AI service | Provides response with usage metadata |
| **Token Extractor** | Parses response | Extracts input/output token counts |
| **Cost Calculator** | Computes costs | Applies per-token pricing |
| **Cost Aggregator** | Accumulates costs | Maintains running totals |
| **Database** | Persistent storage | Stores CostRecord entries |
| **Budget Tracker** | Monitors limits | Tracks against configured budgets |
| **Notify Admin** | Alert mechanism | Sends notifications on overage |

### Cost Tracking Schema

```python
@dataclass
class CostRecord:
    id: str
    project_id: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
```

### Related Source Files

- [`src/orchestrator/cost/tracker.py`](../../src/orchestrator/cost/tracker.py) - CostTracker class
- [`src/orchestrator/cost/calculator.py`](../../src/orchestrator/cost/calculator.py) - Cost calculation logic
- [`src/database/models/cost.py`](../../src/database/models/cost.py) - CostRecord model
- [`src/admin/services.py`](../../src/admin/services.py) - Budget alerting

---

## Summary

| Diagram | Type | Purpose | Key Components |
|---------|------|---------|----------------|
| Request Routing Sequence | Sequence | End-to-end request flow | 9 participants |
| Class Architecture | Class | Module structure | 8 classes |
| Model Selection Logic | Flowchart | Selection algorithm | 3-weight scoring |
| Provider Fallback | Sequence | Error recovery | 3-provider chain |
| Consensus Voting | Sequence | Multi-model agreement | Parallel voting |
| Routing Pipeline | Flowchart | Decision pipeline | 8 decision points |
| Chain Execution | Flowchart | Multi-step workflows | Parallel branches |
| Context Management | State | Token overflow handling | 3 strategies |
| Cost Tracking | Data Flow | Usage monitoring | Budget alerts |

---

## Usage

These diagrams render in GitHub, GitLab, VS Code (Mermaid extension), Obsidian, and [mermaid.live](https://mermaid.live).
