---
title: chain
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-chain-001]
tags: [cli, chain, pipeline, workflow]
---

# cmd_chain

## lattice chain

Manages and executes multi-step AI model pipelines where outputs from one model feed into inputs for subsequent models. Enables complex workflows defined in YAML with support for pipeline resumption, execution history, and detailed cost tracking.

### lattice chain run

Execute a new pipeline from a YAML definition file with optional input parameters.

```bash
lattice chain run PIPELINE_YAML [OPTIONS]
```

**Basic Examples:**

```bash
# Execute a pipeline from YAML
lattice chain run pipeline.yaml
```

```bash
# Execute a different pipeline
lattice chain run research_workflow.yaml
```

```bash
# Execute with verbose output
lattice chain run pipeline.yaml --verbose
```

#### --input, -i

Provide input parameters as key=value pairs. Can be specified multiple times.

```bash
# Single input parameter
lattice chain run pipeline.yaml --input query="AI safety"
```

```bash
# Multiple input parameters
lattice chain run pipeline.yaml --input query="AI safety" --input depth="detailed" --input format="markdown"
```

```bash
# Using short form
lattice chain run pipeline.yaml -i model="gpt-4" -i temperature="0.7"
```

#### --input-json, -j

Path to a JSON file containing input parameters.

```bash
# Load inputs from JSON file
lattice chain run pipeline.yaml --input-json inputs.json
```

```bash
# Combine JSON inputs with CLI overrides
lattice chain run pipeline.yaml --input-json inputs.json --input priority="high"
```

```bash
# Use JSON file from specific path
lattice chain run pipeline.yaml -j /path/to/config/inputs.json
```

### lattice chain resume

Resume a failed or paused pipeline from the last successful step.

```bash
lattice chain resume [OPTIONS]
```

**Basic Examples:**

```bash
# Resume using pipeline ID only
lattice chain resume --id run_abc123
```

```bash
# Resume with YAML reference
lattice chain resume --yaml pipeline.yaml
```

```bash
# Resume with both ID and YAML
lattice chain resume --id run_abc123 --yaml pipeline.yaml
```

#### --id

Pipeline ID to resume from previous execution.

```bash
# Resume by pipeline ID
lattice chain resume --id run_abc123
```

```bash
# Resume with custom ID format
lattice chain resume --id pipeline_2024_01_15_001
```

```bash
# Resume specific run
lattice chain resume --id run_chk92xyz
```
#### --yaml

Original pipeline YAML file (optional if ID is known).

```bash
# Resume with YAML file
lattice chain resume --yaml pipeline.yaml
```

```bash
# Resume with YAML from specific path
lattice chain resume --yaml /path/to/pipelines/workflow.yaml
```

```bash
# Resume with YAML and ID for validation
lattice chain resume --id run_abc123 --yaml pipeline.yaml
```

#### --input, -i

New input parameter overrides for resumed pipeline.

```bash
# Resume with single input override
lattice chain resume --id run_abc123 --input retry="true"
```

```bash
# Resume with multiple overrides
lattice chain resume --id run_abc123 --input model="gpt-4" --input temperature="0.7"
```

```bash
# Resume with input from CLI
lattice chain resume --yaml pipeline.yaml -i debug="true" -i max_retries="5"
```

### lattice chain history

Show pipeline execution history with status and timing information.

```bash
lattice chain history [OPTIONS]
```

**Basic Examples:**

```bash
# View default history (last 10 runs)
lattice chain history
```

```bash
# View with custom limit
lattice chain history --limit 20
```

```bash
# View minimal history
lattice chain history --limit 5
```

#### --limit

Number of pipeline runs to display.

```bash
# Show last 20 runs
lattice chain history --limit 20
```

```bash
# Show last 50 runs for detailed review
lattice chain history --limit 50
```

```bash
# Show only most recent 3 runs
lattice chain history --limit 3
```

**Use Cases:**
- Multi-step reasoning tasks requiring different model strengths
- Automated research pipelines (gather, analyze, synthesize)
- Content generation pipelines (generate, refine, format)
- Data processing workflows with specialized models
- Fault-tolerant workflows with resumption capability

