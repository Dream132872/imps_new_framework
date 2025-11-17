"""
Attachment Commands for CQRS implementation.
Commands handle write operations that change the state of the system.
"""

import uuid
from dataclasses import dataclass
from typing import BinaryIO

from shared.application.cqrs import Command


@dataclass
class CreateAttachmentCommand(Command):
    content_type_id: int
    object_id: uuid.UUID
    file: BinaryIO
    title: str


@dataclass
class UpdateAttachmentCommand(Command):
    attachment_id: uuid.UUID
    content_type_id: int
    object_id: uuid.UUID
    file: BinaryIO | None
    title: str


@dataclass
class DeleteAttachmentCommand(Command):
    pk: uuid.UUID

