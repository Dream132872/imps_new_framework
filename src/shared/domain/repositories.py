"""
Base repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from .entities import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    """
    Base repository interface for domain entities.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity to repository."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Gets an entity by it's ID."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities from the repository."""

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity from the repository."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, id: str) -> bool:
        """Check if an entity exists by it's ID."""
        raise NotImplementedError


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface for managing transactions.
    """

    @abstractmethod
    def __enter__(self):
        """Enter the unit-of-work context."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the unit-of-work context."""
        pass

    @abstractmethod
    def commit(self):
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback the current transaction."""
        pass

    @abstractmethod
    def get_repository(self, entity_type: Type[T]) -> Repository[T]:
        """Get a repository for the specified entity type."""
        pass
