"""
Django implementation of chunk upload service.
"""

import os
import shutil
import time
from io import BytesIO
from typing import BinaryIO

from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from injector import inject

from core.domain.entities.chunk_upload import ChunkUpload
from core.domain.exceptions.chunk_upload import (
    ChunkUploadInvalidEntityError,
    ChunkUploadNotFoundError,
    ChunkUploadValidationError,
)
from core.domain.repositories import ChunkUploadRepository
from core.domain.services.chunk_upload_service import ChunkUploadService

__all__ = ("DjangoChunkUploadService",)


class DjangoChunkUploadService(ChunkUploadService):
    """Django implementation of chunk upload service."""

    @inject
    def __init__(self, chunk_upload_repository: ChunkUploadRepository) -> None:
        self.chunk_upload_repository = chunk_upload_repository

    def append_chunk(
        self, upload_id: str, chunk: BinaryIO, offset: int, chunk_size: int
    ) -> int:
        chunk_upload = self.chunk_upload_repository.get_by_upload_id(upload_id)
        if not chunk_upload:
            raise ChunkUploadNotFoundError(
                _("Upload session {upload_id} not found").format(upload_id=upload_id)
            )

        if chunk_upload.status == "completed":
            return chunk_upload.uploaded_size

        if chunk_upload.status == "failed":
            raise ChunkUploadInvalidEntityError(_("Upload session has failed"))

        chunk_upload.set_status("uploading")

        chunk_dir = f"chunks/{upload_id}"
        chunk_file_path = os.path.join(chunk_dir, f"chunk_{offset}.tmp")

        # Read chunk data - handle both UploadedFile and bytes
        if hasattr(chunk, "read"):
            # It's a file-like object (UploadedFile)
            chunk.seek(0)  # Ensure we're at the start
            chunk_data = chunk.read()
        elif isinstance(chunk, bytes):
            # It's already bytes
            chunk_data = chunk
        else:
            raise ValueError(f"Unsupported chunk type: {type(chunk)}")

        # Save chunk data to temporary file
        chunk_file = BytesIO(chunk_data)
        chunk_file.name = f"chunk_{offset}.tmp"
        default_storage.save(chunk_file_path, chunk_file)

        if not chunk_upload.temp_file_path:
            name, ext = os.path.splitext(chunk_upload.filename)
            final_path = f"chunks/{upload_id}/file{ext}"
            chunk_upload.set_temp_file_path(final_path)

        self._merge_chunk(chunk_upload, chunk_file_path, offset)

        chunk_upload.update_uploaded_size(chunk_upload.uploaded_size + chunk_size)
        chunk_upload.increment_chunk_count()

        if chunk_upload.uploaded_size >= chunk_upload.total_size:
            chunk_upload.set_status("completed")
        else:
            chunk_upload.set_status("uploading")

        chunk_upload = self.chunk_upload_repository.save(chunk_upload)

        # Clean up temporary chunk file
        try:
            default_storage.delete(chunk_file_path)
        except Exception:
            pass

        return chunk_upload.uploaded_size

    def _merge_chunk(
        self, chunk_upload: ChunkUpload, chunk_path: str, offset: int
    ) -> None:
        """Merge a chunk into the final file by appending sequentially."""
        if not chunk_upload.temp_file_path:
            return

        with default_storage.open(chunk_path, "rb") as chunk_file:
            chunk_data = chunk_file.read()

        if default_storage.exists(chunk_upload.temp_file_path):
            with default_storage.open(
                chunk_upload.temp_file_path, "rb"
            ) as existing_file:
                existing_data = existing_file.read()

            if offset == 0:
                new_data = chunk_data
            elif offset == len(existing_data):
                new_data = existing_data + chunk_data
            else:
                new_data = existing_data[:offset] + chunk_data

            with default_storage.open(chunk_upload.temp_file_path, "wb") as final_file:
                final_file.write(new_data)
        else:
            if offset == 0:
                # Save initial chunk data
                chunk_file_obj = BytesIO(chunk_data)
                chunk_file_obj.name = chunk_upload.filename
                default_storage.save(chunk_upload.temp_file_path, chunk_file_obj)
            else:
                # Create file with padding for offset
                padding = b"\x00" * offset
                padded_data = padding + chunk_data
                chunk_file_obj = BytesIO(padded_data)
                chunk_file_obj.name = chunk_upload.filename
                default_storage.save(chunk_upload.temp_file_path, chunk_file_obj)

    def get_completed_file(self, upload_id: str) -> BinaryIO:
        chunk_upload = self.chunk_upload_repository.get_by_upload_id(upload_id)
        if not chunk_upload:
            raise ValueError(f"Upload session {upload_id} not found")

        if not chunk_upload.is_complete():
            raise ValueError("Upload is not complete yet")

        if not chunk_upload.temp_file_path:
            raise ValueError("No file path available")

        if not default_storage.exists(chunk_upload.temp_file_path):
            raise ValueError("Completed file not found")

        # Read file content into memory and return BytesIO to avoid file locking issues
        with default_storage.open(chunk_upload.temp_file_path, "rb") as file:
            file_data = file.read()

        # File is now closed, create BytesIO from the data
        file_obj = BytesIO(file_data)
        file_obj.name = chunk_upload.filename
        # Ensure we're at the start of the file
        file_obj.seek(0)
        return file_obj

    def cleanup_upload(self, upload_id: str) -> None:
        chunk_upload = self.chunk_upload_repository.get_by_upload_id(upload_id)
        if not chunk_upload:
            return

        temp_file_path = chunk_upload.temp_file_path

        # Small delay to ensure file handles are released (Windows issue)
        time.sleep(0.1)

        if temp_file_path and default_storage.exists(temp_file_path):
            try:
                default_storage.delete(temp_file_path)
            except Exception:
                # File might still be in use, try again after a bit
                time.sleep(0.2)
                try:
                    default_storage.delete(temp_file_path)
                except Exception:
                    pass

        # Clean up chunk directory and all its contents
        chunk_dir = f"chunks/{upload_id}"
        if default_storage.exists(chunk_dir):
            try:
                # List all files in the directory
                dirs, files = default_storage.listdir(chunk_dir)
                # Delete all files
                for file in files:
                    try:
                        file_path = os.path.join(chunk_dir, file)
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)
                    except Exception:
                        pass

                # Try to delete the directory itself if using local storage
                # Django storage API doesn't support directory deletion directly
                # So we use os operations if the storage is local
                try:
                    if hasattr(default_storage, "location"):
                        # Local file storage
                        full_dir_path = os.path.join(
                            default_storage.location, chunk_dir
                        )
                        if os.path.exists(full_dir_path):
                            time.sleep(0.1)  # Small delay for Windows
                            shutil.rmtree(full_dir_path, ignore_errors=True)
                except Exception:
                    pass
            except Exception:
                pass

        self.chunk_upload_repository.delete(chunk_upload)

