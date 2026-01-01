"""Database connection management for Cloud SQL (PostgreSQL).

This module provides async and sync database session management using SQLAlchemy,
optimized for Cloud SQL with connection pooling and health checks.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from lattice_lock.database.models.base import Base
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool


# Environment-based configuration
def _get_database_url(async_mode: bool = True) -> str:
    """Build database URL from environment variables.
    
    Supports both Cloud SQL private IP and Unix socket connections.
    
    Args:
        async_mode: If True, returns asyncpg URL; otherwise, psycopg2 URL.
        
    Returns:
        Database connection URL.
    """
    # Check for direct connection string first
    if direct_url := os.getenv("DATABASE_URL"):
        if async_mode and "postgresql://" in direct_url:
            return direct_url.replace("postgresql://", "postgresql+asyncpg://")
        return direct_url

    # Build from components
    user = os.getenv("DB_USER", "lattice_lock_app")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "lattice_lock")

    # Cloud SQL Unix socket (for Cloud Run)
    if instance_connection := os.getenv("CLOUD_SQL_CONNECTION_NAME"):
        socket_path = f"/cloudsql/{instance_connection}"
        if async_mode:
            return f"postgresql+asyncpg://{user}:{password}@/{database}?host={socket_path}"
        return f"postgresql+psycopg2://{user}:{password}@/{database}?host={socket_path}"

    # Direct TCP connection
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    if async_mode:
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


# Engine configuration
_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes


# Async engine (singleton)
_async_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_async_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _async_engine

    if _async_engine is None:
        _async_engine = create_async_engine(
            _get_database_url(async_mode=True),
            poolclass=QueuePool,
            pool_size=_POOL_SIZE,
            max_overflow=_MAX_OVERFLOW,
            pool_timeout=_POOL_TIMEOUT,
            pool_recycle=_POOL_RECYCLE,
            pool_pre_ping=True,  # Health check before each connection
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )

    return _async_engine


def _get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _async_session_factory

    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=_get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    return _async_session_factory


# Sync engine (for migrations and CLI tools)
_sync_engine = None
_sync_session_factory = None


def _get_sync_engine():
    """Get or create the sync database engine."""
    global _sync_engine

    if _sync_engine is None:
        _sync_engine = create_engine(
            _get_database_url(async_mode=False),
            poolclass=QueuePool,
            pool_size=_POOL_SIZE,
            max_overflow=_MAX_OVERFLOW,
            pool_timeout=_POOL_TIMEOUT,
            pool_recycle=_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )

        # Add event listener for connection setup
        @event.listens_for(_sync_engine, "connect")
        def set_search_path(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("SET search_path TO public")
            cursor.close()

    return _sync_engine


def _get_sync_session_factory():
    """Get or create the sync session factory."""
    global _sync_session_factory

    if _sync_session_factory is None:
        _sync_session_factory = sessionmaker(
            bind=_get_sync_engine(),
            expire_on_commit=False,
            autoflush=False,
        )

    return _sync_session_factory


# Public API

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    Usage:
        async with get_async_session() as session:
            result = await session.execute(...)
            
    Yields:
        AsyncSession: Database session that auto-commits on success.
    """
    session = _get_async_session_factory()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Get a sync database session.
    
    Usage:
        with get_sync_session() as session:
            result = session.execute(...)
            
    Yields:
        Session: Database session that auto-commits on success.
    """
    session = _get_sync_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_database(drop_existing: bool = False) -> None:
    """Initialize the database schema.
    
    Creates all tables defined in the models if they don't exist.
    
    Args:
        drop_existing: If True, drops all tables before creating.
                      USE WITH CAUTION in production!
    """
    engine = _get_async_engine()

    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def check_database_health() -> dict:
    """Check database connectivity and return health status.
    
    Returns:
        dict: Health status with connection info.
    """
    try:
        async with get_async_session() as session:
            result = await session.execute(text("SELECT 1 as health, version() as version"))
            row = result.fetchone()
            return {
                "status": "healthy",
                "database": "postgresql",
                "version": row.version if row else "unknown",
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(e),
        }


async def close_database() -> None:
    """Close all database connections.
    
    Call this during application shutdown.
    """
    global _async_engine, _sync_engine

    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None

    if _sync_engine:
        _sync_engine.dispose()
        _sync_engine = None
