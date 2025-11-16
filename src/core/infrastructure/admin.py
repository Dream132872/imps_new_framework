"""
Core model admins.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaesUserAdmin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.admin import BaseModelAdmin

from .models import User
from media.infrastructure.models import Picture


class ManagePictureInline(GenericStackedInline):
    model = Picture
    extra = 0
    fields = ("image", "picture_type", "title", "alternative")
    verbose_name = _("Picture")
    verbose_name_plural = _("Pictures")


@admin.register(User)
class UserAdmin(BaseModelAdmin, BaesUserAdmin):
    inlines = [ManagePictureInline]
