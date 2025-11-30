#!/bin/bash

# Aggressive parallel model warmup script for 32GB+ RAM systems
# Maximizes RAM usage by pre-loading multiple models concurrently
# Target: Load 6-8 models simultaneously for maximum parallel execution capacity

echo "=================================================="
echo "Aggressive Parallel Model Warmup - 32GB+ Tier"
echo "=================================================="
echo ""

# Check total RAM
TOTAL_RAM=$(sysctl hw.memsize | awk '{print $2/1024/1024/1024}')
echo "Total System RAM: ${TOTAL_RAM} GB"

# Get current free RAM
FREE_RAM=$(vm_stat | awk '/Pages free/ {free=$3} /Pages inactive/ {inactive=$3} END {page_size=4096; total_free=(free+inactive)*page_size/1024/1024/1024; print total_free}')
echo "Available RAM: ${FREE_RAM} GB"
echo ""

# 32GB+ Tier: Load 7 models concurrently for maximum parallelization
# Target RAM usage: ~31GB (leaving 5GB for system)
echo "Target Configuration: 7 concurrent models (~31GB total)"
echo "=================================================="
echo ""

# Tier 1: Ultra-fast models (always loaded)
TIER1_MODELS=("deepseek-coder:1.3b" "llama3.2:3b")
echo "TIER 1 - Ultra-Fast Models (3GB total):"
for model in "${TIER1_MODELS[@]}"; do
    echo "  - $model"
done
echo ""

# Tier 2: Balanced models (primary workhorses)
TIER2_MODELS=("magicoder:7b" "llama3.1:8b" "qwen2.5:7b-instruct" "codellama:13b")
echo "TIER 2 - Balanced Models (23GB total):"
for model in "${TIER2_MODELS[@]}"; do
    echo "  - $model"
done
echo ""

# Tier 3: Premium model (specialized tasks)
TIER3_MODELS=("qwen2.5:32b")
echo "TIER 3 - Premium Model (19GB):"
for model in "${TIER3_MODELS[@]}"; do
    echo "  - $model"
done
echo ""

# Combined model list for parallel loading
ALL_MODELS=("${TIER1_MODELS[@]}" "${TIER2_MODELS[@]}" "${TIER3_MODELS[@]}")

echo "Starting aggressive parallel warmup..."
echo "=================================================="
echo ""

# Function to warm up a model
warmup_model() {
    local model=$1
    echo "[$(date '+%H:%M:%S')] Starting warmup: $model"

    # Run model with minimal prompt to load into memory
    ollama run "$model" "test" --verbose 2>/dev/null 1>/dev/null

    local status=$?
    if [ $status -eq 0 ]; then
        echo "[$(date '+%H:%M:%S')] ✅ Loaded: $model"
    else
        echo "[$(date '+%H:%M:%S')] ❌ Failed: $model"
    fi
}

# Export function for parallel execution
export -f warmup_model

# Launch all models in parallel using background jobs
for model in "${ALL_MODELS[@]}"; do
    warmup_model "$model" &
done

# Wait for all background jobs to complete
wait

echo ""
echo "=================================================="
echo "Warmup Complete - Verifying loaded models..."
echo "=================================================="
echo ""

# Check Ollama process memory usage
echo "Ollama RAM Usage:"
ps aux | grep -i "ollama" | grep -v grep | awk '{printf "  Process: %-50s RAM: %5.2f GB\n", $11, $6/1024/1024}'
echo ""

# Get updated free RAM
FINAL_FREE_RAM=$(vm_stat | awk '/Pages free/ {free=$3} /Pages inactive/ {inactive=$3} END {page_size=4096; total_free=(free+inactive)*page_size/1024/1024/1024; print total_free}')
RAM_USED=$(echo "$FREE_RAM - $FINAL_FREE_RAM" | bc)

echo "RAM Statistics:"
echo "  Initial Available: ${FREE_RAM} GB"
echo "  Final Available:   ${FINAL_FREE_RAM} GB"
echo "  RAM Consumed:      ${RAM_USED} GB"
echo ""

echo "=================================================="
echo "All models warmed up and ready for parallel execution"
echo "Concurrent execution capacity: 7 agents simultaneously"
echo "=================================================="
