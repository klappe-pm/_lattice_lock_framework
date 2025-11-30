#!/usr/bin/env python3
import subprocess
import json
import re
import sys
import shutil

# Try to import psutil for RAM monitoring, handle if missing
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class LocalModelAutomation:
    def __init__(self):
        self.ollama_path = shutil.which("ollama")
        self.models = []
        self.categories = {
            "coding": ["code", "coder", "magicoder", "php", "python", "sql"],
            "reasoning": ["deepseek-r1", "o1", "reason", "math"],
            "vision": ["vision", "llava", "bakllava"],
            "general": [] # Fallback
        }

    def check_ollama_installed(self):
        if not self.ollama_path:
            print("Error: 'ollama' command not found. Please install Ollama first.")
            return False
        return True

    def list_models(self):
        """Executes 'ollama list' and parses the output."""
        if not self.check_ollama_installed():
            return []

        try:
            # Run ollama list
            result = subprocess.run([self.ollama_path, "list"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error running ollama list: {result.stderr}")
                return []

            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []

            # Parse lines (skip header)
            # Header: NAME    ID    SIZE    MODIFIED
            parsed_models = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    size_str = parts[2] # e.g., "4.7GB"
                    
                    # Convert size to GB float
                    size_gb = 0.0
                    if "GB" in size_str:
                        size_gb = float(size_str.replace("GB", ""))
                    elif "MB" in size_str:
                        size_gb = float(size_str.replace("MB", "")) / 1024

                    parsed_models.append({
                        "name": name,
                        "size_gb": size_gb,
                        "capabilities": self._categorize_model(name)
                    })
            
            self.models = parsed_models
            return parsed_models

        except Exception as e:
            print(f"Exception during model discovery: {e}")
            return []

    def _categorize_model(self, name):
        """Determines model capabilities based on name."""
        caps = []
        name_lower = name.lower()
        
        is_specialized = False
        
        # Check coding
        if any(keyword in name_lower for keyword in self.categories["coding"]):
            caps.append("CODE_GENERATION")
            caps.append("DEBUGGING")
            is_specialized = True
            
        # Check reasoning
        if any(keyword in name_lower for keyword in self.categories["reasoning"]):
            caps.append("REASONING")
            caps.append("COMPLEX_ANALYSIS")
            is_specialized = True
            
        # Check vision
        if any(keyword in name_lower for keyword in self.categories["vision"]):
            caps.append("VISION")
            is_specialized = True
            
        # Default to general if no specific category found, or add it anyway
        caps.append("GENERAL")
        caps.append("CHAT")
        
        return caps

    def get_system_ram(self):
        """Returns total and available RAM in GB."""
        if not PSUTIL_AVAILABLE:
            return None, None
        
        mem = psutil.virtual_memory()
        return mem.total / (1024**3), mem.available / (1024**3)

    def generate_registry(self):
        """Generates a JSON registry of local models."""
        self.list_models()
        
        total_ram, available_ram = self.get_system_ram()
        
        registry = {
            "system_info": {
                "total_ram_gb": round(total_ram, 2) if total_ram else "Unknown",
                "available_ram_gb": round(available_ram, 2) if available_ram else "Unknown",
                "psutil_installed": PSUTIL_AVAILABLE
            },
            "model_count": len(self.models),
            "models": self.models
        }
        
        return registry

def main():
    automation = LocalModelAutomation()
    registry = automation.generate_registry()
    
    print(json.dumps(registry, indent=2))
    
    # Simple recommendation
    if registry["models"]:
        print("\n--- Model Recommendations ---", file=sys.stderr)
        avail_ram = registry["system_info"]["available_ram_gb"]
        
        if isinstance(avail_ram, (int, float)):
            safe_limit = avail_ram - 2.0 # Leave 2GB buffer
            print(f"Available RAM for models: {avail_ram:.2f} GB (Safe limit: {safe_limit:.2f} GB)", file=sys.stderr)
            
            fits = [m["name"] for m in registry["models"] if m["size_gb"] <= safe_limit]
            print(f"Models that fit in memory: {', '.join(fits)}", file=sys.stderr)
        else:
            print("Install 'psutil' to enable RAM-based recommendations.", file=sys.stderr)

if __name__ == "__main__":
    main()
