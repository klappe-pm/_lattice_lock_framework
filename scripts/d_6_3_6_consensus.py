# IMPLEMENTATION PROTOTYPE (Agent D_6_3_6)
# Task 6.3.6: Consensus Strategy Implementation

import random


class ConsensusEngine:
    def execute_voting(self, prompt: str, models: list) -> str:
        """
        Queries multiple models and returns the majority vote.
        """
        print(f"[CONSENSUS] Starting vote on: '{prompt[:20]}...'")
        votes = []

        for model in models:
            # Simulate Model Response
            print(f"  [>] Querying {model}...")
            # Mock: Randomly vote 'Secure' or 'Insecure' (skewed to Secure)
            vote = "Secure" if random.random() > 0.2 else "Insecure"
            votes.append(vote)

        # Tally
        tally = {v: votes.count(v) for v in set(votes)}
        winner = max(tally, key=tally.get)
        confidence = tally[winner] / len(votes)

        print(f"[CONSENSUS] Result: {winner} (Confidence: {confidence:.2f})")
        return winner


if __name__ == "__main__":
    engine = ConsensusEngine()
    engine.execute_voting("Is eval() safe here?", ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"])
