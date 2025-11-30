# Model Selection Guidelines


**63 Models Across 8 Providers** - Intelligent Task-to-Model Routing

## Task-to-Model Mapping Rules

### Code Tasks
- **Code Generation**: 
  - **Premium**: codellama:34b (local, free) > grok-code-fast-1 > claude-sonnet-4.5 > o3 > magicoder:7b (local, free)
  - **Balanced**: magicoder:7b (local, free) > codellama:13b (local, free) > gemma:7b (local, free) > claude-sonnet-4 > gpt-4o > qwen2.5:32b (local, free)
  - **Fast**: deepseek-coder:1.3b (local, free) > gpt-4o-mini > claude-3-haiku
- **Code Review**: 
  - **Ultimate**: deepseek-r1:70b (local, free) > claude-opus-4.1 > o1-pro > codellama:34b (local, free)
  - **Balanced**: claude-opus-4 > grok-3 > codellama:13b (local, free) > claude-sonnet-4.5
- **Debugging**: 
  - **Best**: deepseek-r1:70b (local, free) > o1-pro > grok-code-fast-1 > codellama:34b (local, free)
  - **Fast**: magicoder:7b (local, free) > gpt-4o > o3-mini > deepseek-coder:1.3b (local, free)

### Reasoning & Analysis
- **Complex Reasoning**: 
  - **Ultimate**: deepseek-r1:70b (local, free) > claude-opus-4.1 > o1-pro > grok-4-fast-reasoning
  - **Balanced**: qwen2.5:32b (local, free) > qwen2.5:7b-instruct (local, free) > claude-opus-4 > o1 > gemini-2.0-pro
- **System Design**: 
  - **Best**: deepseek-r1:70b (local, free) > claude-opus-4.1 > llama-3.1-405b (local, free) > o1-pro
  - **Practical**: qwen2.5:32b (local, free) > claude-sonnet-4.5 > gemini-2.0-pro > grok-3
- **Data Analysis**: 
  - **Advanced**: deepseek-r1:70b (local, free) > gemini-2.0-pro > claude-opus-4 > qwen2.5:32b (local, free)
  - **Quick**: qwen3:8b (local, free) > gemini-2.0-flash > gpt-4o-mini
- **Research**: 
  - **Deep**: deepseek-r1:70b (local, free) > gemini-2.0-pro > claude-opus-4.1 > grok-4-fast-reasoning
  - **Fast**: qwen2.5:32b (local, free) > gemini-2.0-flash > claude-3.5-sonnet

### Creative Tasks
- **Creative Writing**: 
  - **Premium**: claude-opus-4.1 > gpt-4.1-2025 > qwen2.5:32b (local, free) > claude-opus-4
  - **Balanced**: claude-sonnet-4.5 > qwen3:8b (local, free) > gemma:7b (local, free) > gpt-4o > gemini-2.0-pro
- **Storytelling**: 
  - **Best**: gpt-4.1-2025 > claude-opus-4.1 > qwen2.5:32b (local, free) > claude-sonnet-4.5
  - **Quick**: qwen3:8b (local, free) > llama3.1:8b (local, free) > gpt-4o-mini
- **Poetry**: 
  - **Artistic**: claude-opus-4.1 > gpt-4.1-2025 > qwen2.5:32b (local, free) > claude-3.5-sonnet

### Vision & Images
- **Image Analysis**: 
  - **Best**: llama-3.2-90b (local, free, vision) > gpt-4o > grok-2-vision-1212 > llama-3.2-11b (local, free, vision)
  - **Cloud**: gpt-4-turbo > grok-2-vision-1212 > gemini-2.0-pro
- **Screenshot Analysis**: 
  - **Local**: llama-3.2-90b (local, free, vision) > llama-3.2-11b (local, free, vision)
  - **Cloud**: gpt-4o > grok-2-vision-1212 > gemini-2.0-flash

### Fast Tasks
- **Quick Answers**: 
  - **Instant**: deepseek-coder:1.3b (local, free) > llama3.2:3b (local, free) > gemma:7b (local, free) > llama3.1:8b (local, free)
  - **Cloud**: gemini-2.0-flash > claude-3-haiku > gpt-4o-mini
- **Translation**: 
  - **Best**: qwen2.5:32b (local, free) > qwen2.5:7b-instruct (local, free) > qwen3:8b (local, free) > gemini-2.0-flash > claude-3.5-sonnet
  - **Quick**: qwen2.5:7b-instruct (local, free) > qwen3:8b (local, free) > llama3.1:8b (local, free) > gemini-2.0-flash
