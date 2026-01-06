# Governance Validation Flow

```mermaid
sequenceDiagram
    %% Standard Class Definitions
    classDef cli fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px;

    participant User
    participant CLI as "CLI[cli-validate-001]"
    participant Validator as "Schema Validator[api-validator-001]"
    participant Sheriff as "Sheriff[mod-sheriff-001]"
    participant Gauntlet as "Gauntlet[api-gauntlet-001]"

    User->>CLI: lattice validate
    
    rect rgb(240, 248, 255)
        Note over CLI, Validator: Step 1: Structural Validation
        CLI->>Validator: validate_structure()
        Validator-->>CLI: StructureReport
    end
    
    alt Structure Failed
        CLI-->>User: Report Errors & Exit
    end

    rect rgb(255, 250, 240)
        Note over CLI, Sheriff: Step 2: Static Analysis
        CLI->>Sheriff: run_analysis()
        Sheriff-->>CLI: SheriffReport
    end
    
    alt Sheriff Failed (Errors > 0)
        CLI-->>User: Report Violations & Exit
    end

    rect rgb(240, 255, 240)
        Note over CLI, Gauntlet: Step 3: Runtime Verification
        CLI->>Gauntlet: run_verification()
        Gauntlet-->>CLI: GauntletReport
    end

    CLI-->>User: Final Success Report
```
