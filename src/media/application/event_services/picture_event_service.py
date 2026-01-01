"""Picture domain event service."""

from media.application.event_handlers.picture_event_handlers import (
    PictureUpdatedImageEventHandler,
)
from shared.application.event_service import BaseEventService

__all__ = ("PictureEventService",)


class PictureEventService(BaseEventService):
    def _register_handlers(self):
        self.event_bus.subscribe(
            "PictureUpdatedImage", PictureUpdatedImageEventHandler()
        )


picture_event_service = PictureEventService()
