# Provider Fallback Strategy

```mermaid
sequenceDiagram
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5;
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px;

    participant Orch as "Orchestrator[mod-orchestrator-001]"
    participant P1 as "Primary Provider (GPT-4)"
    participant P2 as "Fallback 1 (Claude 3)"
    participant P3 as "Fallback 2 (Llama 3)"

    Orch->>P1: attempt_request(prompt)
    
    alt Success
        P1-->>Orch: 200 OK (Response)
    else Timeout / 5xx Error
        P1-->>Orch: Error
        Note over Orch: Log Failure & Cost
        
        Orch->>P2: attempt_request(prompt)
        
        alt Success
            P2-->>Orch: 200 OK (Response)
        else Error
            P2-->>Orch: Error
            
            Orch->>P3: attempt_request(prompt)
            alt Success
                P3-->>Orch: 200 OK (Response)
            else Error
                Orch-->>Orch: All Providers Failed
                Orch-->>User: Raise ProviderExhaustedError
            end
        end
    end
```
