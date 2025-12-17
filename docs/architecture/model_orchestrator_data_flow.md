# Model Orchestrator Data Flow

## Data Flow

- User submits task via CLI or API
- Orchestrator analyzes task type and requirements
- Selection engine scores all available models
- Applies MODELS.md rules and constraints
- Checks cost budget and quality requirements
- Selects optimal model (or consensus set)
- Routes to appropriate API client
- Executes query with fallback handling
- Tracks performance and cost
- Returns result to user
- Updates performance history for future optimization
