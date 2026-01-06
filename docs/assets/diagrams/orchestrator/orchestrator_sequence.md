# Sequence Diagram

```mermaid
sequenceDiagram
    %% Standard Class Definitions
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef agent fill:#e0f2f1,stroke:#004d40,stroke-width:2px;
    classDef cli fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5;
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px;

    participant User
    participant CLI as "CLI[cli-index-001]"
    participant Orchestrator as "Orchestrator[mod-orchestrator-001]"
    participant Analyzer
    participant Selector
    participant Registry
    participant Pool
    participant Executor
    participant Provider

    %% Apply Classes
    class CLI cli
    class Orchestrator,Analyzer,Selector,Registry,Pool,Executor core
    class Provider external

    User->>CLI: lattice ask "prompt"
    CLI->>Orchestrator: route_request(prompt)
    Orchestrator->>Analyzer: analyze_async(prompt)
    Analyzer-->>Orchestrator: TaskRequirements(type, complexity)
    
    Orchestrator->>Selector: select_best_model(requirements)
    Selector->>Registry: get_capabilities()
    Selector-->>Orchestrator: model_id

    Orchestrator->>Registry: get_model(model_id)
    Registry-->>Orchestrator: ModelCapabilities

    Orchestrator->>Pool: get_client(provider_name)
    Pool-->>Orchestrator: APIClient

    Orchestrator->>Executor: execute(model, client, messages)
    Executor->>Provider: chat(messages)
    Provider-->>Executor: Response
    Executor-->>Orchestrator: APIResponse
    Orchestrator-->>CLI: APIResponse
    CLI-->>User: Display Output
```
