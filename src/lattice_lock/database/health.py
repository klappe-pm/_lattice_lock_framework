"""
Database health checking for monitoring and dependency validation.
"""

import logging
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
            result = await session.execute(text("SELECT 1"))
            _ = result.scalar()

            return {
                "status": "healthy",
                "database": "connected",
                "latency_ms": 0,  # Placeholder for actual timing
                "connections_in_pool": 1,  # Placeholder for actual metrics
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
