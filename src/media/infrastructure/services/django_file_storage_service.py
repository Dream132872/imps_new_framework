"""
Django implementation of file storage service.
"""

import os
import uuid
from typing import BinaryIO

from django.core.files.storage import default_storage

from media.domain.services import FileStorageService

__all__ = ("DjangoFileStorageService",)


class DjangoFileStorageService(FileStorageService):

    def save_image(self, file_content: BinaryIO, image_name: str | None = None) -> str:
        # Ensure file is at the start
        if hasattr(file_content, "seek"):
            file_content.seek(0)

        # Get file extension from name if available
        if hasattr(file_content, "name") and file_content.name:
            name, ext = os.path.splitext(file_content.name)
        else:
            ext = ".jpg"  # Default extension

        image_path = f"images/{uuid.uuid4()}{ext}"
        return default_storage.save(image_path, file_content)

    def delete_image(self, image_path: str) -> None:
        if self.image_exists(image_path=image_path):
            default_storage.delete(image_path)

    def image_exists(self, image_path: str) -> bool:
        return bool(image_path and default_storage.exists(image_path))

    def save_file(self, file_content: BinaryIO, file_name: str | None = None) -> str:
        # Ensure file is at the start
        if hasattr(file_content, "seek"):
            file_content.seek(0)

        # Get file extension from name if available
        if hasattr(file_content, "name") and file_content.name:
            name, ext = os.path.splitext(file_content.name)
        else:
            ext = ".bin"  # Default extension

        file_path = f"attachments/{uuid.uuid4()}{ext}"
        return default_storage.save(file_path, file_content)

    def delete_file(self, file_path: str) -> None:
        if self.file_exists(file_path=file_path):
            default_storage.delete(file_path)

    def file_exists(self, file_path: str) -> bool:
        return bool(file_path and default_storage.exists(file_path))

