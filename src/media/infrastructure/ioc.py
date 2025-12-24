"""
Inversion of Control bindings for media bounded context.
"""

from injector import Binder, Module

from media.domain.repositories import AttachmentRepository, ChunkUploadRepository, PictureRepository
from media.infrastructure.repositories import (
    DjangoAttachmentRepository,
    DjangoChunkUploadRepository,
    DjangoPictureRepository,
)
from media.infrastructure.services import (
    ChunkUploadService,
    DjangoChunkUploadService,
    DjangoFileStorageService,
    FileStorageService,
)


class MediaModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(PictureRepository, DjangoPictureRepository)
        binder.bind(AttachmentRepository, DjangoAttachmentRepository)
        binder.bind(ChunkUploadRepository, DjangoChunkUploadRepository)
        binder.bind(ChunkUploadService, DjangoChunkUploadService)
        binder.bind(FileStorageService, DjangoFileStorageService)

