"""
Chunk upload domain entity.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from shared.domain.entities import Entity

__all__ = ("ChunkUpload",)


class ChunkUpload(Entity):
    """Domain entity for chunk upload sessions."""

    def __init__(
        self,
        upload_id: UUID | str,
        filename: str,
        total_size: int,
        id: str | None = None,
        uploaded_size: int = 0,
        chunk_count: int = 0,
        temp_file_path: str | None = None,
        status: str = "pending",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id, created_at, updated_at)
        self._upload_id = str(upload_id) if isinstance(upload_id, UUID) else upload_id
        self._filename = filename
        self._total_size = total_size
        self._uploaded_size = uploaded_size
        self._chunk_count = chunk_count
        self._temp_file_path = temp_file_path
        self._status = status

    @property
    def upload_id(self) -> str:
        return self._upload_id

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def total_size(self) -> int:
        return self._total_size

    @property
    def uploaded_size(self) -> int:
        return self._uploaded_size

    @property
    def chunk_count(self) -> int:
        return self._chunk_count

    @property
    def temp_file_path(self) -> str | None:
        return self._temp_file_path

    @property
    def status(self) -> str:
        return self._status

    def is_complete(self) -> bool:
        """Check if upload is complete."""
        return self._uploaded_size >= self._total_size and self._status == "completed"

    def get_progress_percent(self) -> float:
        """Get upload progress as percentage."""
        if self._total_size == 0:
            return 0.0
        return min(100.0, (self._uploaded_size / self._total_size) * 100)

    def update_uploaded_size(self, size: int) -> None:
        """Update uploaded size."""
        self._uploaded_size = size
        self.update_timestamp()

    def increment_chunk_count(self) -> None:
        """Increment chunk count."""
        self._chunk_count += 1
        self.update_timestamp()

    def set_status(self, status: str) -> None:
        """Set upload status."""
        self._status = status
        self.update_timestamp()

    def set_temp_file_path(self, path: str) -> None:
        """Set temporary file path."""
        self._temp_file_path = path
        self.update_timestamp()

    def __str__(self) -> str:
        return f"ChunkUpload {self._upload_id} - {self._filename}"

    def __repr__(self) -> str:
        return f"<ChunkUpload id={self.id} upload_id={self._upload_id} filename={self._filename} />"

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "upload_id": self._upload_id,
                "filename": self._filename,
                "total_size": self._total_size,
                "uploaded_size": self._uploaded_size,
                "chunk_count": self._chunk_count,
                "temp_file_path": self._temp_file_path,
                "status": self._status,
                "progress": self.get_progress_percent(),
                "completed": self.is_complete(),
            }
        )
        return base_dict

