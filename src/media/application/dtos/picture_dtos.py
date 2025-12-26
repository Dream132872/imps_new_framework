"""
Data transfer object for picture.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass

from shared.application.dtos.file_field import FileFieldDTO

__all__ = ("PictureDTO",)


@dataclass
class PictureDTO:
    """Data Transfer Object for picture."""

    id: uuid.UUID
    image: FileFieldDTO
    picture_type: str
    title: str
    alternative: str
    content_type_id: int
    object_id: int | str
    created_at: datetime
    updated_at: datetime

