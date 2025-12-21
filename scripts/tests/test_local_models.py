#!/usr/bin/env python3
"""
Test script to verify local code models are properly integrated with the orchestrator.

This is a manual diagnostic script, not a pytest test module.
Run directly with: python tests/test_local_models.py
"""

import os
import sys


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    import importlib.util
    
    # Import the orchestrator
    from lattice_lock import ModelOrchestrator
    from lattice_lock.types import TaskType, TaskRequirements

    print("Testing Local Code Model Integration")
    print("=" * 50)

    orchestrator = ModelOrchestrator()

    local_models = [k for k, v in orchestrator.registry.models.items() if v.provider.value == "local"]
    print(f"\nFound {len(local_models)} local models:")
    for model_id in local_models:
        model = orchestrator.registry.models[model_id]
        print(f"  - {model_id}: {model.reasoning_score:.2f} reasoning, ${model.input_cost:.2f} cost")

    print("\nTesting code generation model selection...")

    requirements = TaskRequirements(task_type=TaskType.CODE_GENERATION, max_cost=0.01)

    prompt = "Write a Python function to calculate fibonacci sequence"
    selected_result = orchestrator._select_best_model(orchestrator.analyzer.analyze(prompt, requirements))

    print("\nSelected model for code generation:")
    if selected_result:
        if isinstance(selected_result, tuple):
            model_id, score = selected_result
        else:
            model_id = selected_result
            score = None

        if isinstance(model_id, str) and model_id in orchestrator.registry.models:
            model = orchestrator.registry.models[model_id]
            provider_type = "local" if model.provider.value == "local" else "cloud"
            print(f"  [{provider_type}] {model_id}")
            print(f"     Provider: {model.provider.value} | Cost: ${model.input_cost:.2f}")
            print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
            print(f"     Accuracy: {model.reasoning_score:.2f} | Speed: {model.speed_rating:.2f}")
            if score and isinstance(score, int | float):
                print(f"     Selection Score: {score:.3f}")
        else:
            print(f"  Unexpected result: {selected_result}")
    else:
        print("  No model selected")

    print("\nLocal code models available for cost optimization:")

    code_models = [
        (k, v)
        for k, v in orchestrator.registry.models.items()
        if v.provider.value == "local" and v.task_scores.get(TaskType.CODE_GENERATION, 0) > 0.7
    ]

    code_models.sort(key=lambda x: x[1].task_scores.get(TaskType.CODE_GENERATION, 0), reverse=True)

    print("Top local code models (by code generation score):")
    for i, (model_id, model) in enumerate(code_models[:5], 1):
        print(f"  {i}. [local] {model_id}")
        print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
        print(f"     Speed: {model.speed_rating:.2f} | Reasoning: {model.reasoning_score:.2f}")

    print("\nLocal model integration test completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
