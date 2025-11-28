"""
Base views for core infrastructure.
"""

import logging
from dataclasses import asdict
from typing import Any, Dict

from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.core.cache import cache
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.response import Response

from core.application.queries import *
from core.infrastructure.forms import TestWidgetsForm
from identity.application.queries.user_queries import SearchUsersQuery
from shared.application.cqrs import dispatch_query_async
from shared.application.dtos import PaginatedResultDTO
from shared.infrastructure import views

logger = logging.getLogger(__name__)


class HomeView(views.AdminGenericMixin, views.FormView):
    form_class = TestWidgetsForm
    page_title = _("Dashboard")
    template_name = "core/base/home.html"
    success_url = reverse_lazy("core:base:home")
    permission_required = ["core_infrastructure.view_admin_dashboard"]

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["items_count"] = 2
        return ctx

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["id"] = self.request.user.id
        return initial

    def form_valid(self, form: TestWidgetsForm) -> HttpResponse:
        print(form.get_form_data())
        return super().form_valid(form)


class TestView(views.AdminGenericMixin, views.TemplateView):
    template_name = "core/base/test.html"


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=300)
    first_name = serializers.CharField(max_length=300)
    last_name = serializers.CharField(max_length=300)
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()


class SampleApiView(APIView):
    async def get(self, request: AsyncRequest) -> Response:
        res: PaginatedResultDTO = await dispatch_query_async(
            SearchUsersQuery(page=1, page_size=100, paginated=True)
        )
        # users = [asdict(u) for u in res.items]
        serializer = UserSerializer(res.items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# class HomeView(CQRSPaginatedViewMixin, AdminGenericMixin, TemplateView):
#     """Admin dashboard home view"""

#     template_name = "core/base/home.html"
#     permission_required = []

#     def get_paginated_query(self) -> SearchUsersQuery:
#         return SearchUsersQuery(
#             page=int(self.request.GET.get("page", 1)),
#             page_size=int(self.request.GET.get("page_size", 10)),
#             full_name=self.request.GET.get("full_name", ""),
#             email=self.request.GET.get("email", ""),
#             username=self.request.GET.get("username", ""),
#         )

#     def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
#         base_context = super().get_context_data(**kwargs)
#         form = TestWidgetsForm(initial={"text_input": "value"})
#         data = form.get_form_data()

#         if form.is_valid():
#             form.add_error(None, "this is error")

#         base_context.update(form=form)
#         return base_context
