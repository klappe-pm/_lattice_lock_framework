"""
Database health checking for monitoring and dependency validation.
"""

import logging
import time
from typing import Any

from sqlalchemy import text

from lattice_lock.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


async def check_database_health() -> dict[str, Any]:
    """
    Perform database health check.

    Returns health status suitable for health endpoints and monitoring.
    """
    try:
        async with DatabaseManager.get_session() as session:
            # Simple query to verify connectivity
            # Measure latency
            start_time = time.time()
            result = await session.execute(text("SELECT 1"))
            latency = (time.time() - start_time) * 1000
            _ = result.scalar()

            # Get pool stats if available
            pool_stats = {}
            if DatabaseManager._engine:
                try:
                    pool = DatabaseManager._engine.sync_engine.pool
                    pool_stats = {
                        "connections_checked_out": pool.checkedout(),
                        "connections_overflow": pool.overflow(),
                        "pool_size": pool.size(),
                    }
                except Exception:
                    pass

            return {
                "status": "healthy",
                "database": "connected",
                "latency_ms": round(latency, 2),
                "connections_in_pool": pool_stats.get("pool_size", 0),
                **pool_stats,
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "connection_failed",
        }
