# Architecture Details

## Architecture Details

### Model Selection Algorithm

The orchestrator uses a weighted scoring system:

- **Task Affinity (40%)**: How well the model handles the specific task type
- **Performance (30%)**: Speed vs reasoning depth trade-off
- **Accuracy (20%)**: Model accuracy rating for the task
- **Cost Efficiency (10%)**: Price/performance ratio

### Task Type Detection

The system automatically detects these task types:

- `CODE_GENERATION`, `CODE_REVIEW`, `DEBUGGING`
- `REASONING`, `ANALYSIS`, `SYSTEM_DESIGN`
- `VISION`, `IMAGE_GENERATION`
- `CREATIVE_WRITING`, `TRANSLATION`, `SUMMARIZATION`
- `QA`, `CONVERSATION`, `RESEARCH`, `DATA_ANALYSIS`

### Multi-Model Patterns

1. **Chain of Thought**: Sequential processing through multiple models
2. **Parallel Consensus**: Multiple models vote on the answer
3. **Hierarchical Refinement**: Start with cheap model, refine with better ones
4. **Adaptive Analysis**: Depth adjusts based on complexity

## Configuration Management

### Model Configuration

Models are defined in the orchestrator with comprehensive capability profiles:

- Context window size
- Task-specific scoring
- Cost per million tokens (input/output)
- Special capabilities (vision, reasoning, function calling)
- Performance metrics (speed, accuracy, creativity)

### Strategy Options

- `balanced`: Default strategy balancing all factors
- `cost_optimize`: Minimize costs while meeting requirements
- `quality_first`: Maximize accuracy and reasoning capability
- `speed_priority`: Fastest response time

### Configuration Files

- `grok-models-config.yaml`: Complete Grok model definitions and aliases
- Model capabilities hardcoded in `model-orchestrator.py` for now
- API endpoints and authentication configured via environment variables

## Claude Integration Specifics

This repository follows the comprehensive Claude configuration system defined in `CLAUDE.md`:

### Required Reading Order

1. `CLAUDE.md` (configuration)
2. `gitignore/Claude Context/CLAUDE.context.md` (current context)
3. `gitignore/Plans/[project-plan-file].md` (project plan)

### Key Integration Points

- Multi-agent orchestration patterns align with Claude's agent definitions
- Context management through snapshot files and main context tracking
- Task planning integration with the orchestration workflow
- Cost tracking aligns with the multi-provider cost optimization
