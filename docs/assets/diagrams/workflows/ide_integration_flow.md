# IDE Integration Flow

```mermaid
sequenceDiagram
    %% Standard Class Definitions
    classDef ide fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;

    participant Editor as "VS Code / Cursor"
    participant LSP as "Lattice LSP Server"
    participant Sheriff as "Sheriff Analyzer[mod-sheriff-001]"

    Editor->>LSP: textDocument/didOpen
    Editor->>LSP: textDocument/didChange
    
    LSP->>Sheriff: validate_file_content(content)
    Sheriff-->>LSP: List[Violation]
    
    LSP-->>Editor: textDocument/publishDiagnostics
    
    Note over Editor, LSP: User hovers over error
    
    Editor->>LSP: textDocument/hover
    LSP->>Sheriff: get_rule_explanation(code)
    Sheriff-->>LSP: Markdown Description
    LSP-->>Editor: Tooltip
```
