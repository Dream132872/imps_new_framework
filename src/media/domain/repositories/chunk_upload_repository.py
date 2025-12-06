"""
Chunk upload domain repository interface (moved from core bounded context).
"""

from abc import abstractmethod
from uuid import UUID

from media.domain.entities import ChunkUpload
from shared.domain.repositories import Repository

__all__ = ("ChunkUploadRepository",)


class ChunkUploadRepository(Repository[ChunkUpload]):
    """Chunk upload repository interface."""

    @abstractmethod
    def get_by_upload_id(self, upload_id: str | UUID) -> ChunkUpload:
        """Get chunk upload by upload_id."""
        raise NotImplementedError

