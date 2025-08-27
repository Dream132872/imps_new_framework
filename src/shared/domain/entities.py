"""
Base entity and aggregate root classes.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from django.utils import timezone


class Entity(ABC):
    """Base entity class that all domain entities should inherit from."""

    def __init__(self, id: Optional[str]):
        self._id = id or str(uuid4())
        self._created_at = timezone.now()
        self._updated_at = timezone.now()

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
        self.update_timestamp = timezone.now()

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
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AggregateRoot(Entity):
    """
    Base class for aggregate roots.
    Aggregate roots are the entry-points to aggregates.
    """

    def __init__(self, id: Optional[str]):
        super().__init__(id)
        self._domain_events = []

    def add_domain_event(self, event) -> None:
        """Adds new domain event for this aggregate root"""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events of this aggregate roots"""
        self._domain_events.clear()

    @property
    def domain_events(self) -> List[Any]:
        """Get all domain events."""
        return self._domain_events


class ValueObject(ABC):
    """
    Base class for value objects.
    Value objects are immutable and defined by it's attributes
    """

    @abstractmethod
    def _get_equality_components(self) -> Tuple:
        raise NotImplementedError()

    def __eq__(self, other_value: "ValueObject"):
        """Check's the equality of this object with other object"""
        if not isinstance(other_value, self.__class__):
            return False

        return self._get_equality_components() == other_value._get_equality_components()

    def __hash__(self):
        """Get hash based on object equality components"""
        return hash(self._get_equality_components())

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Get's the dictionary representation of the value object"""
        raise NotImplementedError()
