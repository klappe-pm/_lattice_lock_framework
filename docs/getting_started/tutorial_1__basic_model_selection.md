# Tutorial 1 - Basic Model Selection

Learn how the Model Orchestrator intelligently selects AI models based on task requirements, balancing quality, cost, and speed.

---

## Learning Objectives

By completing this tutorial, you will:

- Understand how the Model Orchestrator analyzes tasks
- Use the CLI to see model selection reasoning
- Override automatic selection with strategies
- Track usage and costs
- Make informed model selection decisions

**Time Required**: 10-15 minutes
**Difficulty**: Beginner
**Prerequisites**: Interactive Onboarding Guide complete

---

## What is Model Selection?

The Model Orchestrator is an intelligent system that chooses the best AI model for each task. Instead of manually picking models, you describe your task and the orchestrator:

1. **Analyzes** task complexity, domain, and requirements
2. **Scores** available models based on suitability
3. **Selects** optimal model balancing quality, cost, and speed
4. **Falls back** to alternatives if primary model unavailable

### Why This Matters

**Without Intelligent Selection**:
- Use expensive cloud models for simple tasks (waste money)
- Use weak models for complex tasks (poor quality)
- Manually track which model works best (time consuming)

**With Model Orchestrator**:
- Automatic selection optimized for each task
- > 70% local model usage (minimize costs)
- Consistent quality with smart fallbacks

---

## Tutorial Setup

### Verify Prerequisites

```bash
# Navigate to project directory
cd /Users/kevinlappe/Obsidian/Power\ Prompts

# Verify Model Orchestrator exists
ls Model\ Orchestrator/model-orchestrator-consolidated.py

# Check Python version
python3 --version  # Should be 3.8+
```

### Understanding Available Models

The system supports 52 models across 6 providers:

**Local Models** (Free, Private, Fast):
- CodeLlama 34B: Premium code quality (requires Ollama)
- Qwen 2.5 32B: Premium intelligence (requires Ollama)
- Magicoder 7B: Balanced code generation (requires Ollama)
- Llama 3.1 8B: General tasks (requires Ollama)
- DeepSeek Coder 1.3B: Quick code snippets (requires Ollama)

**Cloud Models** (Premium Quality, Pay Per Use):
- Claude Opus 4: Best reasoning and code (Anthropic)
- Claude Sonnet 4.5: Best writing quality (Anthropic)
- GPT-4o: Fast and capable (OpenAI)
- O1 Pro: Ultimate reasoning (OpenAI)
- Gemini 2.5 Pro: Large context (Google)

**Don't have local models?** No problem! The tutorial works with cloud models only.

---

## Exercise 1: Analyze Task and See Reasoning

The `analyze` command shows how the orchestrator thinks about your task.

### Step 1: Analyze a Code Task

```bash
cd Model\ Orchestrator

# Analyze code generation task
python3 orchestrator-cli.py analyze "Generate a Python function to calculate Fibonacci sequence"
```

**Expected Output**:

```
Analyzing task: "Generate a Python function to calculate Fibonacci sequence"

Task Classification:
  - Task Type: CODE_GENERATION
  - Complexity: MEDIUM
  - Domain: Python
  - Estimated Tokens: 500

Model Selection Reasoning:
  Primary: codellama:34b (Score: 0.95)
    - Code specialization: EXCELLENT
    - Quality match: HIGH
    - Cost: FREE (local)
    - Availability: CHECK

  Fallback 1: claude-opus-4 (Score: 0.90)
    - Reasoning capability: EXCELLENT
    - Quality: PREMIUM
    - Cost: $0.015 per 1K tokens
    - Availability: DEPENDS_ON_API_KEY

  Fallback 2: magicoder:7b (Score: 0.85)
    - Code quality: GOOD
    - Speed: FAST
    - Cost: FREE (local)

Recommendation: Use codellama:34b for best quality at zero cost
```

### Step 2: Analyze a Reasoning Task

```bash
# Analyze complex reasoning task
python3 orchestrator-cli.py analyze "Analyze the tradeoffs between microservices and monolithic architecture for a startup"
```

**What to Notice**:
- Different task type (REASONING vs CODE_GENERATION)
- Different model selection (reasoning-focused models score higher)
- Higher complexity estimate
- Different quality thresholds

### Step 3: Analyze a Documentation Task

```bash
# Analyze writing task
python3 orchestrator-cli.py analyze "Write user-friendly documentation for an API endpoint"
```

**What to Notice**:
- Task type: DOCUMENTATION
- Models optimized for writing quality score higher
- Claude Sonnet 4.5 typically recommended for user-facing content

---

## Exercise 2: Use Selection Strategies

