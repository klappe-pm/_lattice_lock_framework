
# IMPLEMENTATION PROTOTYPE (Agent C_4_4)
# Task 4.4: User Feedback Integration

import json
from datetime import datetime
from pathlib import Path

FEEDBACK_FILE = ".lattice/feedback.jsonl"

def submit_feedback(rating: int, comment: str, project: str):
    """
    Simulates submitting user feedback to a central telemetry endpoint.
    For now, logs to a local JSONL file.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "project": project,
        "rating": rating,
        "comment": comment
    }

    Path(FEEDBACK_FILE).parent.mkdir(exist_ok=True)

    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[FEEDBACK] Recorded: {rating}/5 - '{comment}'")

if __name__ == "__main__":
    submit_feedback(5, "Works great!", "alpha-service")
    submit_feedback(3, "Validation is too strict", "beta-service")
