
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .models import UsageRecord

logger = logging.getLogger(__name__)

class CostStorage:
    """SQLite-based storage for usage records."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Default to .lattice/cost.db in user home or current project
            self.db_path = Path.home() / ".lattice" / "cost.db"
            
        self._ensure_db()

    def _ensure_db(self):
        """Ensure database directory and table exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS usage_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        trace_id TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        task_type TEXT NOT NULL,
                        input_tokens INTEGER DEFAULT 0,
                        output_tokens INTEGER DEFAULT 0,
                        cost_usd REAL DEFAULT 0.0,
                        metadata TEXT
                    )
                """)
                # Indexes for common queries
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_logs(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON usage_logs(session_id)")
        except Exception as e:
            logger.error(f"Failed to initialize cost database: {e}")

    def add_record(self, record: UsageRecord):
        """Save a usage record to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO usage_logs (
                        timestamp, session_id, trace_id, model_id, provider, 
                        task_type, input_tokens, output_tokens, cost_usd, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.timestamp.isoformat(),
                    record.session_id,
                    record.trace_id,
                    record.model_id,
                    record.provider,
                    record.task_type,
                    record.input_tokens,
                    record.output_tokens,
                    record.cost_usd,
                    json.dumps(record.metadata)
                ))
        except Exception as e:
            logger.error(f"Failed to save cost record: {e}")

    def get_session_total(self, session_id: str) -> float:
        """Get total cost for a specific session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT SUM(cost_usd) FROM usage_logs WHERE session_id = ?", 
                    (session_id,)
                )
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            logger.error(f"Failed to query session total: {e}")
            return 0.0

    def get_aggregates(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Get cost aggregates for the last N days."""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            aggregates = {
                "total_cost": 0.0,
                "by_provider": {},
                "by_model": {}
            }
            
            with sqlite3.connect(self.db_path) as conn:
                # Total
                cursor = conn.execute(
                    "SELECT SUM(cost_usd) FROM usage_logs WHERE timestamp >= ?", 
                    (start_date,)
                )
                total = cursor.fetchone()[0]
                aggregates["total_cost"] = total if total else 0.0

                # By Provider
                cursor = conn.execute("""
                    SELECT provider, SUM(cost_usd) 
                    FROM usage_logs 
                    WHERE timestamp >= ? 
                    GROUP BY provider
                """, (start_date,))
                for row in cursor.fetchall():
                    aggregates["by_provider"][row[0]] = row[1]

                # By Model
                cursor = conn.execute("""
                    SELECT model_id, SUM(cost_usd) 
                    FROM usage_logs 
                    WHERE timestamp >= ? 
                    GROUP BY model_id
                """, (start_date,))
                for row in cursor.fetchall():
                    aggregates["by_model"][row[0]] = row[1]
                    
            return aggregates
        except Exception as e:
            logger.error(f"Failed to query aggregates: {e}")
            return {}