- **Summarization**: 
  - **Fast**: llama3.2:3b (local, free) > llama3.1:8b (local, free) > claude-3-haiku
  - **Quality**: qwen2.5:32b (local, free) > grok-4-fast-non-reasoning > gemini-2.0-flash

### Large Context Tasks (>500K tokens)
**2M Token Models:**
1. grok-4-fast-reasoning (2M) - Best for complex reasoning
2. grok-4-fast-non-reasoning (2M) - Fast processing
3. gemini-2.0-pro (2M) - Research and analysis
4. gemini-1.5-pro (2M) - Previous generation

**1M Token Models:**
5. gpt-4.1-2025 (1M) - Premium OpenAI
6. gemini-2.0-flash (1M) - Fast responses
7. gemini-1.5-flash (1M) - Cost-effective

**Large Context Local Models:**
8. llama-3.2-90b (128K, local, free) - Best local large context
9. llama-3.1-405b (128K, local, free) - Ultimate local model
10. llama-3.1-70b (128K, local, free) - Balanced local option

## Cost Optimization Rules

### Budget Tiers
- **FREE ($0.00)**: All 20 local models - **ALWAYS PREFERRED**
  - deepseek-r1:70b, codellama:34b, qwen2.5:32b, magicoder:7b, gemma:7b, qwen2.5:7b-instruct, etc.
- **Ultra-Low (<$0.001/1K)**: gemini-2.0-flash ($0.1/$0.4), gemini-1.5-flash ($0.075/$0.3)
- **Low (<$0.01/1K)**: claude-3-haiku ($0.25/$1.25), gpt-4o-mini ($0.15/$0.6), grok-3 ($1/$3)
- **Medium (<$0.1/1K)**: claude-3.5-sonnet ($3/$15), gpt-4o ($5/$15), claude-sonnet-4 ($3/$15)
- **High (<$1/1K)**: o1 ($15/$60), o3 ($10/$30), grok-4 variants ($1-2/$3-6)
- **Premium (>$1/1K)**: claude-opus-4.1 ($20/$100), o1-pro ($60/$240)

### Cost Strategy Overrides
- **Always prefer local models first**: All local models are $0.00 and should be prioritized
- If budget < $0.01: Use local models OR gemini-2.0-flash, claude-3-haiku
- If budget < $0.1: Exclude premium models (opus-4.1, o1-pro, high-cost Grok variants)
- **Local model validation**: Use consensus with cloud models for critical tasks
- **Zero-cost strategy**: `cost_optimize` should always prefer suitable local models

## Performance Rules

### Speed Priority
**Local Models (Instant Response):**
1. deepseek-coder:1.3b (local, instant, 0.98 speed)
2. llama3.2:3b (local, instant, 0.95 speed)
3. llama3.1:8b (local, instant, 0.9 speed)
4. magicoder:7b (local, instant, 0.9 speed)
5. qwen3:8b (local, instant, 0.85 speed)

**Cloud Models:**
6. gemini-2.0-flash (0.95 speed)
7. claude-3-haiku (0.9 speed)
8. gpt-4o-mini (0.9 speed)
9. grok-4-fast-non-reasoning (0.9 speed)

### Accuracy Priority  
**Ultimate Accuracy:**
1. claude-opus-4.1 (0.95 accuracy) - Premium cloud
2. deepseek-r1:70b (0.92 accuracy) - **FREE local**
3. o1-pro (0.98 accuracy) - Premium cloud
4. codellama:34b (0.9 accuracy) - **FREE local**
5. qwen2.5:32b (0.88 accuracy) - **FREE local**

**High Accuracy Cloud:**
6. claude-opus-4 (0.95 accuracy)
7. o1 (0.95 accuracy)
8. gpt-4o (0.9 accuracy)
9. grok-4-fast-reasoning (0.9 accuracy)

