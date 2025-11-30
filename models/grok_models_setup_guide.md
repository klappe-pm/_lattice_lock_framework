# Grok Models Setup Guide

## Overview
This setup provides direct access to **5 xAI Grok models** integrated with the Power Prompts orchestration system, including Grok-4 variants with 2M context windows.

## Available Models (5 total)

### Language Models (4 models)
- **grok-4-fast-reasoning** (2M tokens) - Ultimate reasoning with function calling
- **grok-4-fast-non-reasoning** (2M tokens) - Fast inference with massive context
- **grok-code-fast-1** (256K tokens) - Code generation specialist
- **grok-3** (131K tokens) - General purpose model

### Vision Models (1 model)
- **grok-2-vision-1212** (32K tokens) - Image analysis and vision tasks

### Model Capabilities
| Model | Context | Strengths | Cost (Input/Output) |
|-------|---------|-----------|---------------------|
| grok-4-fast-reasoning | **2M** | Complex reasoning, analysis | $2/$6 per M tokens |
| grok-4-fast-non-reasoning | **2M** | Fast processing, summaries | $1/$3 per M tokens |
| grok-code-fast-1 | 256K | Code generation, debugging | $1.5/$4.5 per M tokens |
| grok-3 | 131K | General tasks, conversations | $1/$3 per M tokens |
| grok-2-vision-1212 | 32K | Image analysis, vision | $2/$6 per M tokens |

## Setup Instructions

### 1. Prerequisites

```bash
# Install required Python packages
pip install requests pyyaml

# Set your xAI API key
export XAI_API_KEY='your-api-key-here'

# Add to your shell profile for persistence
echo "export XAI_API_KEY='your-api-key-here'" >> ~/.zshrc  # or ~/.bashrc
```

### 2. Files Created
- `grok_models_config.yaml` - Complete model catalog and configuration
- `grok_api.py` - Python API client with full feature support
- `grok.sh` - Convenient shell wrapper for quick access
- `GROK_SETUP.md` - This setup guide

### 3. Basic Usage
#### Using the Shell Wrapper

```bash
# List all available models
./grok.sh list

# Quick chat with default Grok-3
./grok.sh quick "Explain quantum computing"

# Use the 2M context reasoning model
./grok.sh chat -m grok4-fast -p "Analyze this large document..."

# Code-focused query
./grok.sh code "Write a Python async web server"

# Vision model with image
./grok.sh vision -i screenshot.png -p "What's in this image?"

# Generate an image
./grok.sh generate -p "A futuristic city at sunset"

# Stream responses
./grok.sh chat -m grok4 -p "Tell me a story" -s

# Get model info
./grok.sh info -m grok-4-fast-reasoning
```

#### Using Python Directly

```python
from grok_api import GrokAPI

# Initialize client
api = GrokAPI()

# List all models
models = api.list_models()
for model in models:
    print(f"{model['id']}: {model['description']}")

# Chat completion
response = api.chat_completion(
    model_id="grok-4-fast-reasoning",  # 2M context!
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ]
)
print(response['choices'][0]['message']['content'])

# Vision with image
response = api.vision_completion(
    model_id="grok-2-vision-1212",
    messages=[{"role": "user", "content": "Describe this image"}],
    image_path="screenshot.png"
)

# Generate image
result = api.image_generation(
    prompt="A cyberpunk city",
    model_id="grok-2-image-1212"
)

# Stream responses
for chunk in api.stream_completion("grok4", messages):
    # Process streaming chunks
    pass
```

### 4. Integration with Other Tools

#### As a Command Line Tool

```bash
# Add to PATH for global access
sudo ln -s "$(pwd)/grok.sh" /usr/local/bin/grok

# Now use from anywhere
grok list
grok chat -m grok4-fast -p "Your prompt here"
```

#### In Scripts

```bash
#!/bin/bash
# Use in your scripts
response=$(./grok.sh chat -m grok-3 -p "Generate a summary")
echo "$response"
```

#### As a Python Module

```python
# Import in your Python projects
import sys
sys.path.append('/Users/kevinlappe/Obsidian/Power Prompts')
from grok_api import GrokAPI

api = GrokAPI()
# Use the API...
```

### 5. Model Selection Guide

#### For Code Tasks
- **First choice**: `grok-code-fast-1` (256K context, optimized for code)
- **Alternative**: `grok-3` for general coding with enterprise features

#### For Reasoning & Analysis
- **First choice**: `grok-4-fast-reasoning` (2M context! Best for large documents)
- **Alternative**: `grok-4-0709` (256K context, solid reasoning)

#### For Fast Responses
- **First choice**: `grok-3-fast` (131K context, higher performance)
- **Alternative**: `grok-4-fast-non-reasoning` (2M context, lighter inference)

#### For Efficiency
- **First choice**: `grok-3-mini` (131K context, compact and efficient)

#### For Vision Tasks
- **Only option**: `grok-2-vision-1212` (32K context, handles images up to 20MB)

#### For Image Generation
- **Only option**: `grok-2-image-1212`

### 6. Advanced Features

#### Using Aliases
```bash
# Use convenient aliases instead of full model IDs
./grok.sh chat -m grok4-fast -p "..."  # Uses grok-4-fast-reasoning
./grok.sh chat -m grok-code -p "..."    # Uses grok-code-fast-1
```

#### Region Selection (Vision)
The vision model is available in multiple regions:
- US East (us-east-1): 600 requests/min rate limit
- EU West (eu-west-1): 50 requests/min rate limit

#### Rate Limits
Each model has different rate limits. Check `grok_models_config.yaml` for details.

### 7. Troubleshooting

#### API Key Issues
```bash
# Check if key is set
echo $XAI_API_KEY

# Test API connection
./grok.sh list
```

#### Python Dependencies
```bash
# Ensure packages are installed
pip install requests pyyaml

# Check Python version (3.6+ required)
python3 --version
```

#### Permission Issues
```bash
# Make scripts executable
chmod +x grok.sh
chmod +x grok_api.py
```

### 8. Updating Models
To add new models as they become available:

1. Edit `grok_models_config.yaml`
2. Add new model entries under appropriate category
3. Add aliases if desired
4. Models are immediately available in both CLI and Python

## Summary

You now have complete access to all Grok models including:
- The new **2M context** Grok-4 models
- Specialized code, vision, and image generation models
- Convenient CLI and Python interfaces
- No dependency on Zen MCP configuration

Use `./grok.sh --help` for quick reference or check the examples above.