Strategies let you override default behavior to prioritize cost, quality, or speed.

### Strategy 1: Balanced (Default)

```bash
# Default balanced strategy
python3 orchestrator-cli.py route "Create a REST API endpoint for user authentication" --strategy balanced
```

**Balanced Strategy**:
- Quality weight: 40%
- Cost weight: 30%
- Speed weight: 30%
- **Use Case**: General-purpose tasks

### Strategy 2: Cost Optimize

```bash
# Minimize costs (prefer local models)
python3 orchestrator-cli.py route "Create a REST API endpoint for user authentication" --strategy cost_optimize
```

**Cost Optimize Strategy**:
- Quality weight: 30%
- Cost weight: 50%
- Speed weight: 20%
- **Use Case**: Budget-conscious projects, development/testing

### Strategy 3: Quality First

```bash
# Maximize quality (willing to pay for premium models)
python3 orchestrator-cli.py route "Create a REST API endpoint for user authentication" --strategy quality_first
```

**Quality First Strategy**:
- Quality weight: 60%
- Cost weight: 10%
- Speed weight: 30%
- **Use Case**: Production code, critical features, user-facing content

### Strategy 4: Speed Priority

```bash
# Fastest response (small/fast models)
python3 orchestrator-cli.py route "What is Python?" --strategy speed_priority
```

**Speed Priority Strategy**:
- Quality weight: 20%
- Cost weight: 30%
- Speed weight: 50%
- **Use Case**: Quick queries, prototyping, development iterations

---

## Exercise 3: Force Local-Only Models

For zero-cost operation, you can force local-only model selection.

### Python API Approach

Create a test file `test_local_only.py`:

```python
from model_orchestrator import ModelOrchestrator, TaskType, TaskRequirements

# Initialize orchestrator
orchestrator = ModelOrchestrator()

# Force local-only with requirements
requirements = TaskRequirements(
    task_type=TaskType.CODE_GENERATION,
    max_cost=0.0,  # Zero cost = local only
    quality_threshold=0.7  # Minimum acceptable quality
)

# Select model
model_id, model = orchestrator.select_model_with_requirements(requirements)

print(f"Selected Model: {model_id}")
print(f"Cost: ${model.cost_per_1k_input} per 1K tokens")
print(f"Location: {model.location}")
```

### Run the Test

```bash
cd Model\ Orchestrator
python3 test_local_only.py
```

**Expected Output**:

```
Selected Model: codellama:34b
Cost: $0.0 per 1K tokens
Location: local
```

**Note**: If no local models are available, you'll get an error. In that case, set `max_cost=0.05` to allow cheap cloud models.

---

## Exercise 4: Track Usage and Costs

Understanding usage patterns helps optimize costs.

### Step 1: Simulate Usage Tracking

Create `test_tracking.py`:

```python
from model_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Simulate several model uses
tasks = [
    "Generate Python function",
    "Write API documentation",
    "Analyze code architecture",
    "Create unit tests",
    "Optimize performance"
]

for task in tasks:
    model_id, model = orchestrator.select_model(task, strategy="balanced")

    # Simulate usage (in real usage, these values come from actual API responses)
    orchestrator.track_usage(
        model_id=model_id,
        input_tokens=500,
        output_tokens=300,
        latency_ms=1200
    )
    print(f"Task: {task[:30]}... -> {model_id}")

# Get cost report
print("\n=== Cost Report ===")
report = orchestrator.get_cost_report()

print(f"Total Cost: ${report['total_cost']:.4f}")
print(f"Total Requests: {report['total_requests']}")
print(f"Average Cost per Request: ${report['average_cost']:.4f}")

print("\nTop 3 Models by Cost:")
for model_id, cost in sorted(report['by_model'].items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"  {model_id}: ${cost:.4f}")

print("\nCost by Provider:")
for provider, cost in sorted(report['by_provider'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {provider}: ${cost:.4f}")
```

### Step 2: Run Tracking Test

```bash
python3 test_tracking.py
```

**Sample Output**:

```
Task: Generate Python function... -> codellama:34b
Task: Write API documentation... -> claude-sonnet-4-5
Task: Analyze code architecture... -> qwen2.5:32b
Task: Create unit tests... -> magicoder:7b
Task: Optimize performance... -> codellama:34b

=== Cost Report ===
Total Cost: $0.0450
Total Requests: 5
Average Cost per Request: $0.0090

Top 3 Models by Cost:
  claude-sonnet-4-5: $0.0450
  codellama:34b: $0.0000
  qwen2.5:32b: $0.0000

Cost by Provider:
  anthropic: $0.0450
  ollama: $0.0000
```

**Insight**: Most tasks used free local models, only documentation used cloud model for quality.

