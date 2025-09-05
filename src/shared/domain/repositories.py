"""
Base repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar

from .entities import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    """
    Base repository interface for domain entities.
    """

    @abstractmethod
    async def save_async(self, entity: T) -> T:
        """Save an entity to repository."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_async(self, id: str) -> Optional[T]:
        """Gets an entity by it's ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_async(self) -> List[T]:
        """Get all entities from the repository."""
        raise NotImplementedError

    @abstractmethod
    async def delete_async(self, entity: T) -> None:
        """Delete an entity from the repository."""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id_async(self, id: str) -> bool:
        """Check if an entity exists by it's ID."""
        raise NotImplementedError


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface for managing transactions.
    """

    @abstractmethod
    def __enter__(self) -> None:
        """Enter the unit-of-work context."""
        pass

    @abstractmethod
    async def __aenter__(self) -> None:
        """Enter the unit-of-work context asyncronously."""
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit-of-work context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit-of-work context asyncronously."""
        pass

    @abstractmethod
    async def commit_async(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    async def rollback_async(self) -> None:
        """Rollback the current transaction."""
        pass

    @abstractmethod
    def get_repository(self, entity_type: Type[T]) -> Repository[T]:
        """Get a repository for the specified entity type."""
        pass
