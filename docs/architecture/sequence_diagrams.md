# Lattice Lock Framework - Sequence Diagrams

Comprehensive Mermaid.js sequence diagrams for the complex, well-designed components of the Lattice Lock Framework.

---

## Table of Contents

1. [Model Orchestrator - Request Routing](#1-model-orchestrator---request-routing)
2. [Model Orchestrator - Fallback Chain](#2-model-orchestrator---fallback-chain)
3. [Admin API - JWT Authentication Flow](#3-admin-api---jwt-authentication-flow)
4. [Admin API - Token Refresh Flow](#4-admin-api---token-refresh-flow)
5. [Sheriff - AST Validation Pipeline](#5-sheriff---ast-validation-pipeline)
6. [Dashboard - WebSocket Real-Time Updates](#6-dashboard---websocket-real-time-updates)
7. [Dashboard - Project Status Update with Broadcast](#7-dashboard---project-status-update-with-broadcast)
8. [Prompt Architect - Orchestration Pipeline](#8-prompt-architect---orchestration-pipeline)
9. [Checkpoint/Rollback - State Management](#9-checkpointrollback---state-management)
10. [Error Handling - Boundary with Retry](#10-error-handling---boundary-with-retry)

---

## 1. Model Orchestrator - Request Routing

The core routing flow that analyzes tasks, selects optimal models, and executes requests across 8 AI providers.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Orchestrator as ModelOrchestrator
    participant Tracer as AsyncSpanContext
    participant Analyzer as TaskAnalyzer
    participant Selector as ModelSelector
    participant Registry as ModelRegistry
    participant Pool as ClientPool
    participant Executor as ConversationExecutor
    participant Provider as AI Provider

    Client->>Orchestrator: route_request(prompt, model_id?, task_type?)

    activate Orchestrator
    Orchestrator->>Tracer: Create span context with trace_id
    activate Tracer

    Note over Orchestrator: Stage 1: Task Analysis
    Orchestrator->>Analyzer: analyze_async(prompt)
    activate Analyzer
    Analyzer-->>Analyzer: Analyze complexity, context, capabilities
    Analyzer-->>Orchestrator: TaskRequirements
    deactivate Analyzer

    Note over Orchestrator: Stage 2: Model Selection
    alt model_id provided
        Orchestrator->>Orchestrator: Use specified model
    else LATTICE_DEFAULT_MODEL set
        Orchestrator->>Orchestrator: Use environment override
    else auto-select
        Orchestrator->>Selector: select_best_model(requirements)
        activate Selector
        Selector->>Registry: get_available_models()
        Registry-->>Selector: List[ModelCapability]
        Selector-->>Selector: Score models against requirements
        Selector-->>Orchestrator: selected_model_id
        deactivate Selector
    end

    Orchestrator->>Registry: get_model(selected_model_id)
    Registry-->>Orchestrator: ModelCapability

    Note over Orchestrator: Stage 3: Execution
    Orchestrator->>Pool: get_client(provider)
    activate Pool
    Pool-->>Orchestrator: ProviderClient
    deactivate Pool

    Orchestrator->>Executor: execute(model_cap, client, messages)
    activate Executor
    Executor->>Provider: API Request
    Provider-->>Executor: API Response
    Executor->>Executor: Track cost & usage
    Executor-->>Orchestrator: APIResponse
    deactivate Executor

    deactivate Tracer
    Orchestrator-->>Client: APIResponse
    deactivate Orchestrator
```

---

## 2. Model Orchestrator - Fallback Chain

Error handling with intelligent fallback to alternative models when the primary model fails.

```mermaid
sequenceDiagram
    autonumber
    participant Orchestrator as ModelOrchestrator
    participant Selector as ModelSelector
    participant Registry as ModelRegistry
    participant Pool as ClientPool
    participant Executor as ConversationExecutor
    participant Provider1 as Primary Provider
    participant Provider2 as Fallback Provider 1
    participant Provider3 as Fallback Provider 2

    Note over Orchestrator: Primary Model Failed
    Orchestrator->>Selector: get_fallback_chain(requirements, failed_model)
    activate Selector
    Selector->>Registry: Get compatible models
    Selector-->>Selector: Filter by availability & capabilities
    Selector-->>Orchestrator: [model_id_1, model_id_2, ...]
    deactivate Selector

    loop For each fallback model
        Orchestrator->>Registry: get_model(fallback_id)
        Registry-->>Orchestrator: ModelCapability

        Orchestrator->>Pool: get_client(provider)
        activate Pool
        Pool-->>Orchestrator: ProviderClient
        deactivate Pool

        alt Fallback 1 - Provider Unavailable
            Orchestrator->>Provider2: API Request
            Provider2--xOrchestrator: ProviderUnavailableError
            Note over Orchestrator: Log warning, continue to next
        else Fallback 2 - Success
            Orchestrator->>Executor: execute(model_cap, client, messages)
            activate Executor
            Executor->>Provider3: API Request
            Provider3-->>Executor: API Response
            Executor-->>Orchestrator: APIResponse (success)
            deactivate Executor
            Note over Orchestrator: Return successful response
        else All Fallbacks Exhausted
            Orchestrator-->>Orchestrator: Collect failed attempts
            Note over Orchestrator: RuntimeError with detailed message
        end
    end
```

---

## 3. Admin API - JWT Authentication Flow

Complete login flow with OAuth2 password grant, JWT token generation, and role-based access.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant FastAPI as FastAPI App
    participant Middleware as Request Logger
    participant AuthService as Auth Service
    participant UserStore as User Authentication
    participant TokenService as Token Service
    participant Config as AuthConfig

    Client->>FastAPI: POST /api/v1/auth/token (username, password)

    activate FastAPI
    FastAPI->>Middleware: Process request
    activate Middleware
    Middleware-->>Middleware: Generate/extract trace_id
    Middleware->>Middleware: Log request start

    FastAPI->>AuthService: login_for_access_token(form_data)
    activate AuthService

    AuthService->>UserStore: authenticate_user(username, password)
    activate UserStore

    alt Invalid Credentials
        UserStore-->>AuthService: None
        AuthService-->>FastAPI: HTTPException 401
        FastAPI-->>Client: 401 Unauthorized
    else Valid Credentials
        UserStore-->>AuthService: User(username, role)
        deactivate UserStore

        AuthService->>Config: get_config()
        Config-->>AuthService: AuthConfig

        AuthService->>TokenService: create_access_token(username, role)
        activate TokenService
        TokenService-->>TokenService: Encode JWT with expiry
        TokenService-->>AuthService: access_token
        deactivate TokenService

        AuthService->>TokenService: create_refresh_token(username, role)
        activate TokenService
        TokenService-->>TokenService: Encode JWT (longer expiry)
        TokenService-->>AuthService: refresh_token
        deactivate TokenService

        AuthService-->>FastAPI: TokenResponse
        deactivate AuthService
    end

    Middleware->>Middleware: Log response (duration)
    Middleware-->>FastAPI: Add X-Trace-ID header
    deactivate Middleware

    FastAPI-->>Client: TokenResponse {access_token, refresh_token, expires_in}
    deactivate FastAPI
```

---

## 4. Admin API - Token Refresh Flow

Secure token refresh mechanism for maintaining authenticated sessions.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant FastAPI as FastAPI App
    participant AuthService as Auth Service
    participant TokenService as Token Service
    participant Config as AuthConfig

    Client->>FastAPI: POST /api/v1/auth/refresh {refresh_token}

    activate FastAPI
    FastAPI->>AuthService: refresh_access_token(refresh_token)
    activate AuthService

    AuthService->>TokenService: verify_token(refresh_token, "refresh")
    activate TokenService

    alt Invalid/Expired Token
        TokenService-->>AuthService: HTTPException
        AuthService-->>FastAPI: HTTPException 401
        FastAPI-->>Client: 401 Invalid or expired refresh token
    else Valid Token
        TokenService-->>AuthService: TokenData(sub, role)
        deactivate TokenService

        AuthService->>Config: get_config()
        Config-->>AuthService: AuthConfig

        AuthService->>TokenService: create_access_token(sub, role)
        activate TokenService
        TokenService-->>TokenService: Generate new JWT
        TokenService-->>AuthService: new_access_token
        deactivate TokenService

        Note over AuthService: refresh_token not reissued<br/>(single-use pattern)

        AuthService-->>FastAPI: TokenResponse
        deactivate AuthService

        FastAPI-->>Client: TokenResponse {access_token, expires_in}
    end
    deactivate FastAPI
```

---

## 5. Sheriff - AST Validation Pipeline

Static analysis engine that parses Python files into AST and validates against configurable rules.

```mermaid
sequenceDiagram
    autonumber
    participant CLI as CLI/Script
    participant Sheriff as run_sheriff()
    participant FeatureFlag as Feature Flags
    participant Config as SheriffConfig
    participant FileSystem as File System
    participant Validator as validate_file_with_audit
    participant Parser as AST Parser
    participant Visitor as SheriffVisitor
    participant Rules as Rule Engine
    participant Result as SheriffResult

    CLI->>Sheriff: run_sheriff(target_path, config)

    activate Sheriff
    Sheriff->>FeatureFlag: is_feature_enabled(SHERIFF)

    alt Feature Disabled
        FeatureFlag-->>Sheriff: False
        Sheriff-->>CLI: Empty SheriffResult
    else Feature Enabled
        FeatureFlag-->>Sheriff: True

        Sheriff->>Config: Create SheriffConfig
        Note over Config: forbidden_imports<br/>enforce_type_hints<br/>custom_rules

        Sheriff->>FileSystem: resolve_under_root(path)
        FileSystem-->>Sheriff: Validated path

        Sheriff->>FileSystem: Collect *.py files
        Note over FileSystem: Exclude __pycache__, .git,<br/>.venv, build, dist
        FileSystem-->>Sheriff: List[Path]

        Sheriff->>Result: Create SheriffResult()

        loop For each Python file
            Sheriff->>Validator: validate_file_with_audit(file, config)
            activate Validator

            Validator->>FileSystem: Read file content
            FileSystem-->>Validator: source_code

            Validator->>Parser: ast.parse(content, filename)
            activate Parser

            alt Syntax Error
                Parser-->>Validator: SyntaxError
                Validator-->>Sheriff: [Violation(SyntaxError)]
            else Parse Success
                Parser-->>Validator: AST Tree
                deactivate Parser

                Validator->>Visitor: SheriffVisitor(file, config, content)
                activate Visitor
                Visitor->>Visitor: visit(tree)

                Note over Visitor: Walk AST nodes

                loop For each node
                    Visitor->>Rules: Check imports
                    Visitor->>Rules: Check type hints
                    Visitor->>Rules: Check custom rules

                    alt Violation Found
                        Rules-->>Visitor: Violation
                        Visitor->>Visitor: Add to violations list
                    end
                end

                Visitor-->>Validator: (violations, ignored_violations)
                deactivate Visitor
                Validator-->>Sheriff: (violations, ignored)
            end
            deactivate Validator

            Sheriff->>Result: Add violations, increment files_checked
        end

        Sheriff-->>CLI: SheriffResult {violations, files_checked, passed}
    end
    deactivate Sheriff
```

---

## 6. Dashboard - WebSocket Real-Time Updates

WebSocket connection lifecycle with heartbeat, message handling, and automatic cleanup.

```mermaid
sequenceDiagram
    autonumber
    participant Browser as Browser Client
    participant FastAPI as FastAPI App
    participant Endpoint as /dashboard/live
    participant Manager as WebSocketManager
    participant Connections as _connections Dict

    Browser->>FastAPI: WebSocket /dashboard/live
    FastAPI->>Endpoint: websocket_endpoint(websocket)
    Endpoint->>Manager: handle_connection(websocket)

    activate Manager
    Manager->>Manager: connect(websocket)
    activate Manager
    Manager->>Browser: websocket.accept()
    Manager->>Connections: Store ConnectionInfo
    Note over Connections: {websocket, connected_at,<br/>last_activity, client_id}
    Manager->>Browser: {"type": "connected", "message": "..."}
    deactivate Manager

    loop Connection Active
        alt Message Received (within timeout)
            Browser->>Manager: receive_text()
            Manager->>Manager: Update last_activity

            alt Ping Message
                Manager->>Manager: _handle_message()
                Manager->>Browser: {"type": "pong"}
            else Subscribe Message
                Manager->>Browser: {"type": "subscribed", "topics": [...]}
            else Other Message
                Manager->>Browser: {"type": "ack"}
            end

        else Timeout (HEARTBEAT_INTERVAL)
            Manager->>Manager: _send_heartbeat()
            Manager->>Browser: {"type": "heartbeat", "timestamp": ...}
        end
    end

    alt Normal Disconnect
        Browser--xManager: WebSocketDisconnect
    else Error
        Note over Manager: Log error
    end

    Manager->>Manager: disconnect(websocket)
    Manager->>Connections: Remove ConnectionInfo
    Note over Manager: Log duration & remaining count
    deactivate Manager
```

---

## 7. Dashboard - Project Status Update with Broadcast

REST API update that triggers WebSocket broadcast to all connected clients.

```mermaid
sequenceDiagram
    autonumber
    participant Client as REST Client
    participant FastAPI as FastAPI App
    participant Router as Dashboard Router
    participant Aggregator as DataAggregator
    participant WSManager as WebSocketManager
    participant WS1 as WebSocket Client 1
    participant WS2 as WebSocket Client 2
    participant WS3 as WebSocket Client 3

    Client->>FastAPI: POST /dashboard/projects/{id}
    Note over Client: {status, details, duration}

    activate FastAPI
    FastAPI->>Router: update_project(project_id, request_body)
    activate Router

    Router->>Aggregator: update_project_status(...)
    activate Aggregator
    Aggregator-->>Aggregator: Update project state
    Aggregator-->>Aggregator: Recalculate health_score
    Aggregator-->>Router: ProjectInfo
    deactivate Aggregator

    Router->>WSManager: broadcast_event("project_update", data, project_id)
    activate WSManager

    Note over WSManager: Build message with timestamp

    par Parallel Broadcast
        WSManager->>WS1: send_json(message)
        WS1-->>WSManager: Success
    and
        WSManager->>WS2: send_json(message)
        WS2-->>WSManager: Success
    and
        WSManager->>WS3: send_json(message)
        WS3--xWSManager: Connection Error
        Note over WSManager: Mark as dead connection
    end

    WSManager-->>WSManager: Remove dead connections
    WSManager-->>Router: sent_count: 2
    deactivate WSManager

    Router-->>FastAPI: ProjectResponse
    deactivate Router

    FastAPI-->>Client: ProjectResponse {id, status, health_score, ...}
    deactivate FastAPI
```

---

## 8. Prompt Architect - Orchestration Pipeline

Four-stage pipeline that generates prompts from specifications and roadmaps with retry logic.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Orchestrator as PromptOrchestrator
    participant State as OrchestrationState
    participant Agent as PromptArchitectAgent
    participant SpecAnalyzer as Spec Analyzer
    participant RoadmapParser as Roadmap Parser
    participant ToolMatcher as Tool Matcher
    participant PromptGen as Prompt Generator
    participant FileSystem as File System

    Client->>Orchestrator: orchestrate_prompt_generation(spec_path, roadmap_path, ...)

    activate Orchestrator
    Orchestrator->>Orchestrator: reset()
    Orchestrator->>State: Initialize OrchestrationState
    Note over State: 4 PipelineStages: pending

    rect rgb(240, 248, 255)
        Note over Orchestrator: Stage 1: Specification Analysis
        Orchestrator->>State: stages["spec_analysis"].status = "running"

        alt from_project
            Orchestrator->>Orchestrator: _discover_spec_from_project()
        end

        Orchestrator->>FileSystem: Validate spec_path exists

        loop Retry (max_retries)
            Orchestrator->>Agent: invoke_spec_analyzer(spec_path)
            activate Agent
            Agent->>SpecAnalyzer: Analyze specification

            alt Success
                SpecAnalyzer-->>Agent: SpecificationAnalysis
                Agent-->>Orchestrator: SpecificationAnalysis
                deactivate Agent
                Note over State: spec_analysis stored
                Orchestrator->>State: status = "completed"
            else Failure & Retries Left
                Agent--xOrchestrator: Exception
                Note over Orchestrator: Sleep, increment retries
            end
        end
    end

    rect rgb(255, 248, 240)
        Note over Orchestrator: Stage 2: Roadmap Parsing
        Orchestrator->>State: stages["roadmap_parsing"].status = "running"

        loop Retry (max_retries)
            Orchestrator->>Agent: invoke_roadmap_parser(roadmap_path)
            activate Agent
            Agent->>RoadmapParser: Parse roadmap
            RoadmapParser-->>Agent: RoadmapStructure
            Agent-->>Orchestrator: RoadmapStructure
            deactivate Agent
            Note over State: roadmap_structure stored
            Orchestrator->>State: status = "completed"
        end
    end

    rect rgb(240, 255, 240)
        Note over Orchestrator: Stage 3: Tool Matching
        Orchestrator->>State: stages["tool_matching"].status = "running"

        Orchestrator->>Orchestrator: _build_task_list(config)
        Note over Orchestrator: Extract tasks from<br/>phases > epics > tasks

        loop Retry (max_retries)
            Orchestrator->>Agent: invoke_tool_matcher(tasks)
            activate Agent
            Agent->>ToolMatcher: Match tasks to tools
            ToolMatcher-->>Agent: List[ToolAssignment]
            Agent-->>Orchestrator: List[ToolAssignment]
            deactivate Agent
            Note over State: tool_assignments stored
            Orchestrator->>State: status = "completed"
        end
    end

    rect rgb(255, 240, 255)
        Note over Orchestrator: Stage 4: Prompt Generation
        Orchestrator->>State: stages["prompt_generation"].status = "running"

        loop For each assignment
            alt Not Dry Run
                Orchestrator->>Orchestrator: _build_context_data(assignment)
                Orchestrator->>Agent: invoke_prompt_generator(assignment, context)
                activate Agent
                Agent->>PromptGen: Generate prompt
                PromptGen-->>Agent: GeneratedPrompt
                Agent-->>Orchestrator: GeneratedPrompt
                deactivate Agent
                Note over State: Append to generated_prompts
            else Dry Run
                Note over Orchestrator: Log "Would generate..."
            end
        end

        Orchestrator->>State: status = "completed"
    end

    Orchestrator->>Orchestrator: _build_result()
    Note over Orchestrator: Calculate metrics,<br/>tool distribution, status

    Orchestrator-->>Client: GenerationResult
    deactivate Orchestrator
```

---

## 9. Checkpoint/Rollback - State Management

Checkpoint creation, file backup, and state restoration system.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Manager as CheckpointManager
    participant Storage as CheckpointStorage
    participant State as RollbackState
    participant FileSystem as File System

    rect rgb(240, 255, 240)
        Note over Client,FileSystem: Create Checkpoint Flow

        Client->>Manager: create_checkpoint(files, config, schema_version, description)
        activate Manager

        Manager->>State: Create RollbackState
        Note over State: timestamp<br/>files (path → hash)<br/>config<br/>schema_version<br/>description

        Manager->>Storage: save_state(state)
        activate Storage
        Storage-->>Storage: Generate checkpoint_id
        Storage-->>Storage: Serialize to JSON
        Storage-->>Storage: Write to storage
        Storage-->>Manager: checkpoint_id
        deactivate Storage

        loop For each file in files
            Manager->>FileSystem: open(filepath, "rb")
            FileSystem-->>Manager: content (bytes)
            Manager->>Storage: save_file_content(checkpoint_id, filepath, content)
            activate Storage
            Storage-->>Storage: Store file backup
            deactivate Storage
        end

        Manager-->>Client: checkpoint_id
        deactivate Manager
    end

    rect rgb(255, 248, 240)
        Note over Client,FileSystem: Restore File Flow

        Client->>Manager: restore_file(checkpoint_id, filepath)
        activate Manager

        Manager->>Storage: load_file_content(checkpoint_id, filepath)
        activate Storage

        alt Backup Found
            Storage-->>Manager: content (bytes)
            deactivate Storage

            Manager->>FileSystem: os.makedirs(dirname, exist_ok=True)
            Manager->>FileSystem: open(filepath, "wb").write(content)

            alt Write Success
                Manager-->>Client: True
            else OSError
                Manager-->>Client: False
            end

        else Backup Not Found
            Storage-->>Manager: None
            deactivate Storage
            Manager-->>Client: False
        end

        deactivate Manager
    end

    rect rgb(248, 240, 255)
        Note over Client,FileSystem: List & Prune Checkpoints

        Client->>Manager: list_checkpoints()
        Manager->>Storage: list_states()
        Storage-->>Manager: [checkpoint_id_1, checkpoint_id_2, ...]
        Manager-->>Client: List[str]

        Client->>Manager: prune_checkpoints(keep_n=5)
        Manager->>Storage: prune_states(5)
        Note over Storage: Delete oldest checkpoints<br/>keeping only last 5
    end
```

---

## 10. Error Handling - Boundary with Retry

Decorator-based error handling with classification, exponential backoff, and fallback.

```mermaid
sequenceDiagram
    autonumber
    participant Caller
    participant Decorator as @error_boundary
    participant Function as Protected Function
    participant Classifier as classify_error()
    participant Metrics as ErrorMetrics
    participant Logger as Logger
    participant RetryConfig as RetryConfig
    participant Fallback as Fallback Function

    Caller->>Decorator: Call decorated function
    activate Decorator

    Note over Decorator: attempt = 0

    loop While attempt <= max_retries
        Decorator->>Function: Execute function(*args, **kwargs)

        alt Success
            Function-->>Decorator: Result
            Decorator-->>Caller: Result
        else Exception Raised
            Function--xDecorator: Exception

            Decorator->>Classifier: classify_error(exception)
            activate Classifier
            Note over Classifier: Determine:<br/>- error_type<br/>- error_code<br/>- severity<br/>- category<br/>- recoverability
            Classifier-->>Decorator: ErrorContext
            deactivate Classifier

            alt track_metrics enabled
                Decorator->>Metrics: record_error(context)
                activate Metrics
                Metrics-->>Metrics: Increment error_counts
                Metrics-->>Metrics: Update error_rates

                alt project_id provided
                    Metrics->>Metrics: _enqueue_persistence()
                    Note over Metrics: Background task:<br/>persist to database
                end

                Metrics->>Metrics: should_alert(context)?
                deactivate Metrics
            end

            alt log_errors enabled
                Decorator->>Logger: _log_error(context)
                Note over Logger: Redact sensitive data<br/>Log with appropriate level
            end

            alt on_error callback provided
                Decorator->>Decorator: on_error(context)
            end

            Note over Decorator: Check recoverability

            alt Is recoverable AND can_retry AND attempt < max_retries
                Decorator->>RetryConfig: get_delay(attempt)
                activate RetryConfig
                Note over RetryConfig: exponential_backoff?<br/>delay = base * 2^attempt<br/>apply jitter
                RetryConfig-->>Decorator: delay_seconds
                deactivate RetryConfig

                Note over Decorator: await asyncio.sleep(delay)
                Note over Decorator: attempt += 1
            else Not recoverable OR max retries reached
                Note over Decorator: Break retry loop
            end
        end
    end

    alt Fallback provided
        Decorator->>Logger: Log "Using fallback..."
        Decorator->>Fallback: fallback(*args, **kwargs)
        Fallback-->>Decorator: Fallback result
        Decorator-->>Caller: Fallback result
    else No fallback
        Decorator--xCaller: Re-raise last_error
    end

    deactivate Decorator
```

---

## Component Quality Assessment

| Component | Complexity | Completeness | Design Quality | Lines |
|-----------|------------|--------------|----------------|-------|
| Model Orchestrator | High | Complete | Excellent | 296 |
| Admin API + Auth | Medium | Complete | Excellent | 365 |
| Sheriff Validation | Medium | Complete | Excellent | 291 |
| Dashboard + WebSocket | High | Complete | Excellent | 860 |
| Prompt Orchestrator | High | Complete | Excellent | 540 |
| Checkpoint Manager | Low | Complete | Good | 127 |
| Error Middleware | High | Complete | Excellent | 554 |

### Design Patterns Identified

- **Factory Pattern**: ModelOrchestrator, create_app()
- **Repository Pattern**: CheckpointStorage, ModelRegistry
- **Decorator Pattern**: error_boundary, handle_errors
- **Pipeline Pattern**: PromptOrchestrator stages
- **Observer Pattern**: WebSocket broadcast
- **Strategy Pattern**: Model selection, fallback chains
- **Context Manager**: ErrorHandler, AsyncSpanContext

---

## Usage

These diagrams are written in Mermaid.js format and can be rendered in:
- GitHub/GitLab Markdown viewers
- VS Code with Mermaid extension
- Obsidian
- Notion
- [Mermaid Live Editor](https://mermaid.live)

To render locally, ensure your markdown viewer supports Mermaid or use a compatible extension.
