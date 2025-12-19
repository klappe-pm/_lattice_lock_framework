# Model Orchestrator Architecture

```text

┌─────────────────────────────────────────────┐
│           Orchestrator CLI & API            │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │   Intelligent     │
        │   Model Router    │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐ ┌─────▼─────┐ ┌─────▼────┐
│ Cost   │ │   Task    │ │Capability│
│Tracker │ │ Analyzer  │ │Matcher   │
└───┬────┘ └─────┬─────┘ └─────┬────┘
    │            │             │
┌───▼────────────▼─────────────▼────┐
│         63 Models Across          │
│  ┌──────┐┌──────┐┌──────┐┌──────┐ │
│  │Local ││OpenAI││Claude││Grok  │ │
│  │(20)  ││(11)  ││(7)   ││(5)   │ │
│  └──────┘└──────┘└──────┘└──────┘ │
│  ┌──────┐┌──────┐┌──────┐┌──────┐ │
│  │Google││Azure ││Bedrk ││DIAL  │ │
│  │(6)   ││(4)   ││(8)   ││(2)   │ │
│  └──────┘└──────┘└──────┘└──────┘ │
└───────────────────────────────────┘

```

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface<br/>orchestrator-cli.py]
        API[API Endpoints]
        USER[User Input]
    end
    subgraph "Core Orchestrator"
        ORCH[ModelOrchestrator<br/>Main Routing Engine]
        GUIDE[ModelGuideParser<br/>MODELS.md Rules]
        CONFIG[Configuration<br/>orchestrator_config.yaml]
    end
    subgraph "Task Analysis"
        TASK_TYPE[TaskType Enum<br/>14 Categories]
        TASK_REQ[TaskRequirements<br/>Specifications]
        SCORING[Task Affinity<br/>Scoring Engine]
    end
    subgraph "Model Registry"
        MODEL_CAP[ModelCapabilities<br/>Provider Profiles]
        PROVIDERS[ModelProvider Enum<br/>9 Providers]
        PERF_HIST[Performance History<br/>Tracking]
    end
    subgraph "API Integration Layer"
        API_CLIENTS[API Clients Factory<br/>api_clients.py]
        ANTHROPIC[Anthropic Client]
        OPENAI[OpenAI Client]
        GOOGLE[Google Client]
        XAI[XAI Grok Client]
        LOCAL[Local Ollama Client]
        DIAL[DIAL Client]
        ZEN[Zen MCP Bridge]
    end
    subgraph "Local Model Management"
        LOCAL_MGR[LocalModelManager<br/>local_model_manager.py]
        KEEP_ALIVE[Keep Models Loaded<br/>keep-models-loaded.py]
        RAM_MON[RAM Monitor<br/>ram_monitor.py]
        WARMUP[Warmup Scripts<br/>warmup-models.sh]
    end
    subgraph "Selection Engine"
        SELECT[Model Selection<br/>Algorithm]
        FALLBACK[Fallback Chain<br/>Handler]
        CONSENSUS[Consensus Mode<br/>Multi-Model]
        PARALLEL[Parallel Execution<br/>Engine]
    end
    subgraph "Cost Optimization"
        COST_TRACK[Cost Tracker<br/>Per Model]
        BUDGET[Budget Manager]
        TIER_SELECT[Tier Selection<br/>Quality vs Cost]
    end
    subgraph "Quality & Monitoring"
        QUALITY[Quality Gates]
        METRICS[Performance Metrics]
        LOGGING[Structured Logging]
        BENCH[Benchmarks<br/>benchmarks/]
    end
    subgraph "Testing Framework"
        UNIT[Unit Tests<br/>test_orchestrator.py]
        INTEG[Integration Tests<br/>test_integration.py]
        CONCUR[Concurrent Tests<br/>test_concurrent_models.py]
        REAL[Real World Tests<br/>test_real_world.py]
    end
    USER --> CLI
    CLI --> ORCH
    API --> ORCH
    ORCH --> GUIDE
    ORCH --> CONFIG
    ORCH --> TASK_TYPE
    ORCH --> MODEL_CAP
    ORCH --> SELECT
    GUIDE -.->|Rules & Constraints| SELECT
    CONFIG -.->|Settings| ORCH
    TASK_TYPE --> TASK_REQ
    TASK_REQ --> SCORING
    SCORING --> SELECT
    MODEL_CAP --> PROVIDERS
    MODEL_CAP -.->|Profiles| SELECT
    PERF_HIST -.->|History| SELECT
    SELECT --> FALLBACK
    SELECT --> CONSENSUS
    SELECT --> PARALLEL
    SELECT --> COST_TRACK
    FALLBACK --> API_CLIENTS
    CONSENSUS --> API_CLIENTS
    PARALLEL --> API_CLIENTS
    API_CLIENTS --> ANTHROPIC
    API_CLIENTS --> OPENAI
    API_CLIENTS --> GOOGLE
    API_CLIENTS --> XAI
    API_CLIENTS --> LOCAL
    API_CLIENTS --> DIAL
    API_CLIENTS --> ZEN
    LOCAL --> LOCAL_MGR
    LOCAL_MGR --> KEEP_ALIVE
    LOCAL_MGR --> RAM_MON
    LOCAL_MGR --> WARMUP
    COST_TRACK --> BUDGET
    BUDGET --> TIER_SELECT
    TIER_SELECT -.->|Adjust| SELECT
    ORCH --> QUALITY
    QUALITY --> METRICS
    METRICS --> LOGGING
    METRICS -.->|Feedback| PERF_HIST
    BENCH -.->|Validation| QUALITY
    UNIT -.->|Verify| ORCH
    INTEG -.->|Verify| API_CLIENTS
    CONCUR -.->|Verify| PARALLEL
    REAL -.->|Verify| SELECT
    style ORCH fill:#4a90e2,stroke:#2c5aa0,stroke-width:3px,color:#fff
    style SELECT fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    style API_CLIENTS fill:#2ecc71,stroke:#27ae60,stroke-width:2px,color:#fff
    style QUALITY fill:#f39c12,stroke:#e67e22,stroke-width:2px,color:#fff

