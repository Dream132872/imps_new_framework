"""
Inversion of Control bindings for chunk_upload bounded context.
"""

from injector import Binder, Module

from chunk_upload.domain.repositories import ChunkUploadRepository
from chunk_upload.domain.services import ChunkUploadService
from chunk_upload.infrastructure.repositories import DjangoChunkUploadRepository
from chunk_upload.infrastructure.services import DjangoChunkUploadService


class ChunkUploadModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(ChunkUploadRepository, DjangoChunkUploadRepository)
        binder.bind(ChunkUploadService, DjangoChunkUploadService)


