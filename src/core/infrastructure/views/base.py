import logging
from typing import Any

from django.http.response import HttpResponse as HttpResponse

from core.application.queries import *
from core.application.queries.user_queries import SearchUsersQuery
from shared.infrastructure.views import TemplateView
from shared.infrastructure.views.mixins import *
from core.infrastructure.forms import TestWidgetsForm

logger = logging.getLogger(__name__)


class HomeView(CQRSPaginatedViewMixin, AdminGenericMixin, TemplateView):
    """Admin dashboard home view"""

    template_name = "core/admin/home.html"
    permission_required = []

    def get_paginated_query(self) -> SearchUsersQuery:
        return SearchUsersQuery(
            page=int(self.request.GET.get("page", 1)),
            page_size=int(self.request.GET.get("page_size", 10)),
            full_name=self.request.GET.get("full_name", ""),
            email=self.request.GET.get("email", ""),
            username=self.request.GET.get("username", ""),
        )

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        base_context = super().get_context_data(**kwargs)
        form = TestWidgetsForm()

        if form.is_valid():
            form.add_error("text_input", "this is error")

        base_context.update(form=form)
        return base_context
