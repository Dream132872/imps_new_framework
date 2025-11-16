"""
Media model admins.
"""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.admin import BaseModelAdmin

from media.infrastructure.models import Picture


class ManagePictureInline(GenericStackedInline):
    model = Picture
    extra = 0
    fields = ("image", "picture_type", "title", "alternative")
    verbose_name = _("Picture")
    verbose_name_plural = _("Pictures")


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

