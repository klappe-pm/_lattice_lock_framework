"""Base repository with common CRUD operations.

This module provides a generic repository pattern implementation for
all database models.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from lattice_lock.database.models.base import Base
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository with common CRUD operations.

    Subclass this to create model-specific repositories with
    additional query methods.

    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)

            async def find_by_email(self, email: str) -> User | None:
                return await self.find_one(email=email)
    """

    def __init__(self, model_class: type[T], session: AsyncSession):
        """Initialize the repository.

        Args:
            model_class: The SQLAlchemy model class.
            session: Async database session.
        """
        self.model_class = model_class
        self.session = session

    async def create(self, **kwargs: Any) -> T:
        """Create a new entity.

        Args:
            **kwargs: Model field values.

        Returns:
            The created entity.
        """
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get(self, id: str) -> T | None:
        """Get an entity by ID.

        Args:
            id: Entity primary key.

        Returns:
            The entity or None if not found.
        """
        return await self.session.get(self.model_class, id)

    async def get_or_raise(self, id: str) -> T:
        """Get an entity by ID or raise an exception.

        Args:
            id: Entity primary key.

        Returns:
            The entity.

        Raises:
            ValueError: If entity not found.
        """
        entity = await self.get(id)
        if entity is None:
            raise ValueError(f"{self.model_class.__name__} with id {id} not found")
        return entity

    async def find_one(self, **filters: Any) -> T | None:
        """Find a single entity matching filters.

        Args:
            **filters: Field=value filters.

        Returns:
            The entity or None if not found.
        """
        stmt = select(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        **filters: Any,
    ) -> Sequence[T]:
        """Find all entities matching filters.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.
            order_by: Column name to order by (prefix with - for desc).
            **filters: Field=value filters.

        Returns:
            Sequence of matching entities.
        """
        stmt = select(self.model_class).filter_by(**filters)

        if order_by:
            if order_by.startswith("-"):
                col = getattr(self.model_class, order_by[1:])
                stmt = stmt.order_by(col.desc())
            else:
                col = getattr(self.model_class, order_by)
                stmt = stmt.order_by(col.asc())

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        """Count entities matching filters.

        Args:
            **filters: Field=value filters.

        Returns:
            Count of matching entities.
        """
        stmt = select(func.count()).select_from(self.model_class).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, id: str, **kwargs: Any) -> T | None:
        """Update an entity by ID.

        Args:
            id: Entity primary key.
            **kwargs: Fields to update.

        Returns:
            The updated entity or None if not found.
        """
        entity = await self.get(id)
        if entity is None:
            return None

        for key, value in kwargs.items():
            setattr(entity, key, value)

        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: Entity primary key.

        Returns:
            True if deleted, False if not found.
        """
        entity = await self.get(id)
        if entity is None:
            return False

        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def exists(self, **filters: Any) -> bool:
        """Check if an entity exists matching filters.

        Args:
            **filters: Field=value filters.

        Returns:
            True if exists, False otherwise.
        """
        count = await self.count(**filters)
        return count > 0
