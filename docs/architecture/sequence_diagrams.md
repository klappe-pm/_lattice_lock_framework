# Sequence Diagrams

This document provides detailed sequence diagrams for the key workflows in the Lattice-Lock Framework.

## 1. Model Orchestrator Request Routing

This sequence shows how a user request flows through the Model Orchestrator to select and execute on the optimal AI model.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI Interface
    participant Router as Request Router
    participant Analyzer as Task Analyzer
    participant Registry as Model Registry
    participant Scorer as Capability Scorer
    participant Cost as Cost Tracker
    participant Provider as AI Provider

    User->>CLI: orchestrator_cli.py route "prompt" --strategy balanced
    CLI->>CLI: Parse arguments
    CLI->>Router: route_request(prompt, strategy="balanced")
    
    Router->>Analyzer: analyze(prompt)
    Note over Analyzer: Stage 1: Regex Heuristics
    Analyzer->>Analyzer: Check patterns for task type
    
    alt Heuristics confidence > 0.8
        Analyzer-->>Router: TaskType (e.g., CODE_GENERATION)
    else Heuristics uncertain
        Note over Analyzer: Stage 2: LLM Semantic Router
        Analyzer->>Provider: Classify task via LLM
        Provider-->>Analyzer: TaskType classification
        Analyzer-->>Router: TaskType
    end
    
    Router->>Registry: get_models_for_task(task_type)
    Registry-->>Router: List[ModelConfig]
    
    Router->>Scorer: score_models(models, task_type, strategy)
    Note over Scorer: Scoring weights:<br/>Task Affinity: 40%<br/>Performance: 30%<br/>Accuracy: 20%<br/>Cost: 10%
    Scorer-->>Router: RankedModels
    
    Router->>Router: Select top model
    Router->>Cost: estimate_cost(model, prompt_tokens)
    Cost-->>Router: EstimatedCost
    
    Router->>Provider: execute(prompt, model)
    Provider-->>Router: Response
    
    Router->>Cost: record_usage(model, tokens, cost)
    Cost-->>Router: Recorded
    
    Router-->>CLI: FormattedResponse
    CLI-->>User: Display result with model info
```

## 2. Governance Validation Flow

This sequence shows how code is validated against governance rules defined in `lattice.yaml`.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI Interface
    participant Validator as Schema Validator
    participant Compiler as Lattice Compiler
    participant Sheriff as Sheriff (AST)
    participant Gauntlet as Gauntlet (Tests)
    participant FS as File System

    User->>CLI: lattice-lock validate ./project
    CLI->>FS: Read lattice.yaml
    FS-->>CLI: lattice.yaml content
    
    CLI->>Validator: validate_schema(lattice_yaml)
    Validator->>Validator: Parse YAML
    Validator->>Validator: Validate against JSON Schema
    
    alt Schema valid
        Validator-->>CLI: ValidationResult(valid=True)
    else Schema invalid
        Validator-->>CLI: ValidationResult(valid=False, errors=[...])
        CLI-->>User: Display validation errors
        Note over User: Process stops here
    end
    
    CLI->>Compiler: compile(lattice_yaml)
    Compiler->>Compiler: Resolve dependencies
    Compiler->>Compiler: Generate enforcement rules
    Compiler-->>CLI: CompiledRules
    
    CLI->>Sheriff: analyze(project_path, rules)
    Sheriff->>FS: Read source files
    FS-->>Sheriff: Source code
    Sheriff->>Sheriff: Parse AST
    Sheriff->>Sheriff: Apply rules to AST nodes
    
    loop For each source file
        Sheriff->>Sheriff: Check naming conventions
        Sheriff->>Sheriff: Check structure requirements
        Sheriff->>Sheriff: Check security patterns
    end
    
    alt Violations found
        Sheriff-->>CLI: List[Violation]
        CLI-->>User: Display violations with line numbers
    else No violations
        Sheriff-->>CLI: Empty list
    end
    
    CLI->>Gauntlet: generate_tests(rules)
    Gauntlet->>Gauntlet: Parse rule contracts
    Gauntlet->>Gauntlet: Generate test assertions
    Gauntlet->>FS: Write test files
    FS-->>Gauntlet: Tests written
    Gauntlet-->>CLI: GeneratedTests
    
    CLI-->>User: Validation complete
```

