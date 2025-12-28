import logging
import yaml
from typing import Any, Dict, List, Optional
from pathlib import Path

from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.orchestrator.types import APIResponse

logger = logging.getLogger(__name__)

class PipelineStep:
    def __init__(self, name: str, prompt: str, model_id: Optional[str] = None, output_key: Optional[str] = None):
        self.name = name
        self.prompt = prompt
        self.model_id = model_id
        self.output_key = output_key or f"{name.lower().replace(' ', '_')}_output"

class Pipeline:
    def __init__(self, name: str, steps: List[PipelineStep]):
        self.name = name
        self.steps = steps

class ChainOrchestrator:
    """
    Orchestrates the execution of a multi-step pipeline (chain).
    """

    def __init__(self, orchestrator: Optional[ModelOrchestrator] = None):
        self.orchestrator = orchestrator or ModelOrchestrator()

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Pipeline":
        """Load a pipeline from a YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        name = data.get("name", "Unnamed Pipeline")
        steps_data = data.get("steps", [])
        
        steps = []
        for s in steps_data:
            steps.append(PipelineStep(
                name=s["name"],
                prompt=s["prompt"],
                model_id=s.get("model_id"),
                output_key=s.get("output_key")
            ))
        
        return Pipeline(name, steps)

    async def run_pipeline(self, pipeline: Pipeline, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the pipeline steps sequentially.
        
        Passes outputs from previous steps to subsequent steps using template rendering.
        """
        context = initial_inputs.copy()
        results = {}

        for step in pipeline.steps:
            logger.info(f"Running pipeline step: {step.name}")
            
            # Simple template rendering
            rendered_prompt = step.prompt
            for key, value in context.items():
                rendered_prompt = rendered_prompt.replace(f"{{{{{key}}}}}", str(value))
            
            try:
                response = await self.orchestrator.route_request(
                    prompt=rendered_prompt,
                    model_id=step.model_id
                )
                
                context[step.output_key] = response.content
                results[step.name] = {
                    "content": response.content,
                    "model": response.model,
                    "usage": response.usage
                }
            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                raise RuntimeError(f"Pipeline {pipeline.name} failed at step {step.name}: {e}")

        return {
            "pipeline_name": pipeline.name,
            "final_context": context,
            "step_results": results
        }
