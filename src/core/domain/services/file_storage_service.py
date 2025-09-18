"""
File storage domain service interface.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO

__all__ = ("FileStorageService",)


class FileStorageService(ABC):
    """Domain service interface for file storage system."""

    @abstractmethod
    def save_image(self, file_content: BinaryIO, image_name: str) -> str:
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
