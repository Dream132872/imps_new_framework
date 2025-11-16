"""
Inversion of Control bindings for media bounded context.
"""

from injector import Binder, Module

from media.domain.repositories import ChunkUploadRepository, PictureRepository
from media.domain.services import ChunkUploadService
from media.infrastructure.repositories import (
    DjangoChunkUploadRepository,
    DjangoPictureRepository,
)
from media.infrastructure.services import DjangoChunkUploadService


class MediaModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(PictureRepository, DjangoPictureRepository)
        binder.bind(ChunkUploadRepository, DjangoChunkUploadRepository)
        binder.bind(ChunkUploadService, DjangoChunkUploadService)