## 3. Prompt Architect Workflow

This sequence shows how the Prompt Architect Agent generates optimized prompts from project specifications.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI Interface
    participant Agent as Prompt Architect
    participant Spec as Spec Analyzer
    participant Roadmap as Roadmap Parser
    participant Matcher as Tool Matcher
    participant Generator as Prompt Generator
    participant Quality as Quality Scorer
    participant Router as Model Router

    User->>CLI: generate-prompts --spec spec.md --roadmap roadmap.md
    CLI->>Agent: generate(spec_path, roadmap_path)
    
    Agent->>Spec: analyze(spec_path)
    Spec->>Spec: Parse markdown sections
    Spec->>Spec: Extract requirements
    Spec->>Spec: Identify constraints
    Spec-->>Agent: SpecAnalysis
    
    Agent->>Roadmap: parse(roadmap_path)
    Roadmap->>Roadmap: Extract phases
    Roadmap->>Roadmap: Extract milestones
    Roadmap->>Roadmap: Build dependency graph
    Roadmap-->>Agent: RoadmapStructure
    
    loop For each phase/milestone
        Agent->>Matcher: match_tools(task)
        Matcher->>Matcher: Load tool profiles
        Matcher->>Matcher: Score tool capabilities
        Matcher-->>Agent: MatchedTools
        
        Agent->>Generator: generate_prompt(task, tools, context)
        Generator->>Generator: Select template
        Generator->>Generator: Inject context
        Generator->>Generator: Apply constraints
        Generator-->>Agent: GeneratedPrompt
        
        Agent->>Quality: score(prompt)
        Quality->>Quality: Check structure
        Quality->>Quality: Check completeness
        Quality->>Quality: Check clarity
        
        alt Score >= threshold
            Quality-->>Agent: QualityScore (pass)
        else Score < threshold
            Quality-->>Agent: QualityScore (fail, suggestions)
            Agent->>Generator: regenerate with suggestions
            Generator-->>Agent: ImprovedPrompt
        end
    end
    
    Agent->>Router: validate_prompts(prompts)
    Router-->>Agent: ValidationResults
    
    Agent-->>CLI: GeneratedPrompts
    CLI-->>User: Display prompts with quality scores
```

## 4. Consensus Engine Multi-Model Flow

This sequence shows how the Consensus Engine aggregates responses from multiple AI models.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI Interface
    participant Router as Request Router
    participant Consensus as Consensus Engine
    participant P1 as Provider 1 (OpenAI)
    participant P2 as Provider 2 (Anthropic)
    participant P3 as Provider 3 (Google)
    participant Aggregator as Response Aggregator

    User->>CLI: route "prompt" --consensus --num-models 3
    CLI->>Router: route_with_consensus(prompt, num=3)
    
    Router->>Consensus: create_group(prompt, num_models=3)
    Consensus->>Consensus: Select diverse models
    Note over Consensus: Selects models from<br/>different providers for diversity
    
    par Parallel execution
        Consensus->>P1: execute(prompt, gpt-4o)
        Consensus->>P2: execute(prompt, claude-3-opus)
        Consensus->>P3: execute(prompt, gemini-2.0-pro)
    end
    
    P1-->>Consensus: Response1
    P2-->>Consensus: Response2
    P3-->>Consensus: Response3
    
    Consensus->>Aggregator: aggregate(responses)
    Aggregator->>Aggregator: Extract key points
    Aggregator->>Aggregator: Identify agreements
    Aggregator->>Aggregator: Flag disagreements
    Aggregator->>Aggregator: Calculate confidence
    
    alt High agreement (>80%)
        Aggregator-->>Consensus: ConsensusResult(high_confidence)
    else Medium agreement (50-80%)
        Aggregator-->>Consensus: ConsensusResult(medium_confidence, differences)
    else Low agreement (<50%)
        Aggregator-->>Consensus: ConsensusResult(low_confidence, all_responses)
    end
    
    Consensus-->>Router: ConsensusResult
    Router-->>CLI: FormattedConsensusResponse
    CLI-->>User: Display consensus with confidence level
```

