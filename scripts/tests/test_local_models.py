#!/usr/bin/env python3
"""
Test script to verify local code models are properly integrated with the orchestrator.

This is a manual diagnostic script, not a pytest test module.
Run directly with: python tests/test_local_models.py
"""

import sys
import os


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

    print("Testing Local Code Model Integration")
    print("=" * 50)

    orchestrator = ModelOrchestrator()

    local_models = [k for k, v in orchestrator.models.items() if v.provider.value == "local"]
    print(f"\nFound {len(local_models)} local models:")
    for model_id in local_models:
        model = orchestrator.models[model_id]
        print(f"  - {model_id}: {model.accuracy:.2f} accuracy, ${model.input_cost:.2f} cost")

    print(f"\nTesting code generation model selection...")

    requirements = TaskRequirements(
        task_type=TaskType.CODE_GENERATION,
        max_cost=0.01
    )

    prompt = "Write a Python function to calculate fibonacci sequence"
    selected_result = orchestrator.select_model(prompt, requirements)

    print(f"\nSelected model for code generation:")
    if selected_result:
        if isinstance(selected_result, tuple):
            model_id, score = selected_result
        else:
            model_id = selected_result
            score = None

        if isinstance(model_id, str) and model_id in orchestrator.models:
            model = orchestrator.models[model_id]
            provider_type = "local" if model.provider.value == "local" else "cloud"
            print(f"  [{provider_type}] {model_id}")
            print(f"     Provider: {model.provider.value} | Cost: ${model.input_cost:.2f}")
            print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
            print(f"     Accuracy: {model.accuracy:.2f} | Speed: {model.speed:.2f}")
            if score and isinstance(score, (int, float)):
                print(f"     Selection Score: {score:.3f}")
        else:
            print(f"  Unexpected result: {selected_result}")
    else:
        print("  No model selected")

    print(f"\nLocal code models available for cost optimization:")

    code_models = [(k, v) for k, v in orchestrator.models.items()
                   if v.provider.value == "local" and
                      v.task_scores.get(TaskType.CODE_GENERATION, 0) > 0.7]

    code_models.sort(key=lambda x: x[1].task_scores.get(TaskType.CODE_GENERATION, 0), reverse=True)

    print(f"Top local code models (by code generation score):")
    for i, (model_id, model) in enumerate(code_models[:5], 1):
        print(f"  {i}. [local] {model_id}")
        print(f"     Code Score: {model.task_scores.get(TaskType.CODE_GENERATION, 0):.2f}")
        print(f"     Speed: {model.speed:.2f} | Accuracy: {model.accuracy:.2f}")

    print(f"\nLocal model integration test completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
