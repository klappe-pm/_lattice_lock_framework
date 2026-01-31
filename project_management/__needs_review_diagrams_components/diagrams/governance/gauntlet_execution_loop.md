# Gauntlet Execution Loop

```mermaid
stateDiagram-v2
    [*] --> Discovery
    Discovery --> Collection: Find Tests
    
    Collection --> Execution: Run Pytest
    
    state Execution {
        [*] --> Setup
        Setup --> RunTest
        RunTest --> Teardown
        Teardown --> StoreResult
        
        StoreResult --> [*]
    }
    
    Execution --> Analysis: Aggregate Results
    
    Analysis --> Success: All Pass
    Analysis --> Failure: Failures > 0
    
    Failure --> Retry{Auto-Fix?}
    Retry --> CodeGen: Yes
    CodeGen --> Execution
    
    Retry --> [*]: No
    Success --> [*]
```
