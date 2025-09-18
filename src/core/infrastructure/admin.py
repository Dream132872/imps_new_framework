from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaesUserAdmin
from shared.infrastructure.admin import BaseModelAdmin
from .models import *


@admin.register(User)
class UserAdmin(BaseModelAdmin, BaesUserAdmin):
    pass


@admin.register(Picture)
class PictureAdmin(BaseModelAdmin):
    pass
