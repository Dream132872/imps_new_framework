from django.contrib import admin

from shared.infrastructure.admin import BaseModelAdmin

from .models import Todo

# Register your models here.


@admin.register(Todo)
class TodoAdmin(BaseModelAdmin):
    """Admin View for Todo"""

    list_display = (
        "pk",
        "title",
    )
