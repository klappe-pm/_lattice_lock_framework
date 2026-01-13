# Admin System - Comprehensive Diagram Documentation

Detailed Mermaid.js diagrams documenting the Admin subsystem including Authentication, Telemetry, and Dashboard Architecture.

---

## Table of Contents

1. [Authentication Flow](#1-authentication-flow)
2. [Telemetry Pipeline](#2-telemetry-pipeline)
3. [Admin Dashboard Architecture](#3-admin-dashboard-architecture)

---

## 1. Authentication Flow

**Purpose**: Shows the JWT-based authentication sequence for admin users, from login through token validation on subsequent requests.

**Diagram Type**: Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Admin UI
    participant API as Admin API
    participant DB as Database

    User->>UI: Login (username, password)
    UI->>API: POST /auth/login

    API->>DB: verify_credentials()
    DB-->>API: Valid User

    API->>API: create_access_token()
    API-->>UI: JWT Token

    UI->>UI: Store Token (LocalStorage)

    Note over User, DB: Subsequent Request

    User->>UI: View Dashboard
    UI->>API: GET /projects (Header: Bearer Token)

    API->>API: decode_token()
    alt Valid
        API-->>UI: Data
    else Invalid/Expired
        API-->>UI: 401 Unauthorized
        UI-->>User: Redirect to Login
    end
```

### Node Descriptions

| Node | Description | Implementation |
|------|-------------|----------------|
| **User** | Admin user interacting with the system | Human actor with credentials |
| **Admin UI** | React-based single page application | Vite/TypeScript/Mantine frontend |
| **Admin API** | FastAPI backend server | REST API with JWT authentication |
| **Database** | Persistent storage | Cloud SQL for user credentials |

### Authentication Flow Details

| Step | Action | Security Consideration |
|------|--------|------------------------|
| **Login** | User submits credentials | HTTPS required, rate limiting |
| **Verify** | Database credential check | Bcrypt password hashing |
| **Token Creation** | JWT generation | RS256 signing, configurable expiry |
| **Token Storage** | Client-side storage | LocalStorage with XSS protection |
| **Token Validation** | Decode and verify | Signature verification, expiry check |

### Related Source Files

- [`src/admin/auth/service.py`](../../src/admin/auth/service.py) - JWT token creation and validation (lines 1-100)
- [`src/admin/api.py`](../../src/admin/api.py) - FastAPI routes and middleware (lines 1-265)
- [`src/admin/auth/models.py`](../../src/admin/auth/models.py) - User and token models
- [`src/admin/auth/dependencies.py`](../../src/admin/auth/dependencies.py) - FastAPI dependency injection for auth

---

## 2. Telemetry Pipeline

**Purpose**: Illustrates the observability stack for collecting, processing, and visualizing application metrics, traces, and logs.

**Diagram Type**: Flowchart (Left-Right)

```mermaid
flowchart LR
    classDef source fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef pipe fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef sink fill:#e0f2f1,stroke:#004d40,stroke-width:2px;

    App[Application]:::source --> |Logs/Traces| Collector[OTEL Collector]:::pipe

    Collector --> |Batch| Processor[Batch Processor]:::pipe

    Processor --> |Metrics| Prometheus[Prometheus]:::sink
    Processor --> |Traces| Jaeger[Jaeger]:::sink
    Processor --> |Logs| Loki[Loki]:::sink

    Prometheus --> Grafana[Grafana Dashboard]:::sink
```

### Node Descriptions

| Node | Description | Purpose |
|------|-------------|---------|
| **Application** | Instrumented Python application | Source of telemetry data |
| **OTEL Collector** | OpenTelemetry Collector | Receives and routes telemetry |
| **Batch Processor** | Data batching component | Optimizes data transmission |
| **Prometheus** | Time-series database | Stores and queries metrics |
| **Jaeger** | Distributed tracing platform | Visualizes request traces |
| **Loki** | Log aggregation system | Stores and indexes logs |
| **Grafana Dashboard** | Visualization platform | Unified observability UI |

### Telemetry Data Types

| Type | Description | Storage |
|------|-------------|---------|
| **Metrics** | Numeric measurements (latency, throughput, errors) | Prometheus TSDB |
| **Traces** | Distributed request traces with spans | Jaeger backend |
| **Logs** | Structured application logs | Loki with label indexing |

### Configuration

```yaml
# Example OTEL configuration
exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  jaeger:
    endpoint: "jaeger:14250"
  loki:
    endpoint: "loki:3100"
```

### Related Source Files

- [`src/admin/telemetry/`](../../src/admin/telemetry/) - Telemetry module
- [`src/admin/telemetry/metrics.py`](../../src/admin/telemetry/metrics.py) - Prometheus metrics definitions
- [`src/admin/telemetry/tracing.py`](../../src/admin/telemetry/tracing.py) - OpenTelemetry tracing setup
- [`docker-compose.yaml`](../../docker-compose.yaml) - Container orchestration with observability stack

---

## 3. Admin Dashboard Architecture

**Purpose**: C4 Container diagram showing the high-level architecture of the Admin Dashboard system with frontend, backend, and data layers.

**Diagram Type**: C4 Container Diagram

```mermaid
C4Container
    title Admin Dashboard Architecture

    Container(browser, "Browser", "Chrome/Firefox")

    System_Boundary(frontend, "Frontend App") {
        Container(react, "React App", "Vite/TS/Mantine", "Single Page Application")
        Container(store, "State Store", "Zustand", "Client-side state")
    }

    System_Boundary(backend, "Admin API") {
        Container(api, "FastAPI Server[api-admin-001]", "Python", "REST API")
        Container(socket, "WebSocket Manager", "Python", "Real-time updates")
        Container(auth, "Auth Service", "JWT/OAuth", "Security")
    }

    ContainerDb(db, "Database", "Cloud SQL", "Persistence")

    Rel(browser, react, "Loads")
    Rel(react, api, "REST Requests")
    Rel(react, socket, "WS Connection (State Sync)")
    Rel(api, db, "Query/Update")
    Rel(api, auth, "Validate Token")
```

### Container Descriptions

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| **Browser** | Chrome/Firefox | User's web browser |
| **React App** | Vite + TypeScript + Mantine | SPA with component library |
| **State Store** | Zustand | Lightweight state management |
| **FastAPI Server** | Python + FastAPI | REST API endpoints |
| **WebSocket Manager** | Python asyncio | Real-time bidirectional communication |
| **Auth Service** | JWT + OAuth | Authentication and authorization |
| **Database** | Cloud SQL (PostgreSQL) | Persistent data storage |

### Communication Patterns

| Pattern | Protocol | Use Case |
|---------|----------|----------|
| **REST API** | HTTP/HTTPS | CRUD operations, data fetching |
| **WebSocket** | WS/WSS | Real-time updates, notifications |
| **Token Auth** | Bearer JWT | Stateless authentication |

### Frontend State Management

```typescript
// Zustand store structure
interface AdminStore {
  user: User | null;
  projects: Project[];
  notifications: Notification[];
  setUser: (user: User) => void;
  fetchProjects: () => Promise<void>;
}
```

### Related Source Files

- [`src/admin/api.py`](../../src/admin/api.py) - FastAPI application factory (lines 1-265)
- [`src/dashboard/websocket.py`](../../src/dashboard/websocket.py) - WebSocket connection manager (lines 1-364)
- [`src/admin/auth/service.py`](../../src/admin/auth/service.py) - Authentication service
- [`frontend/src/`](../../frontend/src/) - React application source
- [`frontend/src/stores/`](../../frontend/src/stores/) - Zustand state stores

---

## Admin System Integration

The admin components work together to provide a complete administration experience:

```mermaid
flowchart TB
    subgraph Frontend["Frontend Layer"]
        UI[React SPA]
        State[Zustand Store]
    end

    subgraph Backend["Backend Layer"]
        API[FastAPI]
        WS[WebSocket Manager]
        Auth[Auth Service]
    end

    subgraph Observability["Observability Layer"]
        OTEL[OTEL Collector]
        Grafana[Grafana]
    end

    subgraph Storage["Storage Layer"]
        DB[(Database)]
        Cache[(Redis Cache)]
    end

    UI --> API
    UI <--> WS
    API --> Auth
    API --> DB
    API --> Cache

    Backend --> OTEL
    OTEL --> Grafana

    style Frontend fill:#e3f2fd
    style Backend fill:#e8f5e9
    style Observability fill:#fff3e0
    style Storage fill:#f5f5f5
```

### Integration Points

| From | To | Data |
|------|-----|------|
| React App | FastAPI | REST requests with JWT |
| React App | WebSocket | Real-time state sync |
| FastAPI | Auth Service | Token validation |
| FastAPI | Database | CRUD operations |
| All Services | OTEL | Metrics, traces, logs |

---

## Summary

| Diagram | Type | Purpose | Key Insight |
|---------|------|---------|-------------|
| Authentication Flow | Sequence | Login and token validation | JWT-based stateless auth |
| Telemetry Pipeline | Flowchart | Observability data flow | OTEL-based unified collection |
| Dashboard Architecture | C4 Container | System structure | Layered frontend/backend design |

---

## Usage

These diagrams render in GitHub, GitLab, VS Code (Mermaid extension), Obsidian, and [mermaid.live](https://mermaid.live).
