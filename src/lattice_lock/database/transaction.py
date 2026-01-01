"""
Transaction management utilities for business operations spanning multiple repositories.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from lattice_lock.database.connection import DatabaseManager
from lattice_lock.exceptions import LatticeError

logger = logging.getLogger(__name__)


class TransactionError(LatticeError):
    """Error during transaction execution."""

    error_code: str = "LL-DB-TX-001"


@asynccontextmanager
async def transaction_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for transaction management.

    Provides a session that automatically commits on success or rolls back on exception.
    """
    async with DatabaseManager.get_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise TransactionError("Transaction failed") from e
