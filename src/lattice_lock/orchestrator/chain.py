import logging
import uuid
from typing import Any

import yaml

from lattice_lock.orchestrator.core import ModelOrchestrator

logger = logging.getLogger(__name__)


class PipelineStep:
    def __init__(
        self,
        name: str,
        prompt: str,
        model_id: str | None = None,
        output_key: str | None = None,
    ):
        self.name = name
        self.prompt = prompt
        self.model_id = model_id
        self.output_key = output_key or f"{name.lower().replace(' ', '_')}_output"


class Pipeline:
    def __init__(self, name: str, steps: list[PipelineStep]):
        self.name = name
        self.steps = steps


class ChainOrchestrator:
    """
    Orchestrates the execution of a multi-step pipeline (chain).
    """

    def __init__(self, orchestrator: ModelOrchestrator | None = None):
        self.orchestrator = orchestrator or ModelOrchestrator()

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Pipeline":
        """Load a pipeline from a YAML file."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        name = data.get("name", "Unnamed Pipeline")
        steps_data = data.get("steps", [])

        steps = []
        for s in steps_data:
            steps.append(
                PipelineStep(
                    name=s["name"],
                    prompt=s["prompt"],
                    model_id=s.get("model_id"),
                    output_key=s.get("output_key"),
                )
            )

        return Pipeline(name, steps)

    async def run_pipeline(
        self,
        pipeline: Pipeline,
        initial_inputs: dict[str, Any],
        start_from_step: str | None = None,
        pipeline_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute the pipeline steps sequentially.

        Args:
            pipeline: The Pipeline definition to run.
            initial_inputs: Dictionary of initial variables.
            start_from_step: Name of step to resume from (skips previous steps).
            pipeline_id: Optional ID for this execution (generated if None).

        Returns:
            Dict containing pipeline results and final context.
        """
        pipeline_id = pipeline_id or str(uuid.uuid4())
        context = initial_inputs.copy()
        results = {}

        # 1. Determine starting point
        steps_to_run = pipeline.steps
        if start_from_step:
            logger.info(f"Resuming pipeline {pipeline_id} from step {start_from_step}")
            try:
                start_index = next(
                    i for i, s in enumerate(pipeline.steps) if s.name == start_from_step
                )
                steps_to_run = pipeline.steps[start_index:]
                # Note: In a real resumption scenario, we would need to load the
                # context from the checkpoint associated with pipeline_id.
                # For now, we assume initial_inputs contains necessary history.
            except StopIteration:
                raise ValueError(f"Step '{start_from_step}' not found in pipeline")

        # 2. Execute Steps
        for step in steps_to_run:
            step_id = str(uuid.uuid4())
            logger.info(f"Running step: {step.name} (ID: {step_id})")

            # Simple template rendering
            rendered_prompt = step.prompt
            for key, value in context.items():
                rendered_prompt = rendered_prompt.replace(f"{{{{{key}}}}}", str(value))

            try:
                response = await self.orchestrator.route_request(
                    prompt=rendered_prompt, model_id=step.model_id
                )

                context[step.output_key] = response.content

                results[step.name] = {
                    "step_id": step_id,
                    "content": response.content,
                    "model": response.model,
                    "usage": response.usage,
                }

                # 3. Persist State (Stub)
                self._save_checkpoint(pipeline_id, step.name, context)

            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                raise RuntimeError(f"Pipeline {pipeline.name} failed at step {step.name}: {e}")

        return {
            "pipeline_name": pipeline.name,
            "pipeline_id": pipeline_id,
            "final_context": context,
            "step_results": results,
        }

    def _save_checkpoint(self, pipeline_id: str, step_name: str, context: dict[str, Any]):
        """
        Save the current execution state to allow for resumption.
        (Stub implementation)
        """
        # In the future, this will write to a local DB or file.
        # For now, we just log it.
        logger.debug(f"Checkpoint saved for {pipeline_id} at {step_name}")

    def _load_checkpoint(self, pipeline_id: str) -> dict[str, Any]:
        """
        Load execution state for a given pipeline ID.
        (Stub implementation)
        """
        # In the future, this will read from DB.
        return {}