---

## Exercise 5: Multi-Model Consensus

For critical decisions, use consensus mode to get multiple perspectives.

### CLI Consensus

```bash
# Get consensus from 3 models
python3 orchestrator-cli.py consensus "Should we use microservices or monolithic architecture?" --num 3
```

**What Happens**:
1. Task analyzed for complexity
2. Top 3 diverse models selected
3. Each model provides independent response
4. Responses aggregated with reasoning

**Use Cases for Consensus**:
- Critical architectural decisions
- Security vulnerability assessment
- Performance optimization strategies
- Code review for production changes

---

## Practice Challenges

Test your understanding with these challenges.

### Challenge 1: Task Type Identification

For each task, predict the task type:

1. "Debug a memory leak in Python application"
2. "Explain dependency injection pattern"
3. "Write a blog post about AI ethics"
4. "Create SQL queries for user analytics"

<details>
<summary>Click to see answers</summary>

1. CODE_DEBUG (debugging domain)
2. REASONING (explanation and analysis)
3. DOCUMENTATION (writing content)
4. CODE_GENERATION (creating code)

</details>

### Challenge 2: Strategy Selection

For each scenario, choose the best strategy:

1. Prototyping a new feature (speed matters most)
2. Writing customer-facing documentation (quality critical)
3. Development testing (want to minimize costs)
4. Production code review (balanced approach)

<details>
<summary>Click to see answers</summary>

1. speed_priority (fast iteration)
2. quality_first (premium writing quality)
3. cost_optimize (free local models)
4. balanced (default quality/cost/speed balance)

</details>

### Challenge 3: Cost Optimization

You have 100 tasks per day. How do you minimize costs while maintaining quality?

<details>
<summary>Click to see solution</summary>

**Strategy**:
1. Set up local models (CodeLlama 34B, Qwen 2.5 32B, Magicoder 7B)
2. Use `strategy="cost_optimize"` by default
3. Override to `quality_first` only for critical tasks (user-facing, production code)
4. Use `speed_priority` for development testing
5. Set `max_cost=0.0` for non-critical tasks

**Expected Cost Reduction**: 70-80% (from ~$10/day to ~$2/day)

</details>

---

## Key Takeaways

**1. Task Analysis is Automatic**
- Model Orchestrator analyzes task type, complexity, domain
- You just describe your task in natural language
- No need to manually choose models

**2. Strategies Control Tradeoffs**
- `balanced`: Default quality/cost/speed balance
- `cost_optimize`: Prefer free local models
- `quality_first`: Premium models for critical work
- `speed_priority`: Fast responses

**3. Local Models Save Money**
- 52 models available, majority are local (free)
- > 70% local usage achievable with proper setup
- Zero cost for most development tasks

**4. Tracking Enables Optimization**
- Monitor costs by model and provider
- Identify expensive tasks
- Optimize strategy selections

**5. Consensus for Critical Decisions**
- Use multiple models for important choices
- Reduces bias and blind spots
- Higher cost but better quality

---

## What's Next?

You've mastered basic model selection! Here are your next steps:

### Immediate Next Steps

1. **Try Tutorial 2**: [Multi-Model Consensus](Tutorial-2-Multi-Model-Consensus.md)
2. **Set Up Local Models**: [Local Models Setup Guide](../Local%20Models%20Setup%20Guide.md)
3. **Explore API**: [Model Orchestrator API Documentation](API%20Documentation.md)

### This Week

1. Experiment with all 4 strategies
2. Track your usage patterns
3. Set up at least 2 local models

### This Month

1. Optimize cost by preferring local models
2. Use consensus for 1-2 critical decisions
3. Contribute model performance feedback

---

## Troubleshooting

### "Model Not available" error

**Solution**: Model not installed locally. Either:
1. Install with Ollama: `ollama pull [model-name]`
2. Use cloud alternative: Add API key and try again
3. Let orchestrator fallback: It will try next best model

### "All Models failed" error

**Solution**: No models available. Check:
1. Ollama running: `ollama list`
2. API keys set: `echo $ANTHROPIC_API_KEY`
3. Network connection working

### High costs despite cost_optimize

**Solution**:
1. Verify local models installed: `ollama list`
2. Set hard limit: `requirements.max_cost = 0.0`
3. Check task complexity (complex tasks may need cloud models)

---

**Tutorial Complete!** You now understand model selection fundamentals.

**Next Tutorial**: [Tutorial 2: Multi-Model Consensus](Tutorial-2-Multi-Model-Consensus.md)

---

**Tutorial Version**: 1.0
**Last Updated**: 2025-10-05
**Estimated Time**: 10-15 minutes
**Difficulty**: Beginner
