"""
Chunk upload domain repository interface.
"""

from abc import abstractmethod
from uuid import UUID

from core.domain.entities.chunk_upload import ChunkUpload
from shared.domain.repositories import Repository

__all__ = ("ChunkUploadRepository",)


class ChunkUploadRepository(Repository[ChunkUpload]):
    """Chunk upload repository interface."""

    @abstractmethod
    def get_by_upload_id(self, upload_id: str | UUID) -> ChunkUpload | None:
        """Get chunk upload by upload_id.

        Args:
            upload_id: Unique upload identifier.

        Returns:
            ChunkUpload | None: Chunk upload entity or None if not found.
        """
        pass

