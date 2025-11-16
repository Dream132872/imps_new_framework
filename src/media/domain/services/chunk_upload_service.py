"""
Chunk upload domain service interface (moved from core bounded context).
"""

from abc import ABC, abstractmethod
from typing import BinaryIO

__all__ = ("ChunkUploadService",)


class ChunkUploadService(ABC):
    """Domain service interface for chunk upload operations."""

    @abstractmethod
    def append_chunk(
        self, upload_id: str, chunk: BinaryIO, offset: int, chunk_size: int
    ) -> int:
        """Append a chunk to the upload."""
        raise NotImplementedError

    @abstractmethod
    def get_completed_file(self, upload_id: str) -> BinaryIO:
        """Get the completed file from chunks."""
        raise NotImplementedError

    @abstractmethod
    def cleanup_upload(self, upload_id: str) -> None:
        """Clean up temporary files for an upload."""
        raise NotImplementedError

