#!/bin/bash
# Grok Models Quick Access Wrapper
# Easy CLI interface for all Grok models

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check for XAI_API_KEY
if [ -z "$XAI_API_KEY" ]; then
    echo -e "${RED}Error: XAI_API_KEY environment variable not set${NC}"
    echo "Please set it with: export XAI_API_KEY='your-api-key'"
    exit 1
fi

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/grok_api.py"

# Function to display help
show_help() {
    cat << EOF
${CYAN}Grok Models CLI - Access all xAI Grok models${NC}

${YELLOW}Usage:${NC}
  ./grok.sh [command] [options]

${YELLOW}Commands:${NC}
  ${GREEN}list${NC}              List all available models
  ${GREEN}list-code${NC}         List code-focused models
  ${GREEN}list-vision${NC}       List vision models
  ${GREEN}list-large${NC}        List models with >1M context
  ${GREEN}chat${NC}              Chat with a model
  ${GREEN}vision${NC}            Use vision model with image
  ${GREEN}generate${NC}          Generate an image
  ${GREEN}info${NC}              Get model information
  ${GREEN}quick${NC}             Quick chat with default model
  ${GREEN}code${NC}              Use code-optimized model
  ${GREEN}reason${NC}            Use reasoning model (2M context)

${YELLOW}Options:${NC}
  -m, --model MODEL     Specify model ID or alias
  -p, --prompt PROMPT   Input prompt
  -i, --image PATH      Image file for vision models
  -s, --stream          Stream responses
  -h, --help            Show this help message

${YELLOW}Model Aliases:${NC}
  ${PURPLE}grok${NC}              → grok-3 (standard)
  ${PURPLE}grok-mini${NC}         → grok-3-mini (compact)
  ${PURPLE}grok-code${NC}         → grok-code-fast-1 (code-focused)
  ${PURPLE}grok4${NC}             → grok-4-0709 (reasoning)
  ${PURPLE}grok4-fast${NC}        → grok-4-fast-reasoning (2M context!)
  ${PURPLE}grok-vision${NC}       → grok-2-vision-1212
  ${PURPLE}grok-image${NC}        → grok-2-image-1212

${YELLOW}Examples:${NC}
  # List all models with details
  ./grok.sh list

  # Quick chat with default Grok-3
  ./grok.sh quick "Explain quantum computing"

  # Use the 2M context reasoning model
  ./grok.sh chat -m grok4-fast -p "Analyze this codebase..."

  # Code-focused query
  ./grok.sh code "Write a Python async web server"

  # Vision model with image
  ./grok.sh vision -i screenshot.png -p "What's in this image?"

  # Generate an image
  ./grok.sh generate -p "A futuristic city at sunset"

  # Stream responses
  ./grok.sh chat -m grok4 -p "Tell me a story" -s

EOF
}

# Function to list models with formatting
list_models() {
    echo -e "${CYAN}Available Grok Models:${NC}"
    python3 "$PYTHON_SCRIPT" list --category "$1"
}

# Parse command
case "$1" in
    list)
        list_models
        ;;
    list-code)
        echo -e "${CYAN}Code-Focused Models:${NC}"
        python3 "$PYTHON_SCRIPT" list | grep -E "(code|Code)"
        ;;
    list-vision)
        echo -e "${CYAN}Vision Models:${NC}"
        python3 "$PYTHON_SCRIPT" list --category vision
        ;;
    list-large)
        echo -e "${CYAN}Large Context Models (>1M tokens):${NC}"
        python3 "$PYTHON_SCRIPT" list | grep -E "2000000|1000000"
        ;;
    chat)
        shift
        python3 "$PYTHON_SCRIPT" chat "$@"
        ;;
    vision)
        shift
        python3 "$PYTHON_SCRIPT" vision "$@"
        ;;
    generate)
        shift
        python3 "$PYTHON_SCRIPT" image "$@"
        ;;
    info)
        shift
        python3 "$PYTHON_SCRIPT" info "$@"
        ;;
    quick)
        shift
        prompt="${1:-Hello, what can you help with today?}"
        echo -e "${BLUE}Using Grok-3 (standard model)...${NC}"
        python3 "$PYTHON_SCRIPT" chat -m grok-3 -p "$prompt"
        ;;
    code)
        shift
        prompt="${1:-Write a hello world program}"
        echo -e "${BLUE}Using Grok Code Fast model...${NC}"
        python3 "$PYTHON_SCRIPT" chat -m grok-code-fast-1 -p "$prompt"
        ;;
    reason)
        shift
        prompt="${1:-Provide a thoughtful analysis}"
        echo -e "${BLUE}Using Grok-4 Fast Reasoning (2M context)...${NC}"
        python3 "$PYTHON_SCRIPT" chat -m grok-4-fast-reasoning -p "$prompt"
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            echo -e "${RED}Unknown command: $1${NC}"
            echo "Use './grok.sh --help' for usage information"
            exit 1
        fi
        ;;
esac