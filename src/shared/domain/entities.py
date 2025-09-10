"""
Base entity and aggregate root classes.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from django.utils import timezone

from .events import *


class Entity(ABC):
    """Base entity class that all domain entities should inherit from."""

    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id or str(uuid4())
        self._created_at = created_at or timezone.now()
        self._updated_at = updated_at or timezone.now()

    @property
    def id(self) -> str:
        """Get the unique identifier of the entity."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp of the entity."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the last updated timestamp of the entity."""
        return self._updated_at

    @property
    def update_timestamp(self) -> None:
        """Get the last updated timestamp of the entity."""
        self._updated_at = timezone.now()

    def __eq__(self, other: Any):
        """Check the equality of this object with another object."""
        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id

    def __hash__(self):
        """Returns the hash based on the entity's id."""
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""

        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AggregateRoot(Entity):
    """
    Base class for aggregate roots.
    Aggregate roots are the entry-points to aggregates.
    """

    def __init__(
        self,
        id: Optional[str],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._domain_events = []

    def add_domain_event(self, event: DomainEvent) -> None:
        """Adds new domain event for this aggregate root.

        Args:
            event (DomainEvent): instance of domain event.
        """
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events of this aggregate roots."""
        self._domain_events.clear()

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Get all domain events."""
        return self._domain_events


class ValueObject(ABC):
    """
    Base class for value objects.
    Value objects are immutable and defined by it's attributes.
    """

    def __eq__(self, other_value: object) -> bool:
        """Check's the equality of this object with other object.

        Args:
            other_value (object): Other value to check

        Returns:
            bool: return's True if the two value match else False
        """
        if not isinstance(other_value, self.__class__):
            return False

        return self._get_equality_components() == other_value._get_equality_components()

    def __hash__(self):
        """Get hash based on object equality components"""
        return hash(self._get_equality_components())

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Get's the dictionary representation of the value object"""
        raise NotImplementedError()

    @abstractmethod
    def _get_equality_components(self) -> tuple:
        raise NotImplementedError()
