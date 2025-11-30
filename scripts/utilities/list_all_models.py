#!/usr/bin/env python3
"""
Comprehensive listing of all available models in the Power Prompts orchestration system
Shows local models, cloud models, API key status, and detailed capabilities
"""

import os
import sys
import importlib.util
from typing import Dict, List

# Import the orchestrator
spec = importlib.util.spec_from_file_location(
    "model_orchestrator", 
    os.path.join(os.path.dirname(__file__), "model-orchestrator.py")
)
model_orchestrator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model_orchestrator)

ModelOrchestrator = model_orchestrator.ModelOrchestrator
TaskType = model_orchestrator.TaskType
ModelProvider = model_orchestrator.ModelProvider

def check_api_keys():
    """Check which API keys are configured"""
    api_keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Anthropic (Claude)': os.getenv('ANTHROPIC_API_KEY'),
        'Google (Gemini)': os.getenv('GOOGLE_API_KEY'),
        'xAI (Grok)': os.getenv('XAI_API_KEY'),
        'DIAL': os.getenv('DIAL_API_KEY'),
        'Azure OpenAI': os.getenv('AZURE_OPENAI_API_KEY'),
        'AWS Bedrock': os.getenv('AWS_ACCESS_KEY_ID'),
    }
    
    configured_keys = {k: bool(v and len(v.strip()) > 0) for k, v in api_keys.items()}
    return configured_keys

def check_local_models():
    """Check which local models are actually installed via Ollama"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            installed_models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        installed_models.append(model_name)
            return installed_models
        else:
            return []
    except:
        return []

def format_task_scores(task_scores, top_n=3):
    """Format top task scores for display"""
    if not task_scores:
        return "No specific task scores"
    
    sorted_scores = sorted(task_scores.items(), key=lambda x: x[1], reverse=True)
    top_scores = sorted_scores[:top_n]
    
    score_strs = []
    for task_type, score in top_scores:
        task_name = task_type.value.replace('_', ' ').title()
        score_strs.append(f"{task_name}: {score:.2f}")
    
    return " | ".join(score_strs)

def main():
    print("🚀 Power Prompts - Complete Model Inventory")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = ModelOrchestrator()
    
    # Check API key status
    print("\n🔑 API Key Configuration Status:")
    print("-" * 40)
    api_status = check_api_keys()
    for provider, configured in api_status.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"  {provider:<20} {status}")
    
    # Check local model status
    print(f"\n🏠 Local Models (via Ollama):")
    print("-" * 40)
    installed_local = check_local_models()
    if installed_local:
        print(f"Found {len(installed_local)} installed local models:")
        for model in installed_local:
            print(f"  ✅ {model}")
    else:
        print("  ❌ No local models found or Ollama not available")
    
    # Group models by provider
    models_by_provider = {}
    for model_id, model in orchestrator.models.items():
        provider = model.provider.value
        if provider not in models_by_provider:
            models_by_provider[provider] = []
        models_by_provider[provider].append((model_id, model))
    
    print(f"\n📊 All Configured Models ({len(orchestrator.models)} total):")
    print("=" * 80)
    
    for provider_name, models in models_by_provider.items():
        provider_emoji = {
            'local': '🏠',
            'openai': '🤖',
            'anthropic': '🧠',
            'google': '🔍',
            'xai': '⚡',
            'azure': '☁️',
            'bedrock': '🪨',
            'dial': '📞',
            'meta': '🦙'
        }.get(provider_name, '🔧')
        
        provider_display = provider_name.upper().replace('_', ' ')
        api_configured = api_status.get({
            'openai': 'OpenAI',
            'anthropic': 'Anthropic (Claude)',
            'google': 'Google (Gemini)',
            'xai': 'xAI (Grok)',
            'azure': 'Azure OpenAI',
            'bedrock': 'AWS Bedrock',
            'dial': 'DIAL'
        }.get(provider_name), True)  # Local is always "configured"
        
        config_status = "✅" if (provider_name == 'local' or api_configured) else "❌"
        
        print(f"\n{provider_emoji} {provider_display} MODELS ({len(models)} models) {config_status}")
        print("-" * 60)
        
        # Sort models by accuracy for better display
        models.sort(key=lambda x: x[1].accuracy, reverse=True)
        
        for model_id, model in models:
            # Check if local model is actually installed
            availability = ""
            if provider_name == 'local':
                if any(model_id in installed for installed in installed_local):
                    availability = "🟢 Installed"
                else:
                    availability = "🔴 Not Installed"
            else:
                availability = "🟢 Available" if api_configured else "🔴 API Key Missing"
            
            print(f"  📝 {model_id}")
            print(f"     Status: {availability}")
            print(f"     Context: {model.context_window:,} tokens | Speed: {model.speed:.2f} | Accuracy: {model.accuracy:.2f}")
            print(f"     Cost: ${model.input_cost:.2f}/${model.output_cost:.2f} per 1M tokens")
            
            # Special capabilities
            capabilities = []
            if model.supports_vision: capabilities.append("Vision")
            if model.supports_function_calling: capabilities.append("Functions")
            if model.supports_reasoning: capabilities.append("Reasoning")
            if model.code_specialized: capabilities.append("Code Specialized")
            
            if capabilities:
                print(f"     Capabilities: {' | '.join(capabilities)}")
            
            # Top task scores
            top_tasks = format_task_scores(model.task_scores)
            print(f"     Best Tasks: {top_tasks}")
            print()
    
    # Summary statistics
    print("\n📈 Summary Statistics:")
    print("-" * 40)
    
    total_models = len(orchestrator.models)
    local_models = len([m for m in orchestrator.models.values() if m.provider.value == 'local'])
    cloud_models = total_models - local_models
    
    available_local = len([m for m_id, m in orchestrator.models.items() 
                          if m.provider.value == 'local' and 
                          any(m_id in installed for installed in installed_local)])
    
    configured_providers = sum(1 for configured in api_status.values() if configured)
    
    code_specialized = len([m for m in orchestrator.models.values() if m.code_specialized])
    vision_capable = len([m for m in orchestrator.models.values() if m.supports_vision])
    free_models = len([m for m in orchestrator.models.values() if m.input_cost == 0.0])
    
    print(f"  Total Models Configured: {total_models}")
    print(f"  Local Models: {local_models} ({available_local} actually installed)")
    print(f"  Cloud Models: {cloud_models}")
    print(f"  Configured API Providers: {configured_providers}/7")
    print(f"  Code-Specialized Models: {code_specialized}")
    print(f"  Vision-Capable Models: {vision_capable}")
    print(f"  Free Models (Local): {free_models}")
    
    print(f"\n✅ Model inventory complete!")
    print(f"💡 Tip: Use 'cost_optimize' strategy to prefer local models")
    print(f"💡 Tip: Code tasks will automatically select code-specialized models")

if __name__ == "__main__":
    main()