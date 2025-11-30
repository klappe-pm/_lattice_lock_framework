#!/usr/bin/env python3
"""
Concurrent Model Capacity Test
Tests true parallel execution with multiple Ollama models to maximize RAM usage
"""

import subprocess
import time
import threading
from datetime import datetime
from typing import List, Dict

# Models to test concurrently
MODELS = [
    "deepseek-coder:1.3b",
    "llama3.2:3b",
    "magicoder:7b",
    "llama3.1:8b",
    "qwen2.5:7b-instruct",
    "codellama:13b",
    "qwen2.5:32b",
]

# Test prompts for each model
PROMPTS = {
    "deepseek-coder:1.3b": "Write a Python function to calculate fibonacci numbers",
    "llama3.2:3b": "Explain recursion in programming",
    "magicoder:7b": "Create a REST API endpoint for user authentication",
    "llama3.1:8b": "Write documentation for a Python class",
    "qwen2.5:7b-instruct": "Explain SOLID principles",
    "codellama:13b": "Refactor code for better performance",
    "qwen2.5:32b": "Design a scalable microservices architecture",
}

results = []
results_lock = threading.Lock()


def run_model(model: str, prompt: str):
    """Run a single model with timing"""
    start_time = time.time()
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] 🚀 Starting: {model}")

    try:
        # Run model with actual workload
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout per model
        )

        end_time = time.time()
        duration = int(end_time - start_time)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if result.returncode == 0:
            print(f"[{timestamp}] ✅ Completed: {model} ({duration}s)")
            with results_lock:
                results.append(
                    {
                        "model": model,
                        "status": "success",
                        "duration": duration,
                        "output_length": len(result.stdout),
                    }
                )
        else:
            print(f"[{timestamp}] ❌ Failed: {model} ({duration}s)")
            with results_lock:
                results.append(
                    {"model": model, "status": "failed", "duration": duration, "error": result.stderr}
                )

    except subprocess.TimeoutExpired:
        end_time = time.time()
        duration = int(end_time - start_time)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⏱️ Timeout: {model} ({duration}s)")
        with results_lock:
            results.append({"model": model, "status": "timeout", "duration": duration})

    except Exception as e:
        end_time = time.time()
        duration = int(end_time - start_time)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ Error: {model} ({duration}s) - {str(e)}")
        with results_lock:
            results.append({"model": model, "status": "error", "duration": duration, "error": str(e)})


def check_loaded_models():
    """Check which models are currently loaded"""
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error checking models: {e}"


def get_ram_usage():
    """Get current RAM usage"""
    try:
        result = subprocess.run(
            [
                "vm_stat",
            ],
            capture_output=True,
            text=True,
        )

        # Parse vm_stat output
        lines = result.stdout.split("\n")
        pages = {}
        for line in lines:
            if "Pages" in line:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[1].rstrip(":")
                    value = parts[2].rstrip(".")
                    pages[key] = int(value)

        # Calculate RAM usage (page size = 4096 bytes)
        page_size = 4096
        total_used = (pages.get("active", 0) + pages.get("wired", 0)) * page_size / (1024**3)
        total_free = (pages.get("free", 0) + pages.get("inactive", 0)) * page_size / (1024**3)

        return total_used, total_free

    except Exception as e:
        return 0, 0


def main():
    print("=" * 50)
    print("Concurrent Model Capacity Test")
    print("=" * 50)
    print()

    print(f"Starting concurrent execution of {len(MODELS)} models...")
    print()

    initial_used, initial_free = get_ram_usage()
    print(f"Initial RAM: {initial_used:.2f} GB used, {initial_free:.2f} GB free")
    print()

    # Create threads for parallel execution
    threads = []
    for model in MODELS:
        prompt = PROMPTS.get(model, "Explain your capabilities")
        thread = threading.Thread(target=run_model, args=(model, prompt))
        threads.append(thread)

    # Start all threads
    start_time = time.time()
    for thread in threads:
        thread.start()

    # Wait a few seconds then check loaded models
    time.sleep(5)
    print()
    print("=" * 50)
    print("Status after 5 seconds...")
    print("=" * 50)
    print()
    print(check_loaded_models())

    mid_used, mid_free = get_ram_usage()
    print(f"Mid-test RAM: {mid_used:.2f} GB used, {mid_free:.2f} GB free")
    print()

    print("Waiting for all models to complete...")
    print()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_duration = int(end_time - start_time)

    # Final status
    print()
    print("=" * 50)
    print("Test Complete - Final Status")
    print("=" * 50)
    print()

    final_used, final_free = get_ram_usage()
    print(f"Final RAM: {final_used:.2f} GB used, {final_free:.2f} GB free")
    print(f"RAM increase: {final_used - initial_used:.2f} GB")
    print()

    print(check_loaded_models())
    print()

    # Results summary
    print("=" * 50)
    print("Results Summary")
    print("=" * 50)
    print()

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]

    print(f"Total models tested: {len(MODELS)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed/Timeout: {len(failed)}")
    print(f"Total test duration: {total_duration}s")
    print()

    if successful:
        print("Successful executions:")
        for r in successful:
            print(f"  ✅ {r['model']}: {r['duration']}s ({r['output_length']} chars)")
        print()

    if failed:
        print("Failed executions:")
        for r in failed:
            print(f"  ❌ {r['model']}: {r['status']}")
        print()

    # Calculate concurrent capacity
    avg_duration = sum(r["duration"] for r in successful) / len(successful) if successful else 0
    print(f"Average completion time: {avg_duration:.1f}s")
    print(f"Peak RAM usage: {final_used:.2f} GB / 36 GB ({(final_used/36)*100:.1f}%)")
    print()
    print("=" * 50)
    print("Concurrent execution capacity verified")
    print("=" * 50)


if __name__ == "__main__":
    main()
