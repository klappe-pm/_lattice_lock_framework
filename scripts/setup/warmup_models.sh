#!/bin/bash
# Model Warmup Script for Power Prompts
# Pre-loads frequently used models to improve response times

set -e

echo "🔥 Power Prompts - Model Warmup Script"
echo "======================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_URL="http://localhost:11434"

# Default models to warm up (from small to large)
DEFAULT_MODELS=(
    "llama3.2:3b"
    "llama3.2:8b" 
    "llama3.1:8b"
    "llama3.2:11b-vision"
    "codellama:13b-code"
    "qwen2.5:32b-instruct-q4_K_M"
    "llama3.1:70b"
    "llama3.2:90b"
)

# Check if Ollama is running
check_ollama() {
    if ! curl -s "${OLLAMA_URL}/api/version" > /dev/null 2>&1; then
        echo -e "${RED}❌ Ollama service not running${NC}"
        echo "Start it with: ./start-ollama.sh"
        exit 1
    fi
    echo -e "${GREEN}✅ Ollama service is running${NC}"
}

# Get list of installed models
get_installed_models() {
    ollama list --format json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'models' in data:
        for model in data['models']:
            print(model['name'])
    else:
        # Fallback for older Ollama versions
        pass
except:
    pass
" 2>/dev/null || ollama list | tail -n +2 | awk '{print $1}' | grep -v '^$'
}

# Warm up a single model
warmup_model() {
    local model="$1"
    local test_prompt="${2:-Hello}"
    
    echo -e "${BLUE}🔄 Warming up ${model}...${NC}"
    
    # Check if model is installed
    if ! ollama list | grep -q "$model"; then
        echo -e "${YELLOW}⚠️  Model $model not installed, skipping${NC}"
        return 1
    fi
    
    # Run a simple test to load the model
    start_time=$(date +%s)
    
    # Use a very simple prompt to minimize processing time
    response=$(ollama run "$model" "$test_prompt" --verbose=false 2>/dev/null)
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $model ready (${duration}s)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to warm up $model${NC}"
        return 1
    fi
}

# Show memory usage
show_memory_usage() {
    echo -e "\n${BLUE}📊 Memory Usage:${NC}"
    
    # Show Ollama processes
    if command -v ollama &> /dev/null; then
        ollama ps 2>/dev/null || echo "No models currently loaded"
    fi
    
    # Show system memory (macOS)
    if command -v vm_stat &> /dev/null; then
        echo -e "\n${BLUE}System Memory:${NC}"
        vm_stat | head -4
    fi
}

# Estimate model sizes
show_model_info() {
    echo -e "\n${BLUE}📋 Model Information:${NC}"
    echo "┌─────────────────────┬─────────────┬─────────────┬─────────────────────────┐"
    echo "│ Model               │ Size        │ RAM Needed  │ Best For                │"
    echo "├─────────────────────┼─────────────┼─────────────┼─────────────────────────┤"
    echo "│ llama3.2:3b        │ ~2GB        │ 4-6GB       │ Fast chat, simple tasks │"
    echo "│ llama3.2:8b        │ ~5GB        │ 8-12GB      │ Balanced performance    │"
    echo "│ llama3.1:8b        │ ~5GB        │ 8-12GB      │ Balanced performance    │"
    echo "│ llama3.2:11b-vision│ ~7GB        │ 12-16GB     │ Vision + text tasks     │"
    echo "│ codellama:13b-code │ ~8GB        │ 16-20GB     │ Code generation         │"
    echo "│ qwen2.5:32b-q4_K_M │ ~20GB       │ 20-32GB     │ Multilingual, tools     │"
    echo "│ llama3.1:70b       │ ~40GB       │ 64-80GB     │ High-quality reasoning  │"
    echo "│ llama3.2:90b       │ ~50GB       │ 80-100GB    │ Top-tier performance    │"
    echo "└─────────────────────┴─────────────┴─────────────┴─────────────────────────┘"
}

# Show help
show_help() {
    echo "Model Warmup Script for Power Prompts"
    echo ""
    echo "Usage: $0 [options] [models...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -a, --all      Warm up all installed models"
    echo "  -s, --status   Show memory usage and loaded models"
    echo "  -i, --info     Show model information table"
    echo "  -f, --fast     Quick warmup (minimal test prompts)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Warm up default models"
    echo "  $0 --all                     # Warm up all installed models"
    echo "  $0 llama3.2:8b llama3.1:8b  # Warm up specific models"
    echo "  $0 --status                  # Show current status"
    echo ""
    echo "Default models:"
    for model in "${DEFAULT_MODELS[@]}"; do
        echo "  - $model"
    done
}

# Parse command line arguments
ALL_MODELS=false
STATUS_ONLY=false
SHOW_INFO=false
FAST_MODE=false
CUSTOM_MODELS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            ALL_MODELS=true
            shift
            ;;
        -s|--status)
            STATUS_ONLY=true
            shift
            ;;
        -i|--info)
            SHOW_INFO=true
            shift
            ;;
        -f|--fast)
            FAST_MODE=true
            shift
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
        *)
            CUSTOM_MODELS+=("$1")
            shift
            ;;
    esac
done

# Main execution
main() {
    check_ollama
    
    if [ "$STATUS_ONLY" = true ]; then
        show_memory_usage
        exit 0
    fi
    
    if [ "$SHOW_INFO" = true ]; then
        show_model_info
        exit 0
    fi
    
    # Determine which models to warm up
    local models_to_warmup=()
    
    if [ ${#CUSTOM_MODELS[@]} -gt 0 ]; then
        models_to_warmup=("${CUSTOM_MODELS[@]}")
        echo -e "${BLUE}Warming up custom models: ${models_to_warmup[*]}${NC}"
    elif [ "$ALL_MODELS" = true ]; then
        echo -e "${BLUE}Getting list of all installed models...${NC}"
        while IFS= read -r model; do
            [ -n "$model" ] && models_to_warmup+=("$model")
        done < <(get_installed_models)
        echo -e "${BLUE}Found ${#models_to_warmup[@]} installed models${NC}"
    else
        models_to_warmup=("${DEFAULT_MODELS[@]}")
        echo -e "${BLUE}Warming up default models${NC}"
    fi
    
    if [ ${#models_to_warmup[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No models to warm up${NC}"
        echo "Install models with: ollama pull llama3.2:8b"
        exit 1
    fi
    
    # Set test prompt based on mode
    local test_prompt="Hi"
    if [ "$FAST_MODE" = false ]; then
        test_prompt="What is the capital of France? Answer in one word."
    fi
    
    # Warm up models
    echo -e "\n${BLUE}🔥 Starting warmup process...${NC}"
    local successful=0
    local failed=0
    
    for model in "${models_to_warmup[@]}"; do
        if warmup_model "$model" "$test_prompt"; then
            ((successful++))
        else
            ((failed++))
        fi
    done
    
    # Summary
    echo -e "\n${BLUE}📊 Warmup Summary:${NC}"
    echo -e "${GREEN}✅ Successful: $successful${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "${RED}❌ Failed: $failed${NC}"
    fi
    
    # Show final status
    show_memory_usage
    
    echo -e "\n${GREEN}🎉 Model warmup complete!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "1. Test orchestrator: ./orchestrator-cli.py analyze 'your prompt'"
    echo "2. Check model selection: ./orchestrator-cli.py route 'your task' --strategy cost_optimize"
    echo "3. Monitor usage: ollama ps"
}

# Run main function
main "$@"