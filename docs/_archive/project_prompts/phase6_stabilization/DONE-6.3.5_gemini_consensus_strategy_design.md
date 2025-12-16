# Task 6.3.5: Multi-Model Consensus Strategy Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.3.6 (Devin AI)

---

## 1. Concept
For high-stakes decisions (e.g., "Is this code secure?"), relying on a single model is risky. **Consensus** queries multiple distinct models and aggregates their answers.

## 2. Strategies

### Strategy A: Voting (Classification)
*   **Use Case:** Boolean checks (True/False), Classification (A/B/C).
*   **Method:** Query 3 models. Majority wins.
*   **Example:** Sheriff validation "Does this violate architecture?"

### Strategy B: Best-of-N (Generation)
*   **Use Case:** Code generation.
*   **Method:** Generate N variations. Have an (N+1)th "Judge" model score them. Pick the highest score.

### Strategy C: Debate (Refinement)
*   **Use Case:** Complex Architecture.
*   **Method:** Model A proposes. Model B critiques. Model A revises.

## 3. API Design

```python
class ConsensusEngine:
    async def run_voting(
        self,
        prompt: str,
        models: List[str],
        timeout: float
    ) -> ConsensusResult:
        ...

@dataclass
class ConsensusResult:
    winner: Any
    agreement_score: float # 0.0 to 1.0
    details: Dict[str, Any]
```

## 4. Lattice.yaml Integration
Users can classify rules as `critical`. Critical rules automatically trigger Consensus Voting (e.g., using both GPT-4 and Claude 3.5).

```yaml
rules:
  - id: "security-check"
    severity: "critical"
    consensus: true # Implies multi-model check
```

## 5. Implementation Plan
1.  Implement `ConsensusEngine` class.
2.  Implement `VotingStrategy` (easier start).
3.  Add CLI command: `lattice-lock orchestrator consensus "Is this safe?" --models gpt-4o,claude-3-opus`.
