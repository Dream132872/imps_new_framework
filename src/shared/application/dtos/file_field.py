"""
Implementation of file field dto.
"""

from dataclasses import dataclass
from typing import Any


__all__ = ("FileFieldDTO",)


@dataclass()
class FileFieldDTO:
    """Information about file field."""

    file_type: str
    url: str | None
    name: str | None
    size: int | None
    width: int | None
    height: int | None
    content_type: str | None
