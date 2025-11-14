"""
Chunk upload domain service interface.
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
        """Append a chunk to the upload.

        Args:
            upload_id: Unique identifier for the upload session.
            chunk: The chunk data to append.
            offset: The byte offset where this chunk should be written.
            chunk_size: Size of the chunk in bytes.

        Returns:
            int: The new total uploaded size after appending this chunk.
        """
        pass

    @abstractmethod
    def get_completed_file(self, upload_id: str) -> BinaryIO:
        """Get the completed file from chunks.

        Args:
            upload_id: Unique identifier for the upload session.

        Returns:
            BinaryIO: The completed file object.
        """
        pass

    @abstractmethod
    def cleanup_upload(self, upload_id: str) -> None:
        """Clean up temporary files for an upload.

        Args:
            upload_id: Unique identifier for the upload session.
        """
        pass

