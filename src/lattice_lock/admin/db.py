import os
import logging
from sqlalchemy import create_all
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("lattice_lock.admin.db")

# Default to SQLite for development, can be overridden by LATTICE_DATABASE_URL
DATABASE_URL = os.environ.get(
    "LATTICE_DATABASE_URL", 
    "sqlite+aiosqlite:///./.lattice-lock/lattice.db"
)

# Ensure the directory for SQLite exists
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.split("///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    """Dependency for getting async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
