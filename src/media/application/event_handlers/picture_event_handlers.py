"""Picture entity related event handlers"""

from media.domain.events.picture_events import PictureUpdatedImageEvent
from shared.domain.events import DomainEvent, EventHandler


class PictureUpdatedImageEventHandler(EventHandler):
    def handle(self, event: PictureUpdatedImageEvent) -> None:  # type: ignore
        print("picture updated image handled successfully")
        print(
            f"old_image_name: {event.old_image_name}, new_image_name: {event.new_image_name}"
        )

    async def handle_async(self, event: DomainEvent) -> None:
        print("picture updated image handled successfully async")
        print(
            f"old_image_name: {event.old_image_name}, new_image_name: {event.new_image_name} async"
        )
