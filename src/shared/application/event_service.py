"""
Base domain event service interface
"""

from abc import ABC, abstractmethod

from shared.domain.events import DomainEvent, EventBus, get_event_bus


class BaseEventService(ABC):
    """Base event service interface."""

    def __init__(self) -> None:
        self._event_bus: EventBus = get_event_bus()
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self):
        """register all handlers."""
        pass

    @property
    def event_bus(self) -> EventBus:
        """return's the event bus instance of this class.

        Returns:
            EventBus: instance of EventBus
        """
        return self._event_bus

    def publish_event(self, event: DomainEvent):
        self.event_bus.publish(event=event)
