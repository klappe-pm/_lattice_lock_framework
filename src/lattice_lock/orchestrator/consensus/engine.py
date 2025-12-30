import asyncio
import logging
from collections import Counter
from typing import Any

from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.orchestrator.types import TaskType

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Executes multi-model consensus strategies using voting.
    Best for governance/gating decisions (approve/reject).
    """

    def __init__(self, orchestrator: ModelOrchestrator | None = None):
        """Initialize with an optional orchestrator instance."""
        self.orchestrator = orchestrator or ModelOrchestrator()

    async def execute_voting(self, prompt: str, models: list[str]) -> str:
        """
        Queries multiple models and returns the majority vote.
        Executes requests in parallel for efficiency.
        """
        logger.info(f"Executing consensus vote with models: {models}")

        # Prepare voting instructions
        voting_prompt = (
            f"{prompt}\n\n"
            "Review the above request. Vote 'Approved' or 'Rejected'. "
            "Provide ONLY the vote word."
        )

        tasks = [
            self.orchestrator.route_request(prompt=voting_prompt, model_id=model_id, task_type=None)
            for model_id in models
        ]

        # Execute all model queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        votes = []
        for model_id, result in zip(models, results, strict=False):
            if isinstance(result, Exception):
                logger.error(f"Model {model_id} failed to vote: {result}")
                continue

            # Normalize vote text
            vote_text = result.content.strip().split("\n")[0].replace("'", "").replace('"', "")
            if "Approved" in vote_text:
                votes.append("Approved")
            elif "Rejected" in vote_text:
                votes.append("Rejected")
            else:
                logger.warning(f"Model {model_id} returned unclear vote: {vote_text}")
                votes.append("Abstain")

        if not votes:
            logger.warning("No valid votes received.")
            return "Indeterminate"

        # Tally votes
        tally = Counter(votes)
        winner = tally.most_common(1)[0][0]

        confidence = tally[winner] / len(votes)
        logger.info(f"Consensus reached: {winner} (Confidence: {confidence:.2f})")

        return winner


class ConsensusOrchestrator:
    """
    Orchestrates multiple models to reach a consensus or synthesize a better result.
    Best for generating unified artifacts by combining complementary information.
    """

    def __init__(self, orchestrator: ModelOrchestrator | None = None):
        self.orchestrator = orchestrator or ModelOrchestrator()

    async def run_consensus(
        self, prompt: str, num_models: int = 3, synthesizer_model_id: str | None = None
    ) -> dict[str, Any]:
        """
        Execute consensus flow:
        1. Analyze task.
        2. Select top N models.
        3. Execute in parallel.
        4. Synthesize results using a strong model.
        """
        # 1. Analyze
        requirements = await self.orchestrator.analyzer.analyze_async(prompt)

        # 2. Select top N models
        # Heuristic: get all suitable models and sort by score
        all_models = []
        for m_id, m_cap in self.orchestrator.registry.models.items():
            score = self.orchestrator.scorer.score(m_cap, requirements)
            if score > 0:
                all_models.append((m_id, m_cap, score))

        all_models.sort(key=lambda x: x[2], reverse=True)
        top_models = all_models[:num_models]

        if not top_models:
            raise RuntimeError("No suitable models found for consensus")

        # 3. Execute in parallel
        logger.info(f"Running parallel consensus with {len(top_models)} models")
        tasks = []
        for m_id, m_cap, _ in top_models:
            tasks.append(self.orchestrator.route_request(prompt, model_id=m_id))

        raw_responses = await asyncio.gather(*tasks, return_exceptions=True)

        valid_responses = []
        for i, resp in enumerate(raw_responses):
            m_id = top_models[i][0]
            if isinstance(resp, Exception):
                logger.error(f"Model {m_id} failed during consensus: {resp}")
            else:
                valid_responses.append(resp)

        if not valid_responses:
            raise RuntimeError("All models failed during consensus execution")

        # 4. Synthesize
        # Prompt for synthesis
        synthesis_prompt = "I have polled multiple AI models with the following prompt:\n\n"
        synthesis_prompt += f"PROMPT: {prompt}\n\n"
        synthesis_prompt += "Here are their responses:\n\n"

        for i, resp in enumerate(valid_responses):
            synthesis_prompt += f"--- RESPONSE FROM {resp.model} ---\n"
            synthesis_prompt += f"{resp.content}\n\n"

        synthesis_prompt += "Please synthesize these responses into a single, high-quality, and comprehensive answer. "
        synthesis_prompt += "If there are contradictions, call them out and try to find the most accurate perspective."

        logger.info("Synthesizing results...")
        # Use a strong model for synthesis if not specified
        if not synthesizer_model_id:
            # Re-run selection for the synthesis task
            synth_requirements = await self.orchestrator.analyzer.analyze_async(synthesis_prompt)
            synth_requirements.task_type = TaskType.REASONING  # Force reasoning for synthesis
            synthesizer_model_id = self.orchestrator.selector.select_best_model(synth_requirements)

        synthesis_response = await self.orchestrator.route_request(
            prompt=synthesis_prompt, model_id=synthesizer_model_id
        )

        return {
            "synthesis": synthesis_response.content,
            "synthesizer_model": synthesis_response.model,
            "individual_responses": [
                {"model": r.model, "content": r.content, "usage": r.usage} for r in valid_responses
            ],
            "total_cost": sum(r.usage.cost for r in valid_responses if hasattr(r.usage, "cost"))
            + (synthesis_response.usage.cost if hasattr(synthesis_response.usage, "cost") else 0.0),
        }
