"""
Database connection management with environment-aware configuration.
"""

import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from lattice_lock.config import get_config
from lattice_lock.exceptions import LatticeError

logger = logging.getLogger(__name__)


class DatabaseConnectionError(LatticeError):
    """Error connecting to database."""

    error_code: str = "LL-DB-CONN-001"


class DatabaseManager:
    """Singleton database connection manager."""

    _engine: AsyncEngine | None = None
    _session_factory: sessionmaker | None = None

    @classmethod
    def initialize(cls):
        """Initialize database connection pool."""
        if cls._engine is not None:
            return

        config = get_config()
        try:
            cls._engine = create_async_engine(
                config.database_url,
                echo=config.database_echo,
                pool_size=config.database_pool_size,
                max_overflow=config.database_max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                isolation_level="SERIALIZABLE",
            )
            cls._session_factory = sessionmaker(
                cls._engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info(f"Database initialized: {config.database_url.split('://')[0]}")
        except Exception as e:
            logger.critical(f"Database initialization failed: {str(e)}")
            raise DatabaseConnectionError("Database connection failed") from e

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncSession:
        """Get database session with automatic cleanup."""
        if cls._session_factory is None:
            cls.initialize()

        session: AsyncSession = cls._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @classmethod
    async def dispose(cls):
        """Dispose database connections for shutdown/testing."""
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            logger.info("Database connections disposed")
