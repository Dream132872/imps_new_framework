"""
All pictures will be saved in this model.
"""

import os
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from media.infrastructure.models.managers import PictureManager
from shared.infrastructure.models import BaseModel

__all__ = ("Picture",)


def image_upload_path(instance: "Picture", filepath: str) -> str:
    """This method generate new unique random image name for picture

    Args:
        instance (Picture): instance of an object of Picture model.
        filepath (str): path of file in memory.

    Returns:
        str: the address of image with unique random name.
    """
    name, ext = os.path.splitext(os.path.basename(filepath))
    return f"images/{uuid.uuid4()}{ext}"


class Picture(BaseModel):
    """Model definition for Picture."""

    class PictureType(models.TextChoices):
        MAIN = "main", _("Main image")
        GALLERY = "gallery", _("Gallery image")
        AVATAR = "avatar", _("Avatar")
        BANNER = "banner", _("Banner")

    # main image in db
    image = models.ImageField(
        max_length=200,
        upload_to=image_upload_path,  # type: ignore
        null=True,
        blank=True,
        verbose_name=_("Image"),  # type: ignore
        help_text=_("The main image"),
    )
    # alternative text
    alternative = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Alternative text"),
        help_text=_("Alternative text of the image when it's not loaded"),
    )

    # title of the image
    title = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Title"),
        help_text=_("Title of the image"),
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

    # Picture type/context - this is KEY for your use case
    picture_type = models.CharField(
        max_length=50,
        choices=PictureType.choices,
        default="main",
        verbose_name=_("Picture Type"),
        help_text=_("Type of the picture to manage"),
    )

    # Order for gallery images
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_("Display order of the image that manage it's priority"),
    )

    # default manager of Picture model
    objects = PictureManager()

    class Meta:
        """Meta definition for Picture."""

        db_table = "pictures"
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")
        ordering = ["display_order", "-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "picture_type"]),
            models.Index(fields=["picture_type"]),
        ]

    def __str__(self) -> str:
        """Unicode representation of Picture."""
        return f"{self.image} / {self.alternative}"

    def __repr__(self) -> str:
        """Debug representation of Picture."""
        return f"<Picture pk={self.id} name={self.image} type={self.picture_type}/>"

    def image_tag(self) -> str:
        """Image html tag that is used in admin"""
        return mark_safe(f'<img src="{self.image.url}" width="100" height="100" />')