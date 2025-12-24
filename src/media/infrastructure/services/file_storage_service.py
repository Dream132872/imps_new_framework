"""
File storage infrastructure service interface and Django implementation.
"""

import os
import uuid
from abc import ABC, abstractmethod
from typing import BinaryIO

from django.core.files.storage import default_storage

__all__ = ("FileStorageService", "DjangoFileStorageService")


class FileStorageService(ABC):
    """Infrastructure service interface for file storage system."""

    @abstractmethod
    def save_image(self, file_content: BinaryIO, image_name: str | None = None) -> str:
        """save image and return the image path/url

        Args:
            file_content (BinaryIO): Binary content of the image.
            image_name (str): Original image name.

        Returns:
            str: The saved image path/url.
        """
        pass

    @abstractmethod
    def delete_image(self, image_path: str) -> None:
        """Delete an image by it's path.

        Args:
            image_path (str): Path of the image to delete.
        """
        pass

    @abstractmethod
    def image_exists(self, image_path: str) -> bool:
        """Check if image exists using Django's default storage.

        Args:
            image_path (str): Path of the image to check.

        Returns:
            bool: True if image exists, False otherwise.
        """
        pass

    @abstractmethod
    def save_file(self, file_content: BinaryIO, file_name: str | None = None) -> str:
        """save file and return the file path/url

        Args:
            file_content (BinaryIO): Binary content of the file.
            file_name (str): Original file name.

        Returns:
            str: The saved file path/url.
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """Delete a file by it's path.

        Args:
            file_path (str): Path of the file to delete.
        """
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists using Django's default storage.

        Args:
            file_path (str): Path of the file to check.

        Returns:
            bool: True if file exists, False otherwise.
        """
        pass


class DjangoFileStorageService(FileStorageService):
    """Django implementation of file storage service."""

    def save_image(self, file_content: BinaryIO, image_name: str | None = None) -> str:
        if not file_content:
            return ""

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
