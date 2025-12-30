"""
Example tests demonstrating repository pattern testing approach.
"""

from unittest.mock import MagicMock

import pytest

from lattice_lock.database.repository import (
    EntityNotFoundError,
    SQLAlchemyRepository,
)


class MockEntity:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


class MockRepository(SQLAlchemyRepository[MockEntity]):
    def __init__(self):
        super().__init__(MockEntity)
        self._storage = {}

    async def create(self, session, entity):
        self._storage[entity.id] = entity
        return entity

    async def get_by_id(self, session, entity_id):
        return self._storage.get(entity_id)

    async def update(self, session, entity):
        self._storage[entity.id] = entity
        return entity

    async def delete(self, session, entity_id):
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    async def list_all(self, session):
        return list(self._storage.values())


@pytest.mark.asyncio
async def test_repository_pattern_example():
    """Example test showing repository pattern usage."""
    repo = MockRepository()
    mock_session = MagicMock()

    # Create entity
    entity = MockEntity("1", "Test")
    result = await repo.create(mock_session, entity)
    assert result.id == "1"

    # Get by ID
    retrieved = await repo.get_by_id(mock_session, "1")
    assert retrieved.name == "Test"

    # Helper get_or_raise
    retrieved_safe = await repo._get_or_raise(mock_session, "1")
    assert retrieved_safe.id == "1"

    # Entity not found
    with pytest.raises(EntityNotFoundError):
        await repo._get_or_raise(mock_session, "nonexistent")


@pytest.mark.asyncio
async def test_repository_methods():
    repo = MockRepository()
    mock_session = MagicMock()

    entity = MockEntity("2", "Test2")
    await repo.create(mock_session, entity)

    # List
    all_items = await repo.list_all(mock_session)
    assert len(all_items) == 1

    # Update
    entity.name = "Test2Updated"
    await repo.update(mock_session, entity)
    updated = await repo.get_by_id(mock_session, "2")
    assert updated.name == "Test2Updated"

    # Delete
    deleted = await repo.delete(mock_session, "2")
    assert deleted is True
    assert await repo.get_by_id(mock_session, "2") is None
