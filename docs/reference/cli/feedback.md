---
title: feedback
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-feedback-001]
tags: [cli, feedback, support]
---

# cmd_feedback

## lattice feedback

Submit structured feedback about Lattice Lock framework. Collects categorized feedback with priority levels for framework improvement and bug reporting.

```bash
lattice feedback [OPTIONS]
```

**Basic Examples:**

```bash
# Submit feedback interactively
lattice feedback
```

```bash
# Submit bug report
lattice feedback --category bug --priority high
```

```bash
# Feature request
lattice feedback --category feature --priority medium
```

#### --category

Category of feedback: bug, feature, improvement, documentation, other.

```bash
# Report a bug
lattice feedback --category bug
```

```bash
# Request new feature
lattice feedback --category feature
```

```bash
# Suggest improvement
lattice feedback --category improvement
```

#### --priority

Priority level: low, medium, high, critical.

```bash
# Low priority feedback
lattice feedback --priority low
```

```bash
# High priority issue
lattice feedback --category bug --priority high
```

```bash
# Critical bug
lattice feedback --category bug --priority critical
```

#### --storage

Storage backend for feedback: local, github, api.

```bash
# Store locally
lattice feedback --storage local
```

```bash
# Submit to GitHub issues
lattice feedback --storage github
```

```bash
# Send to API endpoint
lattice feedback --storage api
```

**Use Cases:**
- Bug reporting
- Feature requests
- Documentation improvements
- User experience feedback
- Framework enhancement suggestions

### Process Flow Diagrams: lattice feedback

#### Decision Flow: Feedback Collection and Routing
This diagram shows how feedback is collected, categorized, and routed to appropriate storage backends. Use this to understand the feedback submission flow.

```mermaid
graph TD
    A[Start Feedback] --> B{Interactive Mode?}
    B -->|Yes| C[Prompt for Category]
    B -->|No| D{Category Provided?}
    C --> E[Prompt for Priority]
    D -->|Yes| F{Priority Provided?}
    D -->|No| C
    E --> G[Prompt for Details]
    F -->|Yes| H[Collect Details]
    F -->|No| E
    G --> I{Storage Backend?}
    H --> I
    I -->|Local| J[Write to lattice feedback]
    I -->|GitHub| K{GitHub Token?}
    I -->|API| L{API Configured?}
    K -->|Yes| M[Create Issue]
    K -->|No| N[Error: No token]
    L -->|Yes| O[POST to API]
    L -->|No| P[Error: No config]
    J --> Q[Success]
    M --> Q
    O --> Q
```

#### Sequence Flow: GitHub Integration
This diagram illustrates the process of submitting feedback as a GitHub issue. Use this when configuring GitHub integration for feedback collection.

```mermaid
sequenceDiagram
    participant User
    participant CLI as Feedback Command
    participant Collector as Feedback Collector
    participant GitHub as GitHub API
    participant Local as Local Storage
    
    User->>CLI: lattice feedback
    CLI->>Collector: Initialize
    Collector->>User: Prompt category
    User-->>Collector: bug
    Collector->>User: Prompt priority
    User-->>Collector: high
    Collector->>User: Prompt details
    User-->>Collector: Description
    Collector->>Collector: Format feedback
    alt GitHub storage
        Collector->>GitHub: Authenticate
        GitHub-->>Collector: Token valid
        Collector->>GitHub: Create issue
        GitHub-->>Collector: Issue created
        Collector->>Local: Save backup
    else Local storage
        Collector->>Local: Write feedback
        Local-->>Collector: Saved
    end
    Collector-->>User: Confirmation
```

#### Data Flow: Feedback Processing
This diagram shows how feedback data flows from collection to storage. Use this to understand feedback data handling.

```mermaid
graph LR
    A[User Input] --> B[Feedback Collector]
    B --> C[Category Validator]
    B --> D[Priority Validator]
    C --> E[Feedback Object]
    D --> E
    E --> F{Storage Type?}
    F -->|Local| G[JSON File]
    F -->|GitHub| H[Issue Formatter]
    F -->|API| I[API Payload]
    G --> J[lattice feedback folder]
    H --> K[GitHub API]
    I --> L[Remote Server]
    K --> M[Issue Number]
    L --> N[Response ID]
    M --> O[Confirmation]
    N --> O
    J --> O
```

#### Detailed Flowchart: Category-Based Routing
This flowchart details how different feedback categories are processed and routed. Use this to understand category-specific handling.

```mermaid
flowchart TD
    A[Feedback Received] --> B{Category}
    B -->|Bug| C[Validate Stack Trace]
    B -->|Feature| D[Check Existing Requests]
    B -->|Improvement| E[Assess Impact]
    B -->|Documentation| F[Identify Section]
    B -->|Other| G[General Processing]
    C --> H{Has Logs?}
    H -->|Yes| I[Attach Logs]
    H -->|No| J[Request Logs]
    D --> K{Duplicate?}
    K -->|Yes| L[Link to Existing]
    K -->|No| M[Create New]
    E --> N[Priority Assessment]
    F --> O[Documentation Index]
    I --> P[Store Feedback]
    J --> P
    M --> P
    L --> P
    N --> P
    O --> P
    G --> P
```

#### State Diagram: Feedback Lifecycle
This state diagram shows the different states of submitted feedback. Use this to track feedback status over time.

```mermaid
stateDiagram-v2
    [*] --> Draft: User starts
    Draft --> Submitted: Submit feedback
    Submitted --> Acknowledged: Auto-confirmation
    Acknowledged --> Triaged: Review process
    Triaged --> InProgress: Action taken
    Triaged --> Rejected: Not applicable
    InProgress --> Resolved: Implemented
    InProgress --> Blocked: Dependencies
    Blocked --> InProgress: Unblocked
    Resolved --> [*]
    Rejected --> [*]
```