### Balanced Selection
**Local Models (Free + Balanced):**
1. magicoder:7b (excellent code balance, **FREE**)
2. qwen2.5:32b (premium intelligence, **FREE**) 
3. codellama:13b (solid code quality, **FREE**)
4. gemma:7b (Google's balanced model, **FREE**)
5. qwen2.5:7b-instruct (instruction-tuned, **FREE**)
6. qwen3:8b (multilingual reasoning, **FREE**)

**Cloud Models:**
5. claude-3.5-sonnet (excellent balance)
6. gpt-4o (strong all-around)
7. gemini-2.0-pro (good balance)
8. claude-sonnet-4 (reliable choice)

## Special Cases

### Multi-Model Consensus
For critical decisions, use 3+ diverse models:
- **Provider diversity**: Mix local + cloud (e.g., deepseek-r1:70b + claude-opus-4.1 + grok-4-fast-reasoning)
- **Capability diversity**: Mix reasoning + speed + accuracy leaders
- **Cost awareness**: Always include at least one FREE local model
- **Local + Cloud**: Best practice is 1-2 local models + 1-2 premium cloud models

### Fallback Chains
Primary → Secondary → Fallback (Local models prioritized):

**Code Generation:**
codellama:34b (local) → magicoder:7b (local) → gemma:7b (local) → grok-code-fast-1 → claude-sonnet-4.5 → deepseek-coder:1.3b (local)

**Reasoning:**
deepseek-r1:70b (local) → qwen2.5:32b (local) → qwen2.5:7b-instruct (local) → claude-opus-4.1 → grok-4-fast-reasoning → o1

**Creative Writing:**
qwen2.5:32b (local) → gemma:7b (local) → qwen3:8b (local) → claude-opus-4.1 → gpt-4.1-2025 → claude-sonnet-4.5

**Quick Tasks:**
deepseek-coder:1.3b (local) → llama3.2:3b (local) → gemma:7b (local) → llama3.1:8b (local) → gemini-2.0-flash → claude-3-haiku

**Vision:**
llama-3.2-90b (local, vision) → llama-3.2-11b (local, vision) → gpt-4o → grok-2-vision-1212

### Model Usage Guidelines

**Local Models - Production Ready:**
- deepseek-r1:70b: ✅ Production reasoning and analysis
- codellama:34b: ✅ Production code generation
- qwen2.5:32b: ✅ Production multilingual tasks
- magicoder:7b: ✅ Production code with validation
- gemma:7b: ✅ Production balanced tasks and conversations
- qwen2.5:7b-instruct: ✅ Production instruction-following tasks

**Local Models - Development/Testing:**
- llama3.2:3b: ⚠️ Quick prototyping only, validate for production
- deepseek-coder:1.3b: ⚠️ Rapid iteration, not final production code
- llama3.1:8b: ⚠️ General tasks, validate critical outputs

**Specialized Usage:**
- grok-2-vision-1212: Only for explicit image analysis tasks
- All vision models: Require explicit vision capability requests

## Context Window Requirements

### Minimum Context by Task
- Simple queries: 4K minimum
- Code files: 32K minimum
- Project analysis: 128K minimum
- Codebase review: 256K minimum
- Large documents: 1M+ required

### Auto-Upgrade Rules
If context_needed > model.context_window:
- Upgrade to next tier model
- Split task if possible
- Warn user about limitations

## Quality Gates

### Minimum Scores by Task Type
- Production Code: accuracy >= 0.85
- Financial Analysis: accuracy >= 0.9
- Creative Writing: creativity >= 0.8
- Customer Support: speed >= 0.7
- Research: reasoning_depth >= 0.8

### Validation Requirements

**Critical Tasks Requiring Multi-Model Consensus:**
- **Code deployment**: deepseek-r1:70b (local) + codellama:34b (local) + claude-opus-4.1 (cloud)
- **Financial decisions**: deepseek-r1:70b (local) + o1-pro (cloud) + claude-opus-4.1 (cloud)
- **Legal text**: claude-opus-4.1 + o1-pro + qwen2.5:32b (local validation)
- **Medical content**: Highest accuracy models + mandatory disclaimer

**Production Code Validation:**
- Use local models for initial development (codellama:34b, magicoder:7b)
- Validate with cloud models for critical systems (claude-sonnet-4.5, gpt-4o)
- Always test locally before cloud API costs

**Cost-Effective Validation:**
- Start with free local models
- Use cloud models only for final validation or complex edge cases
- Leverage local model speed for iterative development


# Model Usage Guidelines

**63 AI Models Across 8 Providers** - Your Complete Guide to Intelligent Model Orchestration

## 🎯 **Quick Start: Your Ready-to-Use Local Models**

### **✅ Currently Available (14 Local Models Installed)**

| Model | Size | RAM Usage | Best For | Speed | Quality |
|-------|------|-----------|----------|-------|---------|
| **deepseek-coder:1.3b** | 776 MB | ~2GB | Quick code snippets, testing | ⚡⚡⚡ | ⭐⭐⭐ |
| **llama3.2:3b** | 2.0 GB | ~4GB | Fast conversations, simple tasks | ⚡⚡⚡ | ⭐⭐⭐ |
| **magicoder:7b** | 3.8 GB | ~8GB | **🏆 Optimal code generation** | ⚡⚡ | ⭐⭐⭐⭐ |
| **llama3.1:8b** | 4.9 GB | ~8GB | Balanced general tasks | ⚡⚡ | ⭐⭐⭐ |
| **llama3:8b** | 4.7 GB | ~8GB | General conversations | ⚡⚡ | ⭐⭐⭐ |
| **qwen3:8b** | 5.2 GB | ~10GB | Multilingual, reasoning | ⚡⚡ | ⭐⭐⭐⭐ |
| **codellama:13b** | 7.4 GB | ~12GB | High-quality code, architecture | ⚡ | ⭐⭐⭐⭐ |
| **qwen2.5:32b** | 19 GB | ~25GB | Premium general intelligence | ⚡ | ⭐⭐⭐⭐⭐ |
| **codellama:34b** | 19 GB | ~30GB | **🏆 Best code quality** | ⚡ | ⭐⭐⭐⭐⭐ |
|| **deepseek-r1:70b** | 42 GB | ~35GB | **🏆 Ultimate reasoning** | ⚡ | ⭐⭐⭐⭐⭐ |
|| **llama3.1:70b** | 42 GB | ~42GB | **🆕 High-end reasoning & analysis** | ⚡ | ⭐⭐⭐⭐⭐ |
|| **gemma:7b** | 5.0 GB | ~8GB | **🆕 Google's balanced model** | ⚡⚡ | ⭐⭐⭐⭐ |
|| **qwen2.5:7b-instruct** | 4.7 GB | ~8GB | **🆕 Instruction-tuned Qwen** | ⚡⚡ | ⭐⭐⭐⭐ |

### **🔄 Total System Overview: 63 Models**

| Provider | Models | Status | Cost | Key Strengths |
|----------|--------|--------|------|---------------|
| **Local/Ollama** | 20 | ✅ Ready | **🆓 FREE** | Privacy, offline, zero cost |
| **OpenAI** | 11 | 🔑 API Key | 💰 Paid | GPT-4o, O1 reasoning, vision |
| **Bedrock** | 8 | 🏢 Enterprise | 💰 Paid | Enterprise Claude, Llama, Titan |
| **Anthropic** | 7 | 🔑 API Key | 💰 Paid | Claude 4.1 Opus, advanced reasoning |
| **Google** | 6 | 🔑 API Key | 💰 Paid | Gemini 2.0, 2M context |
| **xAI Grok** | 5 | 🔑 API Key | 💰 Paid | 2M context, vision, X integration |
| **Azure** | 4 | 🏢 Enterprise | 💰 Paid | Enterprise GPT-4, compliance |
| **DIAL** | 2 | 🏢 Enterprise | 💰 Paid | API gateway access |

---

## 🚀 **Scenario-Based Model Selection**

### **⚡ Code Development Workflow**

#### **Quick Prototyping & Testing**
```bash
# Use fastest model for iteration
./orchestrator-cli.py route "Write a Python function to parse JSON" --strategy speed_priority
# → Automatically selects: deepseek-coder:1.3b
```

#### **Production Code Development** ⭐ **RECOMMENDED**
```bash
# Use balanced quality/speed for daily coding
./orchestrator-cli.py route "Create a REST API with FastAPI" --strategy balanced
# → Automatically selects: magicoder:7b (optimal balance)
```

#### **Complex Code Architecture**
```bash
# Use highest quality for system design
./orchestrator-cli.py route "Design a microservices architecture" --strategy quality_first
# → Automatically selects: codellama:34b (best code quality)
```

#### **Code Review & Analysis**
```bash
# Use reasoning model for analysis
./orchestrator-cli.py route "Review this code for security issues: [code]" --strategy quality_first
# → Automatically selects: deepseek-r1:70b or codellama:34b
```

---

### **🧠 General Tasks**

#### **Fast Q&A and Conversations**
- **Best Choice**: `llama3.2:3b` (ultra-fast, good for simple queries)
- **Balanced**: `gemma:7b` (Google's balanced model with good performance)
- **Alternative**: `llama3.1:8b` (slightly better quality)

#### **Research and Analysis**
- **Best Choice**: `deepseek-r1:70b` (ultimate reasoning power)
- **Alternative**: `qwen2.5:32b` (excellent analysis, faster)

#### **Multilingual Tasks**
- **Best Choice**: `qwen2.5:32b` or `qwen2.5:7b-instruct` (strong multilingual capabilities)
- **Alternative**: `qwen3:8b` (excellent multilingual reasoning)

#### **Creative Writing**
- **Best Choice**: `qwen2.5:32b` (balanced creativity and quality)
- **Alternative**: `deepseek-r1:70b` (for complex creative tasks)

---

## 💡 **Cost Optimization Strategy**

### **Local Models = $0.00 Cost**
All your installed models cost nothing to run! Perfect for:
- Development and testing
- High-volume processing
- Privacy-sensitive tasks
- Learning and experimentation

### **Automatic Cost Optimization**
```bash
# This will ALWAYS prefer your local models
./orchestrator-cli.py route "Any task here" --strategy cost_optimize
```

---

## ⚙️ **Advanced Usage Patterns**

### **Multi-Model Workflows**

#### **Chain of Thought: Simple → Complex**
1. **Quick draft**: `deepseek-coder:1.3b` for initial code
2. **Refinement**: `magicoder:7b` for optimization
3. **Final review**: `codellama:34b` for production quality

#### **Parallel Development**
- **Frontend**: `magicoder:7b` (fast UI code)
- **Backend**: `codellama:13b` (solid architecture)
- **Documentation**: `qwen3:8b` (good writing capabilities)

### **Performance Tuning by RAM Usage**

#### **Low Memory Mode (~8GB available)**
```bash
# Stick to smaller models
PREFERRED_MODELS="deepseek-coder:1.3b,llama3.2:3b,magicoder:7b"
```

#### **High Performance Mode (20GB+ available)**
```bash
# Use premium models
PREFERRED_MODELS="codellama:34b,qwen2.5:32b,deepseek-r1:70b"
```

---

## 🔑 **Unlocking Cloud Models**

### **Setup Priority Order**

#### **1. OpenAI (Most Popular) 🤖**
```bash
# Sign up: https://platform.openai.com/api-keys
export OPENAI_API_KEY="your-openai-key-here"
```
**Unlocks**: GPT-4, GPT-4o, O1 reasoning models (11 models total)

#### **2. Anthropic (Best Reasoning) 🧠**
```bash
# Sign up: https://console.anthropic.com/
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```
**Unlocks**: Claude 4.1 Opus, Claude Sonnet 4.5 (7 models total)

#### **3. xAI Grok (Massive Context) ⚡**
```bash
# Sign up: https://console.x.ai/
export XAI_API_KEY="your-xai-key-here"
```
**Unlocks**: Grok models with 2M+ token context (5 models total)

#### **4. Google Gemini (Research) 🔍**
```bash
# Sign up: https://makersuite.google.com/app/apikey
export GOOGLE_API_KEY="your-google-key-here"
```
**Unlocks**: Gemini 2.0 Pro, Gemini Flash models (6 models total)

### **Enterprise Options**
- **Azure OpenAI** (4 models): Enterprise GPT-4 access with compliance
- **AWS Bedrock** (8 models): Claude + Llama + Titan via AWS managed service
- **DIAL Gateway** (2 models): Enterprise API gateway for model access

---

## 📊 **Performance Comparison**

### **Code Generation Quality Ranking**
1. **codellama:34b** - 95/100 (Highest quality, slower)
2. **magicoder:7b** - 92/100 (⭐ **Optimal balance**)
3. **codellama:13b** - 90/100 (Good quality, medium speed)
4. **qwen2.5:32b** - 85/100 (Excellent general model)
5. **deepseek-r1:70b** - 85/100 (Better for complex logic)

### **Speed Ranking**
1. **deepseek-coder:1.3b** - Ultra fast (0.98/1.0)
2. **llama3.2:3b** - Very fast (0.95/1.0)
3. **magicoder:7b** - Fast (0.90/1.0) ⭐
4. **llama3.1:8b** - Fast (0.90/1.0)
5. **qwen3:8b** - Good (0.85/1.0)

### **RAM Efficiency**
- **Under 8GB available**: `deepseek-coder:1.3b`, `llama3.2:3b`
- **8-16GB available**: `magicoder:7b`, `llama3.1:8b`, `qwen3:8b`
- **16-25GB available**: `codellama:13b`, `qwen2.5:32b`
- **25GB+ available**: `codellama:34b`, `deepseek-r1:70b`

---

## 🎯 **Recommended Daily Workflows**

### **Morning Setup** (Choose Your Default)
```bash
# For code-focused work
echo 'alias ai="./orchestrator-cli.py route"' >> ~/.zshrc
echo 'alias code-ai="./orchestrator-cli.py route --strategy balanced"' >> ~/.zshrc

# For research/analysis work  
echo 'alias research-ai="./orchestrator-cli.py route --strategy quality_first"' >> ~/.zshrc

# For quick questions
echo 'alias quick-ai="./orchestrator-cli.py route --strategy speed_priority"' >> ~/.zshrc
```

### **Development Sessions**

#### **Light Development** (8GB RAM available)
Primary: `magicoder:7b` - Perfect balance for most code tasks

#### **Heavy Development** (25GB+ RAM available)
Primary: `codellama:34b` - Maximum code quality
Secondary: `deepseek-r1:70b` - For complex problem solving

#### **Mixed Work** (Research + Code)
Primary: `qwen2.5:32b` - Excellent at both reasoning and code
Fallback: `magicoder:7b` - For pure code tasks

---

## 🔧 **Troubleshooting & Optimization**

### **Model Not Responding**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart if needed
./start-ollama.sh
```

### **Out of Memory Errors**
1. **Check current usage**: `ollama ps`
2. **Switch to smaller model**: Use 3B-8B models instead of 30B+
3. **Restart Ollama**: Clears model cache

### **Slow Performance**
1. **Use warmup script**: `./warmup-models.sh`
2. **Prefer smaller models**: 7B-13B range for speed
3. **Close other applications**: Free up RAM for models

---

## 📈 **Next Steps to Maximize Your Setup**

### **Immediate Actions**
1. ✅ **You have 9 local models ready** - $0 cost, full privacy
2. 🔧 **Set up 1-2 API keys** for cloud access when needed
3. 📚 **Try the recommended workflows** above

### **Expansion Options**
1. **More local models**: Add `starcoder2:7b`, `codegemma:7b` if available
2. **Cloud integration**: Start with OpenAI API key for GPT-4 access  
3. **Automation**: Create custom scripts for your most common tasks

### **Pro Tips**
- **Local-first strategy**: Use local models for 90% of tasks
- **Cloud for complexity**: Only use APIs for tasks requiring maximum quality
- **Cost monitoring**: Track API usage with built-in cost tracking
- **Privacy**: Keep sensitive code/data on local models only

---

## 🏆 **Your Optimal Configuration Summary**

**For Code Development**:
- **Quick tasks**: `deepseek-coder:1.3b` (instant responses)
- **Daily coding**: `magicoder:7b` (⭐ **sweet spot**)
- **Complex projects**: `codellama:34b` (maximum quality)

**For General Tasks**:
- **Fast Q&A**: `llama3.2:3b`
- **Research**: `deepseek-r1:70b` (when you have 35GB+ RAM)
- **Balanced work**: `qwen2.5:32b`

**Cloud Enhancement Options**:
- **Ultimate reasoning**: O1 Pro (OpenAI) or Claude Opus 4.1
- **Vision tasks**: GPT-4o or Grok 2 Vision
- **Massive context**: Grok 4 Fast (2M tokens) or Gemini 2.0 Pro

**Memory Management**:
- Total local models: 20 available, 14 currently installed
- Model storage: ~110GB for all installed models
- Concurrent usage: Use 1-2 models at a time for optimal performance
- Your hardware: Supports up to ~42GB models (70B parameters)
- **New models**: llama3.1:70b, gemma:7b, qwen2.5:7b-instruct

**System Overview**:
- **Total Models Available**: 63 across 8 providers
- **Local Models (Free)**: 20 models, 14 installed
- **Cloud Models (Paid)**: 43 models across 7 providers
- **Enterprise Options**: Azure (4), Bedrock (8), DIAL (2)

🎉 **You now have access to a professional-grade AI orchestration system with 63 total models across all major providers!**

