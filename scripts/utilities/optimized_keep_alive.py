#!/usr/bin/env python3
"""
Optimized Model Keep-Alive System
Keeps 3-4 most-used models loaded for Power Prompts project
Based on usage patterns: code analysis, documentation, general tasks
"""

import subprocess
import time
import threading
import json
from datetime import datetime
from typing import List, Dict

# OPTIMIZED: 3-4 most-used models based on project needs
# Total target: ~16GB RAM usage
CORE_MODELS = [
    "deepseek-coder:1.3b",    # 776MB  - Quick code analysis, fast iterations
    "magicoder:7b",           # 3.8GB  - Production code generation
    "llama3.1:8b",            # 4.9GB  - General tasks, documentation
    "qwen2.5:7b-instruct",    # 4.7GB  - Technical documentation, instructions
]

# TOTAL: ~14.2GB for core models (leaves 22GB free for system + on-demand models)

# Keep-alive interval (3 minutes)
KEEPALIVE_INTERVAL = 180

# Status file for monitoring
STATUS_FILE = "/tmp/model-keepalive-status.json"

model_threads = {}
stop_event = threading.Event()
model_status = {}
status_lock = threading.Lock()


def update_status(model: str, status: str, message: str = ""):
    """Update model status in shared dictionary"""
    with status_lock:
        model_status[model] = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        # Write to file for external monitoring
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(model_status, f, indent=2)
        except:
            pass


def keep_model_alive(model: str):
    """Keep a model loaded by periodically sending it requests"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Starting keep-alive for {model}", flush=True)
    update_status(model, "starting", "Initializing keep-alive thread")

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
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Keep-alive: {model}", flush=True)
                update_status(model, "active", "Model loaded and responding")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Keep-alive warning: {model}", flush=True)
                update_status(model, "warning", f"Non-zero return code: {result.returncode}")

        except subprocess.TimeoutExpired:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏱️  Keep-alive timeout: {model}", flush=True)
            update_status(model, "timeout", "Request timed out after 30s")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Keep-alive error for {model}: {e}", flush=True)
            update_status(model, "error", str(e))

        # Wait for next keep-alive interval (unless stopping)
        stop_event.wait(KEEPALIVE_INTERVAL)

    update_status(model, "stopped", "Keep-alive thread terminated")


def check_loaded_models() -> str:
    """Check which models are currently loaded"""
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def get_ram_usage() -> tuple:
    """Get current RAM usage"""
    try:
        result = subprocess.run(["vm_stat"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        pages = {}

        for line in lines:
            if "Pages" in line:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[1].rstrip(":")
                    value = parts[2].rstrip(".")
                    try:
                        pages[key] = int(value)
                    except:
                        pass

        page_size = 4096
        total_used = (pages.get("active", 0) + pages.get("wired", 0)) * page_size / (1024**3)
        total_free = (pages.get("free", 0) + pages.get("inactive", 0)) * page_size / (1024**3)

        return total_used, total_free

    except Exception as e:
        return 0, 0


def main():
    print("=" * 70, flush=True)
    print("Optimized Model Keep-Alive System - Power Prompts Project", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    print(f"Core models (3-4 most-used): {len(CORE_MODELS)}", flush=True)
    for i, model in enumerate(CORE_MODELS, 1):
        print(f"  {i}. {model}", flush=True)
    print(flush=True)

    print(f"Target RAM usage: ~14GB (leaves 22GB free)", flush=True)
    print(f"Keep-alive interval: {KEEPALIVE_INTERVAL}s (3 minutes)", flush=True)
    print(f"Status file: {STATUS_FILE}", flush=True)
    print(flush=True)

    initial_used, initial_free = get_ram_usage()
    print(f"Initial RAM: {initial_used:.2f} GB used, {initial_free:.2f} GB free", flush=True)
    print(flush=True)

    print("Loading core models sequentially...", flush=True)
    print(flush=True)

    # Load all core models initially
    for model in CORE_MODELS:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Loading {model}...", flush=True)
        try:
            result = subprocess.run(
                ["ollama", "run", model, "test"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Loaded {model}", flush=True)
                update_status(model, "loaded", "Initial load successful")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Load warning {model}", flush=True)
                update_status(model, "load_warning", f"Return code: {result.returncode}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to load {model}: {e}", flush=True)
            update_status(model, "load_failed", str(e))

    print(flush=True)
    print("=" * 70, flush=True)
    print("Initial loading complete - Starting keep-alive threads", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # Start keep-alive threads
    for model in CORE_MODELS:
        thread = threading.Thread(target=keep_model_alive, args=(model,), daemon=True)
        thread.start()
        model_threads[model] = thread
        time.sleep(2)  # Stagger starts

    print(flush=True)
    print("=" * 70, flush=True)
    print("Keep-alive system active - Monitoring status", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # Monitor and report status
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] Status at {datetime.now().strftime('%H:%M:%S')}", flush=True)
            print("-" * 70, flush=True)

            # Check loaded models
            loaded = check_loaded_models()
            print("Currently loaded:", flush=True)
            for line in loaded.strip().split('\n'):
                if line.strip():
                    print(f"  {line}", flush=True)

            # Check RAM
            used, free = get_ram_usage()
            ram_increase = used - initial_used
            print(f"\nRAM: {used:.2f} GB used, {free:.2f} GB free", flush=True)
            print(f"Change: {ram_increase:+.2f} GB since start", flush=True)
            print(f"Utilization: {(used/36)*100:.1f}%", flush=True)

            # Model status summary
            print("\nModel Status:", flush=True)
            with status_lock:
                for model, status in model_status.items():
                    status_emoji = {
                        "active": "✅",
                        "warning": "⚠️",
                        "timeout": "⏱️",
                        "error": "❌",
                        "starting": "🔄",
                        "loaded": "📦",
                    }.get(status["status"], "❓")
                    print(f"  {status_emoji} {model}: {status['status']}", flush=True)

            # Wait before next check
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\nShutting down keep-alive system...", flush=True)
        stop_event.set()

        for model, thread in model_threads.items():
            print(f"Stopping {model}...", flush=True)
            thread.join(timeout=5)

        print("\nKeep-alive system stopped", flush=True)
        print("=" * 70, flush=True)


if __name__ == "__main__":
    main()
