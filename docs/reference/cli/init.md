---
title: init
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-init-001]
tags: [cli, init, scaffold, project]
---

# cmd_init

## lattice init

Scaffolds new projects with compliant directory structures. Creates a properly structured Lattice Lock project from scratch, including all necessary configuration files, directory hierarchies, and initial templates. Supports multiple project types (agent, service, library) and can integrate with various CI/CD providers.

```bash
lattice init PROJECT_NAME --type TYPE [OPTIONS]
```

**Basic Examples:**

```bash
# Initialize a basic service project
lattice init my_service --type service
```

```bash
# Initialize an agent project
lattice init my_agent --type agent
```

```bash
# Initialize a library project
lattice init my_lib --type library
```

#### --type

Project type: agent, service, or library (required).

```bash
# Create service project
lattice init my_service --type service
```

```bash
# Create agent project
lattice init ai_agent --type agent
```

```bash
# Create library project
lattice init utils_lib --type library
```

#### --ci-provider

CI/CD provider integration: github, aws, or gcp.

```bash
# Setup GitHub Actions
lattice init my_project --type service --ci-provider github
```

```bash
# Setup AWS CodeBuild
lattice init my_service --type service --ci-provider aws
```

```bash
# Setup GCP Cloud Build
lattice init my_app --type service --ci-provider gcp
```

#### --github-repo

GitHub repository URL for CI integration.

```bash
# Link to GitHub repo
lattice init my_project --type library --ci-provider github --github-repo https://github.com/org/repo
```

```bash
# Setup with custom org
lattice init app --type service --github-repo https://github.com/myorg/myapp
```

```bash
# Private repo setup
lattice init private_app --type service --ci-provider github --github-repo https://github.com/company/private
```

#### --with-agents

Include agent scaffolding directories.

```bash
# Create with agent directories
lattice init my_agent --type agent --with-agents
```

```bash
# Service with agent support
lattice init hybrid_app --type service --with-agents
```

```bash
# Library with agent definitions
lattice init agent_lib --type library --with-agents
```

#### --verbose, -v

Show detailed output of created files.

```bash
# Verbose initialization
lattice init my_project --type service --verbose
```

```bash
# See all created files
lattice init my_app --type agent --with-agents -v
```

```bash
# Debug project creation
lattice init test_project --type library --verbose
```

**Use Cases:**
- Starting new AI agent projects with specialized scaffolding
- Creating microservices with organized source structure
- Building library packages with proper initialization
- Setting up CI/CD pipelines (GitHub Actions, AWS, GCP)
- Onboarding new team members with consistent project structure

### Process Flow Diagrams: lattice init

#### Decision Flow: Project Initialization
This diagram shows the complete decision tree for initializing a new project. Use this to understand the validation steps, directory creation process, and conditional template generation based on project type, CI provider, and agent requirements.

```mermaid
graph TD
    A[User Runs 'lattice init'] --> B{Validate Project Name}
    B -->|Invalid| C[Error: Must be snake_case]
    B -->|Valid| D[Determine Project Type]
    D --> E[Create Directory Structure]
    E --> F[Generate Base Templates]
    F --> G{CI Provider Selected?}
    G -->|Yes| H[Add CI/CD Templates]
    G -->|No| I[Skip CI Templates]
    H --> J{With Agents Flag?}
    I --> J
    J -->|Yes| K[Add Agent Scaffolding]
    J -->|No| L[Create Test Files]
    K --> L
    L --> M[Write All Files]
    M --> N[Success: Project Created]
```

#### Sequence Flow: Component Interactions
This sequence diagram illustrates the interaction between CLI components during initialization. Follow this to see how the validator, template engine, and file system work together to create a new project.

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as Init Command
    participant V as Validator
    participant T as Template Engine
    participant FS as File System

    U->>CLI: lattice init my_project --type service
    CLI->>V: Validate project name
    V-->>CLI: Valid (snake_case)
    CLI->>T: Load service templates
    T-->>CLI: Templates ready
    CLI->>FS: Create directory structure
    CLI->>T: Render lattice.yaml
    T-->>CLI: Rendered content
    CLI->>FS: Write lattice.yaml
    CLI->>T: Render README.md
    T-->>CLI: Rendered content
    CLI->>FS: Write README.md
    CLI->>FS: Create test scaffolding
    FS-->>CLI: All files created
    CLI-->>U: Success message
```

#### Data Flow: Template Processing
This data flow diagram shows how project configuration flows through the system to generate final output files. Use this to understand how different template types are selected and processed based on inputs.

```mermaid
graph LR
    A[Project Name] --> B[Validation]
    B --> C{Valid?}
    C -->|No| D[Reject with Error]
    C -->|Yes| E[Template Context]
    E --> F[Directory Creation]
    E --> G[Base Files]
    E --> H[Type-Specific Files]
    E --> I[CI/CD Files]
    E --> J[Agent Files]
    F --> K[Output Project]
    G --> K
    H --> K
    I --> K
    J --> K
```

#### Detailed Flowchart: Execution Path
This detailed flowchart provides a step-by-step view of the entire initialization process. Reference this when debugging or understanding the exact order of operations for different project configurations.

```mermaid
flowchart TD
    Start([lattice init command]) --> Parse[Parse Arguments]
    Parse --> CheckName{Name Valid?}
    CheckName -->|No| ErrorName[Show Error]
    CheckName -->|Yes| SelectType{Project Type?}
    SelectType -->|agent| AgentSetup[Agent Templates]
    SelectType -->|service| ServiceSetup[Service Templates]
    SelectType -->|library| LibrarySetup[Library Templates]
    AgentSetup --> CommonDirs[Create Common Dirs]
    ServiceSetup --> CommonDirs
    LibrarySetup --> CommonDirs
    CommonDirs --> CheckCI{CI Provider?}
    CheckCI -->|github| GHTemplates[Add GitHub Actions]
    CheckCI -->|aws| AWSTemplates[Add AWS CodeBuild]
    CheckCI -->|gcp| GCPTemplates[Add GCP Cloud Build]
    CheckCI -->|none| SkipCI[Skip CI Setup]
    GHTemplates --> CheckAgents
    AWSTemplates --> CheckAgents
    GCPTemplates --> CheckAgents
    SkipCI --> CheckAgents
    CheckAgents{With Agents?} -->|Yes| AddAgents[Create Agent Dirs]
    CheckAgents -->|No| FinalFiles[Create Final Files]
    AddAgents --> FinalFiles
    FinalFiles --> Complete([Project Created])
```

#### State Diagram: Project Creation States
This state diagram shows all possible states during project creation and transitions between them. Use this to understand the lifecycle of an initialization request and identify where failures might occur.

```mermaid
stateDiagram-v2
    [*] --> Parsing: User Input
    Parsing --> Validating: Parse Complete
    Validating --> Rejected: Invalid Name
    Validating --> Configuring: Valid Name
    Rejected --> [*]
    Configuring --> CreatingStructure: Config Ready
    CreatingStructure --> GeneratingTemplates: Dirs Created
    GeneratingTemplates --> WritingFiles: Templates Ready
    WritingFiles --> AddingCICD: Base Files Written
    AddingCICD --> AddingAgents: CI/CD Added
    AddingCICD --> Finalizing: No CI/CD
    AddingAgents --> Finalizing: Agents Added
    AddingAgents --> Finalizing: No Agents
    Finalizing --> [*]: Success
```
