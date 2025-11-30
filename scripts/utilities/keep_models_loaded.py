#!/usr/bin/env python3
"""
Keep Multiple Models Loaded in Memory
Maximizes RAM usage by keeping models active with periodic pings
Prevents Ollama from unloading models to conserve memory
"""

import subprocess
import time
import threading
from datetime import datetime
from typing import List

# Models to keep loaded (32GB+ tier configuration)
TIER1_MODELS = [
    "deepseek-coder:1.3b",  # 776MB
    "llama3.2:3b",  # 2.0GB
]

TIER2_MODELS = [
    "magicoder:7b",  # 3.8GB
    "llama3.1:8b",  # 4.9GB
    "qwen2.5:7b-instruct",  # 4.7GB
]

TIER3_MODELS = [
    "codellama:13b",  # 7.4GB
]

TIER4_MODELS = [
    "qwen2.5:32b",  # 19GB
]

# All models to load (total ~42GB theoretical, but Ollama will manage)
ALL_MODELS = TIER1_MODELS + TIER2_MODELS + TIER3_MODELS + TIER4_MODELS

# Keep-alive interval in seconds
KEEPALIVE_INTERVAL = 180  # 3 minutes

model_threads = {}
stop_event = threading.Event()


def keep_model_alive(model: str):
    """Keep a model loaded by periodically sending it requests"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Starting keep-alive for {model}")

    while not stop_event.is_set():
        try:
            # Send minimal request to keep model loaded
            result = subprocess.run(
                ["ollama", "run", model, "hi"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Keep-alive: {model}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Keep-alive warning: {model}")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Keep-alive error for {model}: {e}")

        # Wait for next keep-alive interval (unless stopping)
        stop_event.wait(KEEPALIVE_INTERVAL)


def check_loaded_models():
    """Check which models are currently loaded"""
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def get_ram_usage():
    """Get current RAM usage"""
    try:
        result = subprocess.run(
            ["vm_stat"],
            capture_output=True,
            text=True,
        )

        lines = result.stdout.split("\n")
        pages = {}
        for line in lines:
            if "Pages" in line:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[1].rstrip(":")
                    value = parts[2].rstrip(".")
                    pages[key] = int(value)

        page_size = 4096
        total_used = (pages.get("active", 0) + pages.get("wired", 0)) * page_size / (1024**3)
        total_free = (pages.get("free", 0) + pages.get("inactive", 0)) * page_size / (1024**3)

        return total_used, total_free

    except Exception as e:
        return 0, 0


def main():
    print("=" * 60)
    print("Maximum RAM Utilization - Model Keep-Alive System")
    print("=" * 60)
    print()

    print(f"Target models: {len(ALL_MODELS)}")
    for i, model in enumerate(ALL_MODELS, 1):
        print(f"  {i}. {model}")
    print()

    print(f"Keep-alive interval: {KEEPALIVE_INTERVAL}s")
    print()

    initial_used, initial_free = get_ram_usage()
    print(f"Initial RAM: {initial_used:.2f} GB used, {initial_free:.2f} GB free")
    print()

    print("Starting initial model loading...")
    print()

    # Load all models initially (sequentially to avoid overload)
    for model in ALL_MODELS:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading {model}...")
        try:
            subprocess.run(
                ["ollama", "run", model, "test"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Loaded {model}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to load {model}: {e}")

    print()
    print("=" * 60)
    print("Initial loading complete - Starting keep-alive threads")
    print("=" * 60)
    print()

    # Start keep-alive threads for all models
    for model in ALL_MODELS:
        thread = threading.Thread(target=keep_model_alive, args=(model,), daemon=True)
        thread.start()
        model_threads[model] = thread
        time.sleep(2)  # Stagger thread starts

    print()
    print("=" * 60)
    print("Keep-alive system active - Models will remain loaded")
    print("=" * 60)
    print()

    # Monitor loaded models and RAM usage
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] Status at {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 60)

            # Check loaded models
            loaded = check_loaded_models()
            print("Loaded models:")
            print(loaded)

            # Check RAM usage
            used, free = get_ram_usage()
            print(f"RAM Usage: {used:.2f} GB used, {free:.2f} GB free")
            print(f"RAM Change: {used - initial_used:+.2f} GB since start")
            print(f"Utilization: {(used/36)*100:.1f}% of 36 GB total")

            # Wait before next check
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n\nShutting down keep-alive system...")
        stop_event.set()

        # Wait for threads to finish
        for model, thread in model_threads.items():
            print(f"Stopping keep-alive for {model}...")
            thread.join(timeout=5)

        print("\nKeep-alive system stopped")
        print("=" * 60)


if __name__ == "__main__":
    main()
