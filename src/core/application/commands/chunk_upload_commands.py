"""
Chunk Upload Commands for CQRS implementation.
Commands handle write operations for chunk upload functionality.
"""

from dataclasses import dataclass
from typing import BinaryIO

from shared.application.cqrs import Command

__all__ = (
    "CreateChunkUploadCommand",
    "UploadChunkCommand",
    "CompleteChunkUploadCommand",
)


@dataclass
class CreateChunkUploadCommand(Command):
    filename: str
    total_size: int


@dataclass
class UploadChunkCommand(Command):
    upload_id: str
    chunk: BinaryIO
    offset: int
    chunk_size: int


@dataclass
class CompleteChunkUploadCommand(Command):
    upload_id: str
    content_type_id: int
    object_id: str
    picture_type: str
    title: str
    alternative: str
    picture_id: str | None = None


