import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(".lattice/cost.db")

class CostTracker:
    """
    Tracks usage and cost telemetry using a local SQLite database.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS usage_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        model TEXT,
                        provider TEXT,
                        input_tokens INTEGER,
                        output_tokens INTEGER,
                        cost REAL
                    )
                """)
        except Exception as e:
            logger.error(f"Failed to initialize Cost DB: {e}")

    def record_usage(self, model: str, provider: str, input_tokens: int, output_tokens: int, cost: float):
        """Record a single usage event."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO usage_logs (model, provider, input_tokens, output_tokens, cost)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (model, provider, input_tokens, output_tokens, cost)
                )
            logger.debug(f"Recorded usage for {model}: ${cost:.4f}")
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

    def get_total_spend(self) -> float:
        """Get total project spend."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT sum(cost) FROM usage_logs")
                row = cursor.fetchone()
                return row[0] if row and row[0] else 0.0
        except Exception:
            return 0.0
