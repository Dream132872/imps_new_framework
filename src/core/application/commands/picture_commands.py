"""
Picture Commands for CQRS implementation.
Commands handle write operations that change the state of the system.
"""

import uuid
from dataclasses import dataclass
from typing import BinaryIO

from shared.application.cqrs import Command


@dataclass
class CreatePictureCommand(Command):
    content_type_id: int
    object_id: uuid.UUID
    picture_type: str
    image: BinaryIO
    title: str
    alternative: str


@dataclass
class UpdatePictureCommand(Command):
    picture_id: uuid.UUID
    content_type_id: int
    object_id: uuid.UUID
    picture_type: str
    image: BinaryIO | None
    title: str
    alternative: str


@dataclass
class DeletePictureCommand(Command):
    pk: uuid.UUID


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
    object_id: uuid.UUID
    picture_type: str
    title: str
    alternative: str
    picture_id: uuid.UUID | None = None