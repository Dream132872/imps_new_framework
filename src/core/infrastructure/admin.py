from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaesUserAdmin
from parsley.mixins import ParsleyAdminMixin

from shared.infrastructure.admin import BaseModelAdmin

from .models import *


@admin.register(User)
class UserAdmin(ParsleyAdminMixin, BaseModelAdmin, BaesUserAdmin):
    pass


@admin.register(Picture)
class PictureAdmin(ParsleyAdminMixin, BaseModelAdmin):
    pass