### Process Flow Diagrams: lattice chain

#### Decision Flow: Pipeline Execution Modes
This diagram shows the three main chain command modes: run, resume, and history. Use this to understand the different execution paths and when to use each mode.

```mermaid
graph TD
    A[Start Chain] --> B{Command Type}
    B -->|run| C[Load Pipeline YAML]
    B -->|resume| D[Load Pipeline State]
    B -->|history| E[Display History]
    C --> F[Parse Inputs]
    D --> F
    F --> G[Execute First Step]
    G --> H{More Steps?}
    H -->|Yes| I[Execute Next Step]
    I --> J{Success?}
    J -->|Yes| H
    J -->|No| K[Save State]
    K --> L[Error Report]
    H -->|No| M[Aggregate Results]
    M --> N[Calculate Costs]
    N --> O[Display Summary]
    E --> P[Query History DB]
    P --> Q[Format Results]
```

#### Sequence Flow: Multi-Step Pipeline Execution
This sequence diagram illustrates how pipeline steps are executed sequentially with output chaining. Follow this to see how results from one model feed into the next step.

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as Chain Command
    participant O as Orchestrator
    participant M1 as Model 1
    participant M2 as Model 2
    participant M3 as Model 3

    U->>CLI: lattice chain run pipeline.yaml
    CLI->>O: Load pipeline
    O->>O: Parse steps
    O->>M1: Execute step 1
    M1-->>O: Result 1
    O->>M2: Execute step 2 with Result 1
    M2-->>O: Result 2
    O->>M3: Execute step 3 with Result 2
    M3-->>O: Result 3
    O->>O: Aggregate results
    O-->>CLI: Pipeline complete
    CLI-->>U: Display summary
```

#### Detailed Flowchart: Step-by-Step Pipeline Processing
This flowchart details the iterative execution of pipeline steps with error handling. Reference this when building fault-tolerant pipelines or implementing resumption logic.

```mermaid
flowchart TD
    Start([lattice chain run]) --> LoadYAML[Load Pipeline YAML]
    LoadYAML --> ParseSteps[Parse Steps]
    ParseSteps --> PrepareInputs[Prepare Inputs]
    PrepareInputs --> StepLoop{For each step}
    StepLoop --> ExecuteStep[Execute Step]
    ExecuteStep --> CheckSuccess{Success?}
    CheckSuccess -->|No| SaveState[Save State]
    SaveState --> ReportError[Report Error]
    ReportError --> Exit1([Exit 1])
    CheckSuccess -->|Yes| StoreResult[Store Result]
    StoreResult --> MoreSteps{More steps?}
    MoreSteps -->|Yes| StepLoop
    MoreSteps -->|No| CalculateCosts[Calculate Total Cost]
    CalculateCosts --> DisplaySummary[Display Summary]
    DisplaySummary --> DisplayResults[Display Results]
    DisplayResults --> Exit0([Exit 0])
```

#### State Diagram: Pipeline Execution States
This state diagram shows the states during pipeline execution with failure handling. Use this to track pipeline progress and understand when state is saved for resumption.

```mermaid
stateDiagram-v2
    [*] --> Loading: Start Pipeline
    Loading --> Executing: Pipeline Loaded
    Executing --> Step1
    Step1 --> Step2: Success
    Step2 --> Step3: Success
    Step3 --> Completed: Success
    Step1 --> Failed: Error
    Step2 --> Failed: Error
    Step3 --> Failed: Error
    Failed --> Saved: State Saved
    Completed --> Reporting: Generate Report
    Saved --> [*]
    Reporting --> [*]
```

#### Data Flow: Result Chaining Through Steps
This data flow shows how results flow through pipeline steps to produce final output with cost tracking. Use this to understand the data transformation pipeline and cost aggregation.

```mermaid
graph LR
    A[Pipeline YAML] --> B[Step 1]
    B --> C[Result 1]
    C --> D[Step 2]
    D --> E[Result 2]
    E --> F[Step 3]
    F --> G[Final Result]
    G --> H[Cost Summary]
```
