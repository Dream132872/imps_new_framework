"""
Django admin configuration for shared infrastructure.
"""

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin class that provides common functionality for models inheriting from BaseModel.
    This can be used as a mixin or base class for other admin classes.
    """

    # Common readonly fields for BaseModel
    readonly_fields = ["id", "created_at", "updated_at"]

    # Common list filter
    list_filter = ["created_at", "updated_at"]

    # Common ordering
    ordering = ["-created_at"]

    # Common list per page
    list_per_page = 25

    def get_fieldsets(
        self, request: HttpRequest, obj: Any | None = None
    ) -> list[tuple[str | None, dict[str, Any]]]:
        """
        Add system information fields to fieldsets.
        Override this in subclasses to customize fieldsets.
        """
        fieldsets = super().get_fieldsets(request, obj)
        if fieldsets:
            # Add system information section if not already present
            system_fields = ("id", "created_at", "updated_at")
            has_system_section = any(
                "System Information" in fieldset[0]
                for fieldset in fieldsets
                if fieldset[0]
            )

            if not has_system_section:
                fieldsets = list(fieldsets)
                fieldsets.append(
                    (
                        "System Information",
                        {"fields": system_fields, "classes": ("collapse",)},
                    )
                )

        return fieldsets

    def get_readonly_fields(
        self, request: HttpRequest, obj: Any | None = None
    ) -> list[str]:
        """
        Ensure system fields are readonly.
        Override this in subclasses to add more readonly fields.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.extend(["id", "created_at", "updated_at"])
        return readonly_fields

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """
        Optimize queryset for common operations.
        Override this in subclasses for specific optimizations.
        """
        return super().get_queryset(request)

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        """
        Custom delete permission logic.
        Override this in subclasses for specific permission logic.
        """
        return super().has_delete_permission(request, obj)

    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        """
        Custom change permission logic.
        Override this in subclasses for specific permission logic.
        """
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Custom add permission logic.
        Override this in subclasses for specific permission logic.
        """
        return super().has_add_permission(request)

    def has_view_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        """
        Custom view permission logic.
        Override this in subclasses for specific permission logic.
        """
        return super().has_view_permission(request, obj)


# Note: BaseModel is abstract, so it's not registered with admin
# This admin class is meant to be inherited by other admin classes
# that work with models that inherit from BaseModel
