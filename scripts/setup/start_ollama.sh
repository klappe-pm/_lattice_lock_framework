#!/bin/bash
# Ollama Startup Script for Power Prompts
# Starts Ollama service and verifies connectivity

set -e

echo "🚀 Power Prompts - Ollama Startup Script"
echo "========================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_HOST="localhost"
OLLAMA_PORT="11434"
OLLAMA_URL="http://${OLLAMA_HOST}:${OLLAMA_PORT}"

# Check if Ollama is installed
check_ollama_installed() {
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}❌ Ollama not found!${NC}"
        echo "Please install Ollama first:"
        echo "  curl -fsSL https://ollama.com/install.sh | sh"
        echo "Or visit: https://ollama.com"
        exit 1
    fi
    echo -e "${GREEN}✅ Ollama found: $(ollama --version)${NC}"
}

# Check if Ollama service is running
check_ollama_running() {
    if curl -s "${OLLAMA_URL}/api/version" > /dev/null 2>&1; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Start Ollama service
start_ollama() {
    echo -e "${YELLOW}🔄 Starting Ollama service...${NC}"
    
    # Try to start as system service first (macOS with brew)
    if command -v brew &> /dev/null && brew services list | grep -q ollama; then
        echo "Starting via Homebrew services..."
        brew services start ollama
        sleep 5
    else
        # Start manually in background
        echo "Starting Ollama manually..."
        nohup ollama serve > ollama.log 2>&1 &
        sleep 3
    fi
    
    # Wait up to 30 seconds for service to start
    echo "Waiting for service to start..."
    for i in {1..30}; do
        if check_ollama_running; then
            echo -e "${GREEN}✅ Ollama service started successfully${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo -e "\n${RED}❌ Failed to start Ollama service${NC}"
    echo "Check the logs: tail -f ollama.log"
    return 1
}

# Show service status
show_status() {
    echo -e "\n${BLUE}📊 Service Status:${NC}"
    
    if check_ollama_running; then
        echo -e "${GREEN}✅ Ollama service is running${NC}"
        echo "   URL: ${OLLAMA_URL}"
        
        # Get version info
        version_info=$(curl -s "${OLLAMA_URL}/api/version" 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "   Version: $(echo $version_info | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])" 2>/dev/null || echo "unknown")"
        fi
    else
        echo -e "${RED}❌ Ollama service is not running${NC}"
        return 1
    fi
}

# List installed models
list_models() {
    echo -e "\n${BLUE}📋 Installed Models:${NC}"
    
    if check_ollama_running; then
        models=$(ollama list 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$models" ]; then
            echo "$models"
        else
            echo -e "${YELLOW}⚠️  No models installed${NC}"
            echo "Install a model with: ollama pull llama3.2:8b"
        fi
    else
        echo -e "${RED}❌ Cannot list models - service not running${NC}"
    fi
}

# Test model connectivity
test_model() {
    local model="${1:-llama3.2:8b}"
    
    echo -e "\n${BLUE}🧪 Testing Model: ${model}${NC}"
    
    if ! ollama list | grep -q "$model"; then
        echo -e "${YELLOW}⚠️  Model $model not installed${NC}"
        echo "Install with: ollama pull $model"
        return 1
    fi
    
    echo "Running test query..."
    response=$(ollama run "$model" "What is 1+1? Answer with just the number." 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Model test successful${NC}"
        echo "Response: $response"
    else
        echo -e "${RED}❌ Model test failed${NC}"
        return 1
    fi
}

# Show help
show_help() {
    echo "Ollama Startup Script for Power Prompts"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -s, --status   Show service status only"
    echo "  -t, --test MODEL Test specific model (default: llama3.2:8b)"
    echo "  -q, --quiet    Quiet mode - minimal output"
    echo ""
    echo "Examples:"
    echo "  $0              # Start service and show status"
    echo "  $0 --status     # Check if service is running"
    echo "  $0 --test llama3.1:8b  # Test specific model"
}

# Parse command line arguments
QUIET=false
STATUS_ONLY=false
TEST_MODEL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--status)
            STATUS_ONLY=true
            shift
            ;;
        -t|--test)
            TEST_MODEL="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    if [ "$QUIET" = false ]; then
        check_ollama_installed
    fi
    
    if [ "$STATUS_ONLY" = true ]; then
        show_status
        exit $?
    fi
    
    if [ -n "$TEST_MODEL" ]; then
        if ! check_ollama_running; then
            echo -e "${RED}❌ Ollama service not running${NC}"
            exit 1
        fi
        test_model "$TEST_MODEL"
        exit $?
    fi
    
    # Main startup flow
    if check_ollama_running; then
        if [ "$QUIET" = false ]; then
            echo -e "${GREEN}✅ Ollama is already running${NC}"
        fi
    else
        start_ollama || exit 1
    fi
    
    if [ "$QUIET" = false ]; then
        show_status
        list_models
        
        echo -e "\n${GREEN}🎉 Ollama is ready for Power Prompts!${NC}"
        echo -e "\n${BLUE}Next steps:${NC}"
        echo "1. Install models: ollama pull llama3.2:8b"
        echo "2. Test orchestrator: ./orchestrator-cli.py test"
        echo "3. Analyze tasks: ./orchestrator-cli.py analyze 'your prompt'"
    fi
}

# Run main function
main "$@"