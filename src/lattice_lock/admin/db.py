import os
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger("lattice_lock.admin.db")

# Default to SQLite for development, can be overridden by LATTICE_DATABASE_URL
DATABASE_URL = os.environ.get(
    "LATTICE_DATABASE_URL", 
    "sqlite+aiosqlite:///./.lattice-lock/lattice.db"
)

# Lazy initialization to avoid import-time failures when aiosqlite is not installed
_engine = None
_async_session = None

def _ensure_db_dir():
    """Ensure the directory for SQLite exists."""
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.split("///")[-1]
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        _ensure_db_dir()
        _engine = create_async_engine(DATABASE_URL, echo=False)
    return _engine

def get_async_session():
    """Get or create the async session maker."""
    global _async_session
    if _async_session is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _async_session = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _async_session

# For backwards compatibility
@property
def engine():
    return get_engine()

@property
def async_session():
    return get_async_session()

# Base class for models - this can be imported without triggering engine creation
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

async def get_db():
    """Dependency for getting async database session."""
    session_maker = get_async_session()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
