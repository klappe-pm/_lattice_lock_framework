#!/bin/bash

# Model Orchestrator Setup Script
# Sets up the complete orchestration system with all dependencies

echo "="
echo "Model Orchestrator Setup"
echo "="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher required (found $python_version)"
    exit 1
fi

echo "✓ Python version: $python_version"

# Install dependencies
echo -e "\nInstalling dependencies..."

pip3 install -q --upgrade pip

# Core dependencies
pip3 install -q requests aiohttp pyyaml numpy rich tenacity

echo "✓ Dependencies installed"

# Make scripts executable
echo -e "\nMaking scripts executable..."

chmod +x orchestrator_cli.py 2>/dev/null || true
chmod +x grok.sh 2>/dev/null || true
chmod +x grok_api.py 2>/dev/null || true
chmod +x model_orchestrator.py 2>/dev/null || true
chmod +x model_orchestrator_v2.py 2>/dev/null || true
chmod +x zen_mcp_bridge.py 2>/dev/null || true

echo "✓ Scripts made executable"

# Check for API keys
echo -e "\nChecking API keys..."

api_keys_found=0
missing_keys=""

if [ -n "$XAI_API_KEY" ]; then
    echo "✓ XAI_API_KEY found (Grok models)"
    api_keys_found=$((api_keys_found + 1))
else
    missing_keys="$missing_keys XAI_API_KEY"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OPENAI_API_KEY found"
    api_keys_found=$((api_keys_found + 1))
else
    missing_keys="$missing_keys OPENAI_API_KEY"
fi

if [ -n "$GOOGLE_API_KEY" ]; then
    echo "✓ GOOGLE_API_KEY found"
    api_keys_found=$((api_keys_found + 1))
else
    missing_keys="$missing_keys GOOGLE_API_KEY"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY found"
    api_keys_found=$((api_keys_found + 1))
else
    missing_keys="$missing_keys ANTHROPIC_API_KEY"
fi

if [ -n "$DIAL_API_KEY" ]; then
    echo "✓ DIAL_API_KEY found"
    api_keys_found=$((api_keys_found + 1))
else
    missing_keys="$missing_keys DIAL_API_KEY"
fi

if [ $api_keys_found -eq 0 ]; then
    echo -e "\n⚠️  No API keys found. Set at least one:"
    echo "  export XAI_API_KEY='your-key'"
    echo "  export OPENAI_API_KEY='your-key'"
    echo "  export GOOGLE_API_KEY='your-key'"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo "  export DIAL_API_KEY='your-key'"
else
    echo -e "\n✓ Found $api_keys_found API key(s)"
    if [ -n "$missing_keys" ]; then
        echo "ℹ️  Optional keys not set:$missing_keys"
    fi
fi

# Create alias for easy access
echo -e "\nSetting up command aliases..."

# Add to current session
alias orchestrator="python3 $(pwd)/orchestrator_cli.py"
alias orch="python3 $(pwd)/orchestrator_cli.py"

# Offer to add to shell profile
echo -e "\nWould you like to add 'orchestrator' command to your shell profile? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    shell_profile=""
    
    if [ -n "$ZSH_VERSION" ]; then
        shell_profile="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        shell_profile="$HOME/.bashrc"
    fi
    
    if [ -n "$shell_profile" ]; then
        echo "" >> "$shell_profile"
        echo "# Model Orchestrator" >> "$shell_profile"
        echo "alias orchestrator='python3 $(pwd)/orchestrator_cli.py'" >> "$shell_profile"
        echo "alias orch='python3 $(pwd)/orchestrator_cli.py'" >> "$shell_profile"
        echo "✓ Added to $shell_profile"
        echo "  Run 'source $shell_profile' to use immediately"
    fi
fi

# Test the installation
echo -e "\n"
echo "Testing installation..."
echo ""

python3 orchestrator_cli.py test 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "\n✅ Setup complete!"
    echo ""
    echo "Quick Start Commands:"
    echo "  ./orchestrator_cli.py list          # List all models"
    echo "  ./orchestrator_cli.py analyze 'your prompt'  # Analyze task"
    echo "  ./orchestrator_cli.py route 'your prompt'    # Route request"
    echo "  ./orchestrator_cli.py consensus 'your prompt' # Multi-model consensus"
    echo "  ./orchestrator_cli.py cost          # Show cost report"
    echo ""
    echo "Or use the alias: orchestrator [command]"
else
    echo -e "\n⚠️  Setup complete but test failed. Check your API keys."
fi