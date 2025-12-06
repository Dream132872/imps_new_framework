"""
Picture related domain implementations.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from django.utils.translation import gettext_lazy as _

from media.domain.exceptions import PictureValidationError
from shared.domain.entities import AggregateRoot, FileField

__all__ = ("Picture",)


class PictureType(Enum):
    """Types values for picture."""

    MAIN = "main"
    GALLERY = "gallery"
    AVATAR = "avatar"
    BANNER = "banner"

    @classmethod
    def from_string(cls, value: str) -> "PictureType":
        """Create PictureType from value.

        Args:
            value (str): picture type value as string

        Returns:
            PictureType: Valid picture type

        Raises:
            PictureValidationError: if value is invalid
        """
        try:
            return cls(value)
        except:
            raise PictureValidationError(
                _(
                    "Picture type '{picture_type}' is not valid. Valid types are: {valid_types}"
                ).format(
                    picture_type=value, valid_types=", ".join([pt.value for pt in cls])
                )
            )


class Picture(AggregateRoot):
    def __init__(
        self,
        image: FileField,
        picture_type: str | PictureType,
        content_type_id: int,
        object_id: int | str,
        id: str | None = None,
        title: str | None = None,
        alternative: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id, created_at, updated_at)

        if not image or (image.size is not None and image.size == 0):
            raise PictureValidationError(_("Image cannot be None"))

        if not content_type_id or not object_id:
            raise PictureValidationError(_("Picture should have relation information"))

        if isinstance(picture_type, str):
            self._picture_type = PictureType.from_string(picture_type)
        elif isinstance(picture_type, PictureType):
            self._picture_type = picture_type

        self._image = image
        self._alternative = alternative or ""
        self._title = title or ""
        self._content_type_id = content_type_id
        self._object_id = object_id

    @property
    def image(self) -> FileField:
        return self._image

    @property
    def alternative(self) -> str:
        return self._alternative

    @property
    def title(self) -> str:
        return self._title

    @property
    def picture_type(self) -> str:
        return self._picture_type.value

    @property
    def content_type_id(self) -> int:
        return self._content_type_id

    @property
    def object_id(self) -> int | str:
        return self._object_id

    def update_image(self, new_image: FileField) -> None:
        """Update the image itself.

        Args:
            new_image (str): new address of the image.
        """
        if not new_image or (new_image.size is not None and new_image.size == 0):
            raise PictureValidationError(_("Image cannot be None"))

        self._image = new_image
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
        return self.image.name

    def __repr__(self) -> str:
        return f"<PictureEntity id={self.id} image={self.image.name} />"

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "image": self.image.to_dict(),
                "title": self.title,
                "alternative": self.alternative,
            }
        )
        return base_dict
