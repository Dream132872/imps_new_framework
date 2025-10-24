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
    id: uuid.UUID
    image: FileFieldDTO
    picture_type: str
    title: str
    alternative: str
    content_type: int
    object_id: int | uuid.UUID
    created_at: datetime
    updated_at: datetime
