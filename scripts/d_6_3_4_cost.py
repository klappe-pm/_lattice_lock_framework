
# IMPLEMENTATION PROTOTYPE (Agent D_6_3_4)
# Task 6.3.4: Cost Tracking Implementation

import sqlite3
import datetime
from pathlib import Path

DB_PATH = ".lattice/cost.db"

class CostTracker:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        Path(DB_PATH).parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model TEXT,
                provider TEXT,
                cost REAL
            )
        """)
        conn.commit()
        conn.close()
        print(f"[COST] Database initialized at {DB_PATH}")

    def record(self, model: str, provider: str, cost: float):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO usage_logs (model, provider, cost) VALUES (?, ?, ?)",
            (model, provider, cost)
        )
        conn.commit()
        conn.close()
        print(f"[COST] Recorded: {model} (${cost:.4f})")

    def show_report(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("SELECT sum(cost) FROM usage_logs")
        row = cursor.fetchone()
        total = row[0] if row and row[0] else 0.0
        print(f"\n[REPORT] Total Project Spend: ${total:.4f}")
        conn.close()

if __name__ == "__main__":
    tracker = CostTracker()
    tracker.record("gpt-4o", "openai", 0.02)
    tracker.show_report()
