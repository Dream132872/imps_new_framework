"""
Picture related domain implementations.
"""

from datetime import datetime
from typing import Any

from shared.domain.entities import AggregateRoot
from shared.domain.events import Any

__all__ = ("Picture",)


class Picture(AggregateRoot):
    def __init__(
        self,
        image: str,
        picture_type: str,
        content_type: str | None = None,
        object_id: str | None = None,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        title: str | None = None,
        alternative: str | None = None,
    ) -> None:
        super().__init__(id, created_at, updated_at)
        self._image = image
        self._picture_type = picture_type
        self._alternative = alternative or ""
        self._title = title or ""
        self._content_type = content_type or ""
        self._object_id = object_id or ""

    @property
    def image(self) -> str:
        return self._image

    @property
    def alternative(self) -> str:
        return self._alternative

    @property
    def title(self) -> str:
        return self._title

    @property
    def picture_type(self) -> str:
        return self._picture_type

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def object_id(self) -> str:
        return self._object_id

    def update_image(self, new_image_path: str) -> None:
        """Update the image itself.

        Args:
            new_image_path (str): new address of the image.
        """
        old_image = self.image
        self._image = new_image_path
        self.update_timestamp()

    def update_information(
        self, title: str | None = None, alternative: str | None = None
    ) -> None:
        """Update picture information.

        Args:
            title (str | None, optional): title of the image. Defaults to None.
            alternative (str | None, optional): alternative of the image. Defaults to None.
        """
        if title:
            self._title = title

        if alternative:
            self._alternative = alternative

        self.update_timestamp()

    def __str__(self) -> str:
        return f"{self.image}"

    def __repr__(self) -> str:
        return f"<PictureEntity id={self.id} image={self.image} />"

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {"image": self.image, "title": self.title, "alternative": self.alternative}
        )
        return base_dict
