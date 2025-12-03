"""
Data transfer object for picture.
"""

from datetime import datetime
import uuid
from dataclasses import dataclass

from shared.application.dtos.file_field import FileFieldDTO

__all__ = ("PictureDTO",)


@dataclass
class PictureDTO:
    """Data Transfer Object for picture."""

    id: str
    image: FileFieldDTO
    picture_type: str
    title: str
    alternative: str
    content_type_id: int
    object_id: int | str
    created_at: datetime
    updated_at: datetime