## 5. Error Handling and Rollback Flow

This sequence shows how the framework handles errors and performs rollback operations.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI Interface
    participant Middleware as Error Middleware
    participant Classifier as Error Classifier
    participant Rollback as Rollback Manager
    participant Checkpoint as Checkpoint Storage
    participant Remediation as Remediation Engine

    User->>CLI: Execute operation
    CLI->>Middleware: wrap(operation)
    
    Middleware->>Checkpoint: create_checkpoint(state)
    Checkpoint-->>Middleware: CheckpointID
    
    Middleware->>Middleware: Execute operation
    
    alt Operation succeeds
        Middleware-->>CLI: Success result
        CLI-->>User: Display success
    else Operation fails
        Middleware->>Classifier: classify(error)
        Classifier->>Classifier: Analyze error type
        Classifier->>Classifier: Determine severity
        Classifier-->>Middleware: ErrorClassification
        
        alt Recoverable error
            Middleware->>Remediation: suggest_fix(error)
            Remediation-->>Middleware: RemediationSteps
            Middleware-->>CLI: Error with fix suggestions
            CLI-->>User: Display error and suggestions
        else Critical error
            Middleware->>Rollback: rollback(checkpoint_id)
            Rollback->>Checkpoint: get_checkpoint(id)
            Checkpoint-->>Rollback: SavedState
            Rollback->>Rollback: Restore state
            Rollback-->>Middleware: RollbackComplete
            Middleware-->>CLI: Error with rollback notification
            CLI-->>User: Display error, state rolled back
        end
    end
```

## 6. Dashboard Real-Time Updates

This sequence shows how the Dashboard receives real-time updates via WebSocket.

```mermaid
sequenceDiagram
    autonumber
    participant Browser as Dashboard (Browser)
    participant WS as WebSocket Server
    participant Aggregator as Metrics Aggregator
    participant Cost as Cost Tracker
    participant Router as Request Router

    Browser->>WS: Connect WebSocket
    WS-->>Browser: Connection established
    
    Browser->>WS: Subscribe to metrics
    WS->>Aggregator: register_subscriber(client)
    Aggregator-->>WS: Subscription confirmed
    
    loop Every 5 seconds
        Aggregator->>Cost: get_current_costs()
        Cost-->>Aggregator: CostMetrics
        
        Aggregator->>Router: get_request_stats()
        Router-->>Aggregator: RequestStats
        
        Aggregator->>Aggregator: Compile metrics
        Aggregator->>WS: push_metrics(compiled)
        WS->>Browser: Metrics update (JSON)
        Browser->>Browser: Update charts
    end
    
    Note over Browser: User triggers action
    Browser->>WS: Request detailed report
    WS->>Aggregator: generate_report(time_range)
    Aggregator->>Cost: get_historical_data(range)
    Cost-->>Aggregator: HistoricalData
    Aggregator-->>WS: DetailedReport
    WS->>Browser: Report data
    Browser->>Browser: Render report
```

## Key Decision Points Summary

| Workflow | Decision Point | Options | Default |
|----------|---------------|---------|---------|
| Request Routing | Task classification | Heuristics vs LLM | Heuristics first, LLM fallback |
| Request Routing | Model selection | 63 models across 8 providers | Highest scored model |
| Request Routing | Routing strategy | balanced, cost_optimized, performance, quality | balanced |
| Governance | Validation strictness | error, warning, info | error |
| Governance | Auto-fix | enabled, disabled | disabled |
| Prompt Architect | Quality threshold | 0.0 - 1.0 | 0.7 |
| Consensus | Agreement threshold | 0.0 - 1.0 | 0.8 |
| Error Handling | Rollback trigger | automatic, manual | automatic for critical |
