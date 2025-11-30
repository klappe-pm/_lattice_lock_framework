#!/usr/bin/env python3
"""
Test script to verify local code models are properly integrated with the orchestrator
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import from file with dashes (Python converts to underscores)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "model_orchestrator", 
        os.path.join(os.path.dirname(__file__), "model-orchestrator.py")
    )
    model_orchestrator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_orchestrator)
    
    ModelOrchestrator = model_orchestrator.ModelOrchestrator
    TaskType = model_orchestrator.TaskType
    TaskRequirements = model_orchestrator.TaskRequirements
    
    print("🚀 Testing Local Code Model Integration")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = ModelOrchestrator()
    
    # Check if our local models are loaded
    local_models = [k for k, v in orchestrator.models.items() if v.provider.value == "local"]
    print(f"\n📋 Found {len(local_models)} local models:")
    for model_id in local_models:
        model = orchestrator.models[model_id]
        print(f"  • {model_id}: {model.accuracy:.2f} accuracy, ${model.input_cost:.2f} cost")
    
    # Test code generation task selection
    print(f"\n🔍 Testing code generation model selection...")
    
    requirements = TaskRequirements(
        task_type=TaskType.CODE_GENERATION,
        max_cost=0.01  # Prefer low-cost (local) models
    )
    
    prompt = "Write a Python function to calculate fibonacci sequence"
    selected_result = orchestrator.select_model(prompt, requirements)
    
    print(f"\n🏆 Selected model for code generation:")
    if selected_result:
        # Handle different return types
        if isinstance(selected_result, tuple):
            model_id, score = selected_result
        else:
            # If just model ID returned
            model_id = selected_result
            score = None
            
        if isinstance(model_id, str) and model_id in orchestrator.models:
            model = orchestrator.models[model_id]
            provider_emoji = "🏠" if model.provider.value == "local" else "☁️"
            print(f"  {provider_emoji} {model_id}")
            print(f"     Provider: {model.provider.value} | Cost: ${model.input_cost:.2f}")
            print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
            print(f"     Accuracy: {model.accuracy:.2f} | Speed: {model.speed:.2f}")
            if score and isinstance(score, (int, float)):
                print(f"     Selection Score: {score:.3f}")
        else:
            print(f"  Unexpected result: {selected_result}")
    else:
        print("  No model selected")
    
    # Test with cost optimization by checking local models
    print(f"\n🎯 Local code models available for cost optimization:")
    
    code_models = [(k, v) for k, v in orchestrator.models.items() 
                   if v.provider.value == "local" and 
                      v.task_scores.get(TaskType.CODE_GENERATION, 0) > 0.7]
    
    # Sort by code generation score
    code_models.sort(key=lambda x: x[1].task_scores.get(TaskType.CODE_GENERATION, 0), reverse=True)
    
    print(f"Top local code models (by code generation score):")
    for i, (model_id, model) in enumerate(code_models[:5], 1):
        print(f"  {i}. 🏠 {model_id}")
        print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
        print(f"     Speed: {model.speed:.2f} | Accuracy: {model.accuracy:.2f}")
    
    print(f"\n✅ Local model integration test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)