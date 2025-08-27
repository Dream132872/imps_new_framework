"""
Domain events system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4

from django.utils import timezone


class DomainEvent(ABC):
    """
    Base class for domain event.
    """

    def __init__(self, aggregate_id: str, event_type: Optional[str] = None):
        self.event_id = str(uuid4())
        self.aggregate_id = aggregate_id
        self.event_type = event_type or self.__class__.__name__
        self.occurred_on = timezone.now()
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation"""
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
        }


class EventHandler(ABC):
    """Base class for event handlers."""

    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """Main handle method of event."""
        raise NotImplementedError


class EventBus(ABC):
    """Event bus interface for publishing domain events"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to a specific event type."""
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe from a specific event type."""
        raise NotImplementedError


class InMemoryEventBus(EventBus):
    """
    In-Memory implementation of EventBus.
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}

    def publish(self, event: DomainEvent):
        """Publish a domain event."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            handler.handle(event)

    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe to a specific event type."""
        if not event_type in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler):
        """Unsubscribe from a specific event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