```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Orchestrator
    participant Guide as ModelGuideParser
    participant Selector as Selection Engine
    participant API as API Clients
    participant Provider as Model Provider
    participant Monitor as Quality Monitor
    User->>CLI: Submit Task
    CLI->>Orchestrator: Process Request
    Orchestrator->>Guide: Load MODELS.md Rules
    Guide-->>Orchestrator: Task Mappings & Constraints
    Orchestrator->>Orchestrator: Parse Task Requirements
    Orchestrator->>Selector: Request Model Selection
    Selector->>Selector: Score All Models
    Selector->>Selector: Apply Cost Constraints
    Selector->>Selector: Check Availability
    Selector->>Selector: Apply Guide Rules
    Selector-->>Orchestrator: Selected Model(s)
    Orchestrator->>API: Route to Provider Client
    API->>Provider: Execute Query
    Provider-->>API: Response
    API-->>Orchestrator: Formatted Response
    Orchestrator->>Monitor: Track Performance
    Monitor->>Monitor: Update Metrics
    Monitor->>Monitor: Track Cost
    Monitor-->>Orchestrator: Quality Score
    Orchestrator-->>CLI: Result
    CLI-->>User: Formatted Output
    alt Fallback Required
        Provider-->>API: Error/Timeout
        API->>Orchestrator: Failure Signal
        Orchestrator->>Selector: Request Fallback
        Selector-->>Orchestrator: Fallback Model
        Orchestrator->>API: Retry with Fallback
    end
    alt Consensus Mode
        Orchestrator->>API: Query Model A
        Orchestrator->>API: Query Model B
        Orchestrator->>API: Query Model C
        API-->>Orchestrator: Response A
        API-->>Orchestrator: Response B
        API-->>Orchestrator: Response C
        Orchestrator->>Orchestrator: Synthesize Consensus
    end

```

## Model Selection Decision Tree

```mermaid

graph TD
    START[Task Input] --> PARSE[Parse Task Type & Requirements]
    PARSE --> GUIDE{Check MODELS.md<br/>Rules}
    GUIDE -->|Blocked Model| FILTER1[Remove Blocked Models]
    GUIDE -->|Recommended Models| FILTER2[Prioritize Recommended]
    GUIDE -->|No Rules| SCORE
    FILTER1 --> SCORE[Score All Models]
    FILTER2 --> SCORE
    SCORE --> REQ{Meets<br/>Requirements?}
    REQ -->|Context Window| CHECK1[Filter by Context]
    REQ -->|Vision Required| CHECK2[Filter by Vision]
    REQ -->|Function Calling| CHECK3[Filter by Functions]
    REQ -->|Reasoning| CHECK4[Filter by Reasoning]
    CHECK1 --> COST{Within<br/>Budget?}
    CHECK2 --> COST
    CHECK3 --> COST
    CHECK4 --> COST
    COST -->|Yes| AVAIL{Available?}
    COST -->|No| FALLBACK1[Use Lower Cost Alternative]
    AVAIL -->|Yes| QUALITY{Meets Quality<br/>Threshold?}
    AVAIL -->|No| FALLBACK2[Use Fallback Chain]
    QUALITY -->|Yes| SELECT[Select Top Model]
    QUALITY -->|No| CONSENSUS[Use Consensus Mode]
    FALLBACK1 --> SELECT
    FALLBACK2 --> SELECT
    CONSENSUS --> SELECT
    SELECT --> EXECUTE[Execute Query]
    EXECUTE --> MONITOR[Monitor & Track]
    MONITOR --> RESULT[Return Result]
    style START fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style SELECT fill:#2ecc71,stroke:#27ae60,stroke-width:3px,color:#fff
    style EXECUTE fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    style RESULT fill:#9b59b6,stroke:#8e44ad,stroke-width:2px,color:#fff

```
