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
        """Main handle method of event.

        Args:
            event (DomainEvent): the event object
        """
        raise NotImplementedError

    @abstractmethod
    async def handle_async(self, event: DomainEvent) -> None:
        """Main handle method of event asyncronously.

        Args:
            event (DomainEvent): the event object
        """
        raise NotImplementedError


class EventBus(ABC):
    """Event bus interface for publishing domain events"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event.

        Args:
            event (DomainEvent): Instance of domain event.

        Raises:
            NotImplementedError: you should implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    async def publish_async(self, event: DomainEvent) -> None:
        """Publish a domain event  asyncronously.

        Args:
            event (DomainEvent): Instance of domain event.

        Raises:
            NotImplementedError: You should implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to a specific event type.

        Args:
            event_type (str): type of the event (Name of the event).
            handler (EventHandler): handler of this event type.

        Raises:
            NotImplementedError: You should implment this method.
        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe from a specific event type.

        Args:
            event_type (str): Type of the event (Name of the event)
            handler (EventHandler): Handler of this event type.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


class InMemoryEventBus(EventBus):
    """
    In-Memory implementation of EventBus.
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}

    def publish(self, event: DomainEvent):
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            handler.handle(event)

    async def publish_async(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler.handle_async(event)

    def subscribe(self, event_type: str, handler: EventHandler):
        if not event_type in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler):
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]


def get_event_bus(event_bus_type: str = "in_memory") -> EventBus:
    """
    gets required event bus based on type you pass

    Args:
        event_bus_type (str, optional): type of the event bus that you want. Defaults to "in_memory".

    Returns:
        EventBus: an instance of EventBus interface implementation
    """

    event_buses = {
        "in_memory": InMemoryEventBus,
    }

    if not event_bus_type in event_buses:
        raise KeyError(f"Event bus ('{event_bus_type}') does not exists.")

    return event_buses[event_bus_type]()
