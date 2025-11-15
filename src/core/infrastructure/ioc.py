"""
Inversion of Control in Core layer.
"""

from injector import Binder, Module

from core.infrastructure.services import (
    DjangoChunkUploadService,
    DjangoFileStorageService,
)
from core.domain.repositories import (
    ChunkUploadRepository,
    PictureRepository,
    UserRepository,
)
from core.domain.services import ChunkUploadService, FileStorageService
from core.infrastructure.repositories import (
    DjangoChunkUploadRepository,
    DjangoPictureRepository,
    DjangoUserRepository,
)


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)
        binder.bind(PictureRepository, DjangoPictureRepository)
        binder.bind(ChunkUploadRepository, DjangoChunkUploadRepository)
        binder.bind(FileStorageService, DjangoFileStorageService)
        binder.bind(ChunkUploadService, DjangoChunkUploadService)
