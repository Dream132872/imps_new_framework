"""
Media model admins.
"""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _

from media.infrastructure.models import Attachment, Picture
from shared.infrastructure.admin import BaseModelAdmin


class ManagePictureInline(GenericStackedInline):
    model = Picture
    extra = 0
    fields = ("image", "picture_type", "title", "alternative")
    verbose_name = _("Picture")
    verbose_name_plural = _("Pictures")


class ManageAttachmentInline(GenericStackedInline):
    model = Attachment
    extra = 0
    fields = ("file", "title", "display_order")
    verbose_name = _("Attachment")
    verbose_name_plural = _("Attachments")


@admin.register(Picture)
class PictureAdmin(BaseModelAdmin):
    list_display = (
        "image_tag",
        "picture_type",
        "related_object",
        "content_type",
        "object_id",
        "created_at",
    )
    list_filter = ("picture_type", "content_type")
    search_fields = ("title", "alternative")

    def related_object(self, obj):  # type: ignore
        return obj.content_object

    related_object.short_description = "Related object"  # type: ignore


@admin.register(Attachment)
class AttachmentAdmin(BaseModelAdmin):
    list_display = (
        "__str__",
        "related_object",
        "content_type",
        "object_id",
        "created_at",
    )
    list_filter = ("content_type",)
    search_fields = ("title",)

    def related_object(self, obj):  # type: ignore
        return obj.content_object

    related_object.short_description = "Related object"  # type: ignore
