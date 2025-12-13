"""
Base repository interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Self, TypeVar

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
    def get_by_id(self, id: str) -> T:
        """
        Gets an entity by it's ID.
        you should override this method in the implemented repository for specific Domain Entity.

        Raises:
            DomainEntityNotFoundError: when the entity does not exists by provided ID.

        Returns:
            AggregateRoot: an instance of the received entity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities from the repository."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity from the repository."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, id: str) -> bool:
        """Check if an entity exists by it's ID."""
        raise NotImplementedError


R = TypeVar("R", bound=Repository)


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface for managing transactions.
    """

    @abstractmethod
    def __enter__(self) -> Self:
        """Enter the unit-of-work context."""
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit-of-work context."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    @abstractmethod
    def _get_repository(self, repo: type[R]) -> R:
        """Get a repository for the specified repository."""
        pass

    @abstractmethod
    def __getitem__(self, repo_type: type[R]) -> R:
        pass
