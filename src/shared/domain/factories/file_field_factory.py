"""
File field factory for Image and File.
"""

from typing import Any

from shared.domain.entities import FileField, FileType

__all__ = ("FileFieldFactory",)


class FileFieldFactory:
    @staticmethod
    def from_image_field(image_field: Any) -> FileField:
        if not image_field:
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
