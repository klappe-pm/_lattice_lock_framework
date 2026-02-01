---
title: mcp
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-mcp-001]
tags: [cli, mcp, server, protocol]
---

# cmd_mcp

## lattice mcp

Start MCP (Model Context Protocol) server to expose Lattice context to AI agents. Enables programmatic access to schema information, validation, and framework operations.

```bash
lattice mcp [OPTIONS]
```

**Basic Examples:**

```bash
# Start MCP server with default transport
lattice mcp
```

```bash
# Use stdio transport
lattice mcp --transport stdio
```

```bash
# Use SSE transport
lattice mcp --transport sse
```

#### --transport

Transport protocol: stdio, sse, websocket.

```bash
# Standard IO transport (default)
lattice mcp --transport stdio
```

```bash
# Server-Sent Events transport
lattice mcp --transport sse
```

```bash
# WebSocket transport
lattice mcp --transport websocket
```

**Use Cases:**
- AI agent integration
- IDE extensions
- Automated tooling
- Remote schema access
- Context provisioning for LLMs

### Process Flow Diagrams: lattice mcp

#### Decision Flow: Server Initialization
This diagram shows how the MCP server initializes based on transport type. Use this to understand server startup and protocol selection.

```mermaid
graph TD
    A[Start MCP Server] --> B[Load Configuration]
    B --> C[Parse Transport Option]
    C --> D{Transport Type}
    D -->|stdio| E[Setup stdio handlers]
    D -->|sse| F[Initialize HTTP server]
    D -->|websocket| G[Initialize WS server]
    E --> H[Register Capabilities]
    F --> I[Configure CORS]
    G --> J[Setup Connection Handler]
    I --> H
    J --> H
    H --> K[Load Schema]
    K --> L[Register Tools]
    L --> M[Register Resources]
    M --> N{Ready?}
    N -->|Yes| O[Start Listening]
    N -->|No| P[Error: Setup failed]
    O --> Q[Accept Connections]
```

#### Sequence Flow: Client-Server Interaction
This diagram illustrates a typical interaction between an MCP client and the Lattice server. Use this to understand request-response patterns.

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as Lattice MCP Server
    participant Schema as Schema Manager
    participant Validator as Validator
    
    Client->>Server: Connect transport
    Server-->>Client: Capabilities
    Client->>Server: List Resources
    Server->>Schema: Get schema files
    Schema-->>Server: Resource list
    Server-->>Client: Available resources
    Client->>Server: Read Resource lattice yaml
    Server->>Schema: Load schema
    Schema-->>Server: Schema content
    Server-->>Client: Schema data
    Client->>Server: Call Tool validate
    Server->>Validator: Run validation
    Validator-->>Server: Results
    Server-->>Client: Validation output
    Client->>Server: Disconnect
    Server-->>Client: Goodbye
```

#### Data Flow: Context Provisioning
This diagram shows how Lattice context flows from the framework to connected clients. Use this when understanding what data is exposed through MCP.

```mermaid
graph LR
    A[Lattice Project] --> B[Schema Files]
    A --> C[Validation Rules]
    A --> D[Entity Definitions]
    B --> E[MCP Server]
    C --> E
    D --> E
    E --> F[Resources API]
    E --> G[Tools API]
    F --> H[Schema Resources]
    F --> I[Config Resources]
    G --> J[Validate Tool]
    G --> K[Generate Tool]
    G --> L[Query Tool]
    H --> M[MCP Client]
    I --> M
    J --> M
    K --> M
    L --> M
```

#### Detailed Flowchart: Transport Selection
This flowchart details the differences between transport protocols and their use cases. Use this to choose the appropriate transport for your integration.

```mermaid
flowchart TD
    A[Select Transport] --> B{Use Case}
    B -->|CLI Tool| C[stdio]
    B -->|Web App| D[SSE or WebSocket]
    B -->|IDE Plugin| E[stdio or WebSocket]
    C --> F[Single Process]
    D --> G{Real-time Updates?}
    E --> H{Long-running?}
    G -->|Yes| I[WebSocket]
    G -->|No| J[SSE]
    H -->|Yes| K[WebSocket]
    H -->|No| L[stdio]
    F --> M[Start Server]
    I --> N[Start WS Server]
    J --> O[Start SSE Server]
    K --> N
    L --> M
```

#### State Diagram: Connection Lifecycle
This state diagram shows the lifecycle of an MCP client connection. Use this to understand connection management and error handling.

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: Client connects
    Connecting --> Handshake: Transport established
    Handshake --> Active: Capabilities exchanged
    Active --> Processing: Request received
    Processing --> Active: Response sent
    Active --> Idle: No activity
    Idle --> Active: Request received
    Active --> Error: Exception occurred
    Error --> Active: Recoverable
    Error --> Disconnected: Fatal error
    Active --> Disconnecting: Client disconnect
    Disconnecting --> Disconnected: Cleanup complete
    Disconnected --> [*]
```
