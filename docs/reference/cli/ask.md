---
title: ask
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-ask-001]
tags: [cli, ask, query, ai_routing]
---

# cmd_ask

## lattice ask

Universal AI query routing that automatically selects the optimal model for any question. Analyzes prompts, determines task type and requirements, and routes requests to best-performing models based on performance metrics, cost efficiency, and task-specific capabilities.

```bash
lattice ask PROMPT [OPTIONS]
```

**Basic Examples:**

```bash
# Simple query with automatic routing
lattice ask "What is the capital of France?"
```

```bash
# Technical query
lattice ask "Explain quantum entanglement"
```

```bash
# Complex analysis query
lattice ask "Analyze this architectural pattern and suggest improvements"
```

#### --model, -m

Force a specific model instead of automatic selection.

```bash
# Use specific Claude model
lattice ask "Explain quantum computing" --model claude-3-5-sonnet
```

```bash
# Use specific GPT model
lattice ask "Write a Python function" --model gpt-4o
```

```bash
# Use local model
lattice ask "Summarize this text" -m llama-3-70b
```

#### --task-type, -t

Override automatic task classification.

```bash
# Force code generation task type
lattice ask "Write a function to sort an array" --task-type CODE_GENERATION
```

```bash
# Force reasoning task type
lattice ask "What are the implications of AGI?" --task-type REASONING
```

```bash
# Force writing task type
lattice ask "Draft an email" -t WRITING
```

#### --compare

Compare responses from multiple top-ranking models.

```bash
# Compare top 3 models
lattice ask "What are the implications of AGI?" --compare
```

```bash
# Compare with complex query
lattice ask "Design a distributed caching system" --compare
```

```bash
# Compare for research
lattice ask "Explain the halting problem" --compare
```

#### --verbose, -v

Show detailed routing metadata and token usage.

```bash
# Show routing details
lattice ask "Analyze this pattern" --verbose
```

```bash
# Show model selection reasoning
lattice ask "What is the best approach?" -v
```

```bash
# Show cost breakdown
lattice ask "Generate documentation" --verbose
```

**Use Cases:**
- Quick AI queries without manual model selection
- Model comparison for quality evaluation
- Cost-optimized routing (simple vs complex tasks)
- Task-specific routing overrides
- Research and benchmarking across models

### Process Flow Diagrams: lattice ask

#### Decision Flow: Query Routing Logic
This diagram shows how the ask command determines which model to use based on user input. Use this to understand the decision points for model selection, comparison mode, and metadata display.

```mermaid
graph TD
    A[User Submits Prompt] --> B{Model Specified?}
    B -->|Yes| C[Use Specified Model]
    B -->|No| D[Analyze Prompt]
    D --> E[Determine Task Type]
    E --> F[Calculate Requirements]
    F --> G[Score All Models]
    G --> H[Select Best Model]
    H --> I{Compare Mode?}
    I -->|Yes| J[Get Top 3 Models]
    I -->|No| K[Execute Single Request]
    J --> L[Execute Parallel Requests]
    L --> M[Display All Responses]
    K --> N[Display Response]
    C --> K
    N --> O{Verbose?}
    O -->|Yes| P[Show Metadata]
    O -->|No| Q[Complete]
    P --> Q
    M --> Q
```

#### Sequence Flow: Model Selection Process
This sequence diagram details the interaction between components during prompt analysis and model scoring. Follow this to see how task requirements are calculated and models are ranked.

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as Ask Command
    participant A as Analyzer
    participant S as Scorer
    participant O as Orchestrator
    participant M as Model API

    U->>CLI: lattice ask "prompt"
    CLI->>A: Analyze prompt
    A->>A: Classify task type
    A->>A: Calculate requirements
    A-->>CLI: TaskRequirements
    CLI->>S: Score models
    loop For each model
        S->>S: Calculate score
    end
    S-->>CLI: Ranked models
    CLI->>O: Route to best model
    O->>M: API request
    M-->>O: Response
    O-->>CLI: ModelResponse
    CLI-->>U: Formatted output
```

#### Data Flow: Analysis to Execution
This data flow shows how a prompt is transformed into requirements, scored across models, and executed. Use this to understand the information flow from user input to model response.

```mermaid
graph LR
    A[Prompt] --> B[Task Analysis]
    B --> C[Task Type]
    B --> D[Context Size]
    B --> E[Special Needs]
    C --> F[Model Scoring]
    D --> F
    E --> F
    F --> G[Best Match]
    G --> H{Execute}
    H --> I[Response]
    I --> J[Usage Stats]
```

#### Detailed Flowchart: Single vs Comparison Mode
This flowchart shows the two execution paths: single model queries and comparison mode. Reference this to understand how compare mode selects and executes multiple models in parallel.

```mermaid
flowchart TD
    Start([lattice ask]) --> CheckMode{Compare Mode?}
    CheckMode -->|No| SinglePath[Single Model Path]
    CheckMode -->|Yes| ComparePath[Comparison Path]
    
    SinglePath --> Analyze[Analyze Prompt]
    Analyze --> Score[Score Models]
    Score --> Select[Select Best]
    Select --> Execute[Execute Request]
    Execute --> Display[Display Response]
    Display --> ShowMeta{Verbose?}
    ShowMeta -->|Yes| Meta[Show Metadata]
    ShowMeta -->|No| End([Complete])
    Meta --> End
    
    ComparePath --> AnalyzeC[Analyze Prompt]
    AnalyzeC --> GetTop[Get Top 3 Models]
    GetTop --> Parallel[Execute in Parallel]
    Parallel --> DisplayAll[Display All Results]
    DisplayAll --> End
```

#### State Diagram: Query Execution States
This state diagram illustrates the lifecycle of a query from receipt to completion. Use this to track the state transitions and identify where errors might occur during execution.

```mermaid
stateDiagram-v2
    [*] --> Received: Prompt Input
    Received --> Analyzing: Start Analysis
    Analyzing --> Scored: Models Scored
    Scored --> Selected: Best Model
    Selected --> Routing: Route Request
    Routing --> Executing: API Call
    Executing --> Success: Response Ready
    Executing --> Failed: Error
    Success --> Formatted: Format Output
    Failed --> ErrorHandler: Handle Error
    ErrorHandler --> [*]
    Formatted --> [*]: Display
```
