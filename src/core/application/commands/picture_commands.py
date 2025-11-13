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
