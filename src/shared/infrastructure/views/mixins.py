"""
Shared django view mixins.
"""

from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest
from django.views.generic.base import ContextMixin

from shared.application.cqrs import dispatch_query
from shared.application.dtos import PaginatedResultDTO
from shared.infrastructure.views.exceptions import ApplicationExceptionHandlerMixin

__all__ = (
    "ViewTitleMixin",
    "AdminGenericMixin",
    "CQRSPaginatedViewMixin",
)


class ViewTitleMixin(ContextMixin):
    """
    This mixin adds title to the context.
    you can use it via set title attribute or call get_title method.
    """

    page_title = ""

    def get_title(self) -> str:
        return self.page_title

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_title() or self.page_title
        return context


class CQRSPaginatedViewMixin(ContextMixin):
    """
    Mixin for views that use CQRS queries with pagination.
    """

    def get_paginated_query(self) -> Any:
        """Create and return the paginated query."""

        raise NotImplementedError("Subclasses must implement get_paginated_query()")

    def get(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> Any:
        # Get the paginated query
        query = self.get_paginated_query()

        # Dispatch the query and get paginator
        page_obj: PaginatedResultDTO = dispatch_query(query)

        # Store the result for context
        self.page_obj = page_obj

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Add pagination data to context - Django's standard format
        if hasattr(self, "page_obj"):
            context.update({"page_obj": self.page_obj})

        return context


class PopupDetectionMixin(ContextMixin):
    """
    Mixin to detect if the current request is from a popup window.
    """

    def is_popup_request(self) -> bool:
        """Check if the current request is from a popup window."""
        return self.request.GET.get("popupId", "") != ""

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["is_popup"] = self.is_popup_request()
        context["popup_mode"] = self.is_popup_request()
        return context


class AdminGenericMixin(
    ViewTitleMixin,
    PopupDetectionMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    """
    This class contains basic mixins that every admin view should have like:
    PermissionRequiredMixin, ViewTitleMixin and LoginRequiredMixin.

    You should inherit from this class then django's generic views.
    for example:


    class TestView(AdminGenericMixin, TemplateView):
        pass
    """

    permission_required = []
