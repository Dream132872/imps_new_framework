"""
File field factory for Image and File.
"""

import mimetypes
import os
from typing import Any

from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image

from shared.domain.entities import FileField, FileType

__all__ = ("FileFieldFactory",)


class FileFieldFactory:
    @staticmethod
    def from_image_field(image_field: Any) -> FileField:
        if not image_field or not default_storage.exists(image_field.name):
            return FileField(
                file_type=FileType.NONE,
                path="",
                url=None,
                name=None,
                size=None,
                width=None,
                height=None,
                content_type=None,
            )

        return FileField(
            file_type=FileType.IMAGE,
            path=image_field.path,
            url=image_field.url,
            name=image_field.name,
            size=image_field.size,
            width=image_field.width,
            height=image_field.height,
            content_type=getattr(image_field, "content_type", None),
        )

    @staticmethod
    def from_file_field(file_field: Any) -> FileField:
        if not file_field:
            return FileField(
                file_type=FileType.FILE,
                path="",
                url=None,
                name=None,
                size=None,
                content_type=None,
            )

        return FileField(
            file_type=FileType.FILE,
            path=file_field.path,
            url=file_field.url,
            name=file_field.name,
            size=file_field.size,
            content_type=getattr(file_field, "content_type", None),
        )

    @staticmethod
    def from_image_name(image_name: str) -> FileField:
        """Create a FileField from an image name/path in default storage.

        Args:
            image_name: The image path/name (e.g., "images/bc42bb4f-a43e-4f62-a861-3fa0d3dccffb.png")

        Returns:
            FileField: A FileField object with file information from default storage
        """
        if not image_name or not default_storage.exists(image_name):
            return FileField(
                file_type=FileType.NONE,
                path="",
                url=None,
                name=None,
                size=None,
                width=None,
                height=None,
                content_type=None,
            )

        # Get absolute path from default storage
        absolute_path = default_storage.path(image_name)

        # Get relative path from MEDIA_ROOT (like Django ImageField.name)
        media_root = os.path.normpath(settings.MEDIA_ROOT)
        relative_name = os.path.relpath(absolute_path, media_root)
        # Normalize path separators to forward slashes (like Django does)
        relative_name = relative_name.replace(os.sep, "/")

        # Get file information from default storage
        file_size = default_storage.size(image_name)
        file_url = default_storage.url(image_name)

        # Determine content type from file extension
        content_type, _ = mimetypes.guess_type(image_name)

        # Check if it's an image based on extension
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
        file_ext = os.path.splitext(image_name)[1].lower()
        is_image = file_ext in image_extensions

        # Get image dimensions if it's an image
        width = None
        height = None

        if is_image:
            try:
                with default_storage.open(image_name, "rb") as f:
                    with Image.open(f) as img:
                        width, height = img.size
            except Exception:
                # If we can't open as image, treat as regular file
                is_image = False

        return FileField(
            file_type=FileType.IMAGE if is_image else FileType.FILE,
            path=absolute_path,
            url=file_url,
            name=relative_name,
            size=file_size,
            width=width,
            height=height,
            content_type=content_type,
        )

    @staticmethod
    def from_file_name(file_name: str) -> FileField:
        """Create a FileField from a file name/path in default storage.

        Args:
            file_name: The file path/name (e.g., "attachments/bc42bb4f-a43e-4f62-a861-3fa0d3dccffb.pdf")

        Returns:
            FileField: A FileField object with file information from default storage
        """
        if not file_name or not default_storage.exists(file_name):
            return FileField(
                file_type=FileType.NONE,
                path="",
                url=None,
                name=None,
                size=None,
                width=None,
                height=None,
                content_type=None,
            )

        # Get absolute path from default storage
        absolute_path = default_storage.path(file_name)

        # Get relative path from MEDIA_ROOT (like Django FileField.name)
        media_root = os.path.normpath(settings.MEDIA_ROOT)
        relative_name = os.path.relpath(absolute_path, media_root)
        # Normalize path separators to forward slashes (like Django does)
        relative_name = relative_name.replace(os.sep, "/")

        # Get file information from default storage
        file_size = default_storage.size(file_name)
        file_url = default_storage.url(file_name)

        # Determine content type from file extension
        content_type, _ = mimetypes.guess_type(file_name)

        return FileField(
            file_type=FileType.FILE,
            path=absolute_path,
            url=file_url,
            name=relative_name,
            size=file_size,
            width=None,
            height=None,
            content_type=content_type,
        )