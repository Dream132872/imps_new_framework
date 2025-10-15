"""
Core model admins.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaesUserAdmin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.admin import BaseModelAdmin

from .models import *


class ManagePictureInline(GenericStackedInline):
    model = Picture
    extra = 0
    fields = ("image", "picture_type", "title", "alternative")
    verbose_name = _("Picture")
    verbose_name_plural = _("Pictures")


@admin.register(User)
class UserAdmin(BaseModelAdmin, BaesUserAdmin):
    inlines = [ManagePictureInline]


@admin.register(Picture)
class PictureAdmin(BaseModelAdmin):
    list_display = (
        "id",
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
