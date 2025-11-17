"""
Data transfer object for attachment.
"""

from datetime import datetime
from dataclasses import dataclass

from shared.application.dtos.file_field import FileFieldDTO

__all__ = ("AttachmentDTO",)


@dataclass
class AttachmentDTO:
    """Data Transfer Object for attachment."""

    id: str
    file: FileFieldDTO
    title: str
    content_type: int
    object_id: int | str
    created_at: datetime
    updated_at: datetime

