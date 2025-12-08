import os
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.models import BaseModel

__all__ = ("Attachment",)


def attachment_upload_path(instance: "Attachment", filepath: str) -> str:
    """This method generate new unique random name for attachment file

    Args:
        instance (Attachment): instance of an object of Attachment model.
        filepath (str): path of file in memory.

    Returns:
        str: the address of attachment with unique random name.
    """
    name, ext = os.path.splitext(os.path.basename(filepath))
    return f"attachments/{uuid.uuid4()}{ext}"


class Attachment(BaseModel):
    # attachment file
    file = models.FileField(
        max_length=200,
        upload_to=attachment_upload_path,
        null=True,
        blank=True,
        verbose_name=_("File"),
        help_text=_("The main file"),
    )

    # title of the file
    title = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Title"),
        help_text=_("Title of the file"),
    )

    # Order for attachment files
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_("Display order of the file that manage it's priority"),
    )

    # content type for generic relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
        help_text=_("Django content type foreign key"),
    )

    # object id for generic relation
    object_id = models.CharField(
        verbose_name=_("Object id"),
        help_text=_("Object id of the related model"),
    )

    # content object
    content_object = GenericForeignKey("content_type", "object_id")

    # Attachment type/context
    attachment_type = models.CharField(
        max_length=50,
        default="",
        blank=True,
        verbose_name=_("Attachment Type"),
        help_text=_("Type of the attachment to manage"),
    )

    class Meta:
        db_table = "attachments"
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "attachment_type"]
            ),  # For generic relation lookups
            models.Index(
                fields=["attachment_type"]
            ),  # For attachment type lookups
            models.Index(
                fields=["display_order", "-created_at"]
            ),  # For ordering queries
        ]
        ordering = ["display_order", "-created_at"]

    def __str__(self) -> str:
        """Unicode representation of the attachment."""
        return f"{self.content_type} / {self.file.name}"

    def __repr__(self) -> str:
        """Debug representation of the attachment."""
        return f"<Attachment pk={self.id} name={self.file} type={self.attachment_type}/>"
