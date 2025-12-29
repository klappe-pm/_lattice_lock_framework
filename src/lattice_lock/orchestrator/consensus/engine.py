import asyncio
import logging
from collections import Counter

from lattice_lock.orchestrator.core import ModelOrchestrator

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Executes multi-model consensus strategies.
    dictating agreement between models.
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
            self.orchestrator.route_request(
                prompt=voting_prompt,
                model_id=model_id,
                task_type=None
            )
            for model_id in models
        ]

        # Execute all model queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        votes = []
        for model_id, result in zip(models, results):
            if isinstance(result, Exception):
                logger.error(f"Model {model_id} failed to vote: {result}")
                continue
            
            # Normalize vote text
            vote_text = result.content.strip().split('\n')[0].replace("'", "").replace('"', "")
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
