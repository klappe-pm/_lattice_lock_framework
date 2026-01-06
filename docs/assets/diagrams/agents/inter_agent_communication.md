# Inter-Agent Communication

```mermaid
sequenceDiagram
    classDef agent fill:#e0f2f1,stroke:#004d40,stroke-width:2px;
    
    participant PM as "Project Agent[concept-agents-001]"
    participant Eng as "Engineering Agent"
    participant QA as "QA Agent"

    PM->>Eng: assign_task(feature_spec)
    activate Eng
    
    Eng->>Eng: Implement Feature
    
    Eng->>QA: request_verification(pr_link)
    activate QA
    
    QA->>QA: Run Tests
    QA-->>Eng: Report (Bugs Found)
    deactivate QA
    
    Eng->>Eng: Fix Bugs
    Eng-->>PM: Task Complete
    deactivate Eng
```
