"""
Core logic for the Consensus Engine.
"""

import logging
from typing import Any

from .templates import SYNTHESIS_TEMPLATE
<<<<<<< HEAD
from .types import ConsensusRequest
=======
from .types import ConsensusRequest, VoteStrategy
>>>>>>> origin/main

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Engine for aggregating multiple model outputs into a consolidated result.
    """

    def __init__(self, orchestrator: Any = None):
        """
        Initialize the ConsensusEngine.

        Args:
            orchestrator: Optional reference to ModelOrchestrator for running synthesis.
        """
        self.orchestrator = orchestrator

    async def consolidate(self, request: ConsensusRequest) -> str:
        """
        Consolidate multiple candidate responses into a single answer.

        Args:
            request: ConsensusRequest object containing task, candidates, etc.

        Returns:
            str: Synthesized response
        """
        logger.info(
            f"Consolidating {len(request.candidates)} candidates using "
            f"{request.strategy} strategy with stance='{request.stance}'"
        )

        # 1. Prepare Prompt
        formatted_candidates = "\n\n".join(
            [f"--- Candidate {i+1} ---\n{c}" for i, c in enumerate(request.candidates)]
        )

        prompt = SYNTHESIS_TEMPLATE.format(
            task=request.task,
            context=request.context or "None",
            stance=request.stance or "Neutral/Objective",
            candidates=formatted_candidates,
        )
<<<<<<< HEAD
        logger.debug(f"Synthesis prompt: {prompt}")
=======
>>>>>>> origin/main

        # 2. Execute Consensus Logic
        # (Stub implementation for PR #5 - in full implementation, this calls the orchestrator)
        # We would likely route this to a high-reasoning model (e.g. Claude 3.5 Sonnet or Opus)

        msg = (
            f"[Consensus Engine]\n"
            f"Strategy: {request.strategy}\n"
            f"Stance: {request.stance}\n"
            f"Synthesized from {len(request.candidates)} inputs."
        )

        if self.orchestrator:
            current_context = f"{request.context or ''}\n\nTask: {request.task}"

            # Multi-round debate loop
            for round_num in range(request.rounds):
                logger.info(f"Consensus Round {round_num + 1}/{request.rounds}")

                # 1. Update candidates based on previous round (if not first)
                # In a full agentic implementation, we would re-query models here with the current synthesis
                # For now, we simulate convergence by appending the synthesis to context

                # 2. Synthesize
                prompt = SYNTHESIS_TEMPLATE.format(
                    task=request.task,
                    context=current_context,
                    stance=f"{request.stance} ({request.strength.value} strength)",
                    candidates=formatted_candidates,
                )

                response = await self.orchestrator.route_request(prompt)
                result = response.content

                # Update context for next round
                current_context += f"\n\nRound {round_num + 1} Synthesis:\n{result}"
                msg = result  # Final result is last round

        return msg
