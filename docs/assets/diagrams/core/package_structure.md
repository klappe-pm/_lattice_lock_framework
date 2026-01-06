# Package Structure

```mermaid
classDiagram
    %% Standard Class Definitions
    classDef pkg fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef mod fill:#e0f2f1,stroke:#004d40,stroke-width:2px;
    
    package "src.lattice_lock" {
        class CLI:::pkg
        class Orchestrator:::pkg
        class Sheriff:::pkg
        class Gauntlet:::pkg
        class Admin:::pkg
        class Config:::pkg
        class Database:::pkg
        class Utils:::pkg
    }
    
    CLI ..> Orchestrator : uses
    CLI ..> Sheriff : uses
    CLI ..> Gauntlet : uses
    CLI ..> Admin : uses
    
    Orchestrator ..> Config : reads
    Sheriff ..> Config : reads
    Gauntlet ..> Config : reads
    
    Admin ..> Database : owns
    Orchestrator ..> Database : logs to
    
    class Orchestrator {
        +providers
        +routing
        +scoring
        +consensus
    }
    
    class Sheriff {
        +ast_visitor
        +rules
        +reports
    }
    
    class Gauntlet {
        +generator
        +validator
        +runner
    }
    
    class Config {
        +loader
        +schema
        +inheritance
    }
```
