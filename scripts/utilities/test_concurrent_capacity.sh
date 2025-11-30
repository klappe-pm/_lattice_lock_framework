#!/bin/bash

# Test concurrent model execution capacity
# Runs multiple models simultaneously to maximize RAM usage
# Tests true parallel execution with overlapping requests

echo "=================================================="
echo "Concurrent Model Capacity Test"
echo "=================================================="
echo ""

# Models to test concurrently (all available on 32GB+ tier)
MODELS=(
    "deepseek-coder:1.3b"
    "llama3.2:3b"
    "magicoder:7b"
    "llama3.1:8b"
    "qwen2.5:7b-instruct"
    "codellama:13b"
    "qwen2.5:32b"
)

# Test prompts for each model (representative of actual workload)
declare -A PROMPTS
PROMPTS["deepseek-coder:1.3b"]="Write a Python function to calculate fibonacci numbers"
PROMPTS["llama3.2:3b"]="Explain the concept of recursion in programming"
PROMPTS["magicoder:7b"]="Create a REST API endpoint for user authentication"
PROMPTS["llama3.1:8b"]="Write comprehensive documentation for a Python class"
PROMPTS["qwen2.5:7b-instruct"]="Explain the SOLID principles in software development"
PROMPTS["codellama:13b"]="Refactor this code for better performance and maintainability"
PROMPTS["qwen2.5:32b"]="Design a scalable microservices architecture for an e-commerce platform"

echo "Starting concurrent model execution test..."
echo "Running ${#MODELS[@]} models simultaneously"
echo ""

# Function to run a model with timing
run_model() {
    local model=$1
    local prompt="${PROMPTS[$model]}"
    local start_time=$(date +%s)

    echo "[$(date '+%H:%M:%S')] 🚀 Starting: $model"

    # Run model with actual workload (not just 'test')
    local response=$(ollama run "$model" "$prompt" 2>&1)
    local status=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ $status -eq 0 ]; then
        echo "[$(date '+%H:%M:%S')] ✅ Completed: $model (${duration}s)"
    else
        echo "[$(date '+%H:%M:%S')] ❌ Failed: $model (${duration}s)"
    fi
}

# Export function for parallel execution
export -f run_model

# Declare associative array for parallel use
declare -p PROMPTS > /tmp/prompts.sh
source /tmp/prompts.sh

# Launch all models in parallel
for model in "${MODELS[@]}"; do
    run_model "$model" &
done

# Wait a few seconds then check what's loaded
sleep 5

echo ""
echo "=================================================="
echo "Checking loaded models after 5 seconds..."
echo "=================================================="
echo ""

ollama ps

echo ""
echo "RAM Usage:"
ps aux | grep -i "ollama" | grep -v grep | awk '{printf "  %-50s %5.2f GB\n", substr($11,1,50), $6/1024/1024}'

echo ""
echo "Waiting for all models to complete..."

# Wait for all background jobs
wait

echo ""
echo "=================================================="
echo "Test Complete - Final Status"
echo "=================================================="
echo ""

ollama ps

echo ""
echo "Final RAM Usage:"
ps aux | grep -i "ollama" | grep -v grep | awk '{printf "  %-50s %5.2f GB\n", substr($11,1,50), $6/1024/1024}'

# Get final RAM stats
FINAL_RAM=$(vm_stat | awk '/Pages free/ {free=$3} /Pages active/ {active=$3} /Pages inactive/ {inactive=$3} /Pages wired/ {wired=$4} END {page_size=4096; total_used=(active+wired)*page_size/1024/1024/1024; printf "%.2f", total_used}')

echo ""
echo "Total System RAM Usage: ${FINAL_RAM} GB / 36 GB"
echo ""
echo "=================================================="
echo "Concurrent execution capacity verified"
echo "=================================================="
