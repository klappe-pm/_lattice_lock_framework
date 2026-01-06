# Consensus Engine Voting

```mermaid
sequenceDiagram
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5;

    participant Client
    participant Engine as "ConsensusEngine[mod-consensus-001]"
    participant Voter1 as "Model A"
    participant Voter2 as "Model B"
    participant Voter3 as "Model C"

    Client->>Engine: request_consensus(prompt, strategy='majority')
    
    par Vote Collection
        Engine->>Voter1: get_response(prompt)
        Engine->>Voter2: get_response(prompt)
        Engine->>Voter3: get_response(prompt)
    end
    
    Voter1-->>Engine: Response A
    Voter2-->>Engine: Response B
    Voter3-->>Engine: Response A
    
    Engine->>Engine: tally_votes()
    Note right of Engine: A: 2 votes, B: 1 vote
    
    Engine-->>Client: Response A (Winner)
```
