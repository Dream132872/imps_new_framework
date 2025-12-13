"""
Implementation of FileField aggregate roots.
"""

from enum import Enum
from typing import Any

from django.utils.translation import gettext_lazy as _

from .base import *

__all__ = (
    "FileFieldType",
    "FileField",
)


class FileFieldType(Enum):
    IMAGE = "image"
    FILE = "file"
    NONE = "none"


class FileField(ValueObject):
    def __init__(
        self,
        file_type: FileFieldType | str,
        name: str,
        path: str,
        url: str | None = None,
        size: int | None = None,
        width: int | None = None,
        height: int | None = None,
        content_type: str | None = None,
    ) -> None:

        if isinstance(file_type, FileFieldType):
            self._file_type = file_type
        elif isinstance(file_type, str):
            self._file_type = FileFieldType(file_type)
        else:
            raise ValueError(
                _("Invalid value. valid types are: {types}").format(
                    types=", ".join([a.value for a in FileFieldType])
                )
            )

        self._path = path
        self._url = url
        self._name = name
        self._size = size
        self._width = width
        self._height = height
        self._content_type = content_type

    @property
    def file_type(self) -> FileFieldType:
        return self._file_type

    @property
    def path(self) -> str:
        return self._path

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int | None:
        return self._size

    @property
    def width(self) -> int | None:
        return self._width

    @property
    def height(self) -> int | None:
        return self._height

    @property
    def content_type(self) -> str | None:
        return self._content_type

    def is_image(self) -> bool:
        return self.file_type.value == FileFieldType.IMAGE.value

    def has_dimensions(self) -> bool:
        return self._width is not None and self._height is not None

    def get_dimensions(self) -> tuple[int, int] | None:
        if self.has_dimensions():
            return (self._width, self._height)  # type: ignore

        return None

    def _get_equality_components(self) -> tuple:
        return (
            self._file_type,
            self._path,
            self._url,
            self._name,
            self._size,
            self._width,
            self._height,
            self._content_type,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_type": self._file_type.value,
            "url": self._url,
            "name": self._name,
            "size": self._size,
            "width": self._width,
            "height": self._height,
            "content_type": self._content_type,
        }
