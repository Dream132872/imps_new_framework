"""
Django implementation of file storage service.
"""

import os
import uuid
from typing import BinaryIO

from django.core.files.storage import default_storage

from core.domain.services import FileStorageService

__all__ = ("DjangoFileStorageService",)


class DjangoFileStorageService(FileStorageService):

    def save_image(self, file_content: BinaryIO, image_name: str | None = None) -> str:
        if not image_name:
            image_name = str(uuid.uuid4())

        name, ext = os.path.splitext(file_content.name)
        image_path = f"images/{uuid.uuid4()}{ext}"
        return default_storage.save(image_path, file_content)

    def delete_image(self, image_path: str) -> None:
        if self.image_exists(image_path=image_path):
            default_storage.delete(image_path)

    def image_exists(self, image_path: str) -> bool:
        return bool(image_path and default_storage.exists(image_path))
