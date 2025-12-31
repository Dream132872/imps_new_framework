"""Picture entity related events"""

from typing import Any

from shared.domain.events import DomainEvent


class PictureUpdatedImageEvent(DomainEvent):
    def __init__(self, picture_id: str, old_image_name: str, new_image_name: str):
        super().__init__(picture_id, "PictureUpdatedImage")
        self.old_image_name = old_image_name
        self.new_image_name = new_image_name

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "old_image_name": self.old_image_name,
                "new_image_name": self.new_image_name,
            }
        )
        return base_dict
