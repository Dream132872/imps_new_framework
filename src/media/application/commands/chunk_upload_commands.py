"""
Chunk Upload Commands for CQRS implementation (moved from core bounded context).
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

