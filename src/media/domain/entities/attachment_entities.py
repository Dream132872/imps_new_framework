"""
Attachment related domain implementations.
"""

from datetime import datetime
from typing import Any

from django.utils.translation import gettext_lazy as _

from media.domain.exceptions import AttachmentValidationError
from shared.domain.entities import AggregateRoot, FileField

__all__ = ("Attachment",)


class Attachment(AggregateRoot):
    def __init__(
        self,
        file: FileField,
        content_type_id: int,
        object_id: int | str,
        id: str | None = None,
        title: str | None = None,
        attachment_type: str = "",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id, created_at, updated_at)

        if not isinstance(file, FileField):
            raise AttachmentValidationError(
                _("File should be an instance of FileField")
            )

        if not file or file.size == 0:
            raise AttachmentValidationError(_("File cannot be None"))

        if not content_type_id or not object_id:
            raise AttachmentValidationError(
                _("Attachment should have relation information")
            )

        if not attachment_type or attachment_type == "":
            raise AttachmentValidationError(
                _("Attachment should have a type to identify it")
            )

        self._file = file
        self._title = title or ""
        self._attachment_type = attachment_type or ""
        self._content_type_id = content_type_id
        self._object_id = object_id

    @property
    def file(self) -> FileField:
        return self._file

    @property
    def title(self) -> str:
        return self._title

    @property
    def attachment_type(self) -> str:
        return self._attachment_type

    @property
    def content_type_id(self) -> int:
        return self._content_type_id

    @property
    def object_id(self) -> int | str:
        return self._object_id

    def update_file(self, new_file: FileField) -> None:
        """Update the file itself.

        Args:
            new_file (FileField): new file field.
        """

        if not isinstance(new_file, FileField):
            raise AttachmentValidationError(
                _("File should be an instance of FileField")
            )

        if not new_file or (new_file.size is not None and new_file.size == 0):
            raise AttachmentValidationError(_("File cannot be None"))

        self._file = new_file
        self.update_timestamp()

    def update_information(
        self, title: str | None = None, attachment_type: str | None = None
    ) -> None:
        """Update attachment information.

        Args:
            title (str | None, optional): title of the file. Defaults to None.
            attachment_type (str | None, optional): type of the attachment. Defaults to None.
        """
        if title is not None:
            self._title = title
        if attachment_type is not None:
            self._attachment_type = attachment_type

        self.update_timestamp()

    def __str__(self) -> str:
        return self.file.name

    def __repr__(self) -> str:
        return f"<AttachmentEntity id={self.id} file={self.file.name} />"

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "file": self.file.to_dict(),
                "title": self.title,
                "attachment_type": self.attachment_type,
            }
        )
        return base_dict
