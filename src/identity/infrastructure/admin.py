"""
Identity model admins.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaesUserAdmin
from django.utils.translation import gettext_lazy as _

from media.infrastructure.admin import ManagePictureInline
from media.infrastructure.models import Picture
from shared.infrastructure.admin import BaseModelAdmin

from .models import User



@admin.register(User)
class UserAdmin(BaseModelAdmin, BaesUserAdmin):
    inlines = [ManagePictureInline]
