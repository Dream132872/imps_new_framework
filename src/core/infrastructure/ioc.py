"""
Inversion of Control in Core layer.
"""

from injector import Binder, Module

from core.domain.repositories import ChunkUploadRepository, UserRepository
from core.domain.services import ChunkUploadService, FileStorageService
from core.infrastructure.repositories import (
    DjangoChunkUploadRepository,
    DjangoUserRepository,
)
from core.infrastructure.services import (
    DjangoChunkUploadService,
    DjangoFileStorageService,
)


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)
        binder.bind(ChunkUploadRepository, DjangoChunkUploadRepository)
        binder.bind(FileStorageService, DjangoFileStorageService)
        binder.bind(ChunkUploadService, DjangoChunkUploadService)
