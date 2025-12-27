"""
Repository pattern base classes for data access abstractions.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from lattice_lock.database.connection import DatabaseManager
from lattice_lock.exceptions import LatticeError

T = TypeVar('T')

class EntityNotFoundError(LatticeError):
    """Entity not found in database."""
    pass

class RepositoryInterface(ABC, Generic[T]):
    """
    Abstract repository interface defining standard CRUD operations.
    
    Provides consistent patterns for all data access objects.
    """
    
    @abstractmethod
    async def create(self, session: AsyncSession, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session: AsyncSession, entity_id: str) -> Optional[T]:
        """Retrieve entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, session: AsyncSession, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, session: AsyncSession, entity_id: str) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        pass
    
    @abstractmethod
    async def list_all(self, session: AsyncSession) -> List[T]:
        """List all entities."""
        pass


class SQLAlchemyRepository(RepositoryInterface[T], ABC):
    """
    Base class for SQLAlchemy repository implementations.
    
    Provides common functionality for SQLAlchemy-based repositories.
    """
    
    def __init__(self, model_class):
        self._model_class = model_class
    
    async def _get_or_raise(self, session: AsyncSession, entity_id: str) -> T:
        """
        Get entity or raise EntityNotFoundError.
        
        Common utility for get operations that require existence.
        """
        entity = await self.get_by_id(session, entity_id)
        if entity is None:
            raise EntityNotFoundError(f"{self._model_class.__name__} with ID {entity_id} not found")
        return entity
