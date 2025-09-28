import logging
from dataclasses import asdict
from typing import Any

from adrf.mixins import sync_to_async
from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from core.application.queries import *
from core.application.queries.user_queries import SearchUsersQuery
from core.domain.repositories import UserRepository
from core.infrastructure.forms import TestWidgetsForm
from shared.application.cqrs import dispatch_query_async
from shared.application.dtos import PaginatedResultDTO
from shared.infrastructure.views import *

logger = logging.getLogger(__name__)


class HomeView(AdminGenericMixin, FormView):
    page_title = _("Home view")
    permission_required = []
    form_class = TestWidgetsForm
    template_name = "core/admin/home.html"
    success_url = reverse_lazy("core:index_view")

    def form_valid(self, form: TestWidgetsForm):
        data = form.get_form_data()
        print(data["split_datetime_input"])
        return super().form_valid(form)


# class HomeView(AdminGenericMixin, View):
#     permission_required = []
#     page_title = _("Dashboard")

#     def get(self, request: HttpRequest) -> HttpResponse:
#         context = {"form": TestWidgetsForm()}
#         return render(request, "core/admin/home.html", context)

#     def post(self, request: HttpRequest) -> HttpResponse:
#         form = TestWidgetsForm(request.POST)
#         if form.is_valid():
#             form.add_error("char_field", "این مورد قبلا ثبت شده")
#             form.add_error("char_field", "شما نمیتونین مجددا یک آیتم جدید ثبت کنین")
#             form.add_error(None, "شما نمیتونین مجددا یک آیتم جدید ثبت کنین")
#             form.add_error(None, "شما نمیتونین مجددا یک آیتم جدید ثبت کنین")

#         context = {"form": form}
#         return render(request, "core/admin/home.html", context)


# class HomeView(CQRSPaginatedViewMixin, AdminGenericMixin, TemplateView):
#     """Admin dashboard home view"""

#     template_name = "core/admin/home.html"
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


class SampleApiView(APIView):
    @inject_dependencies()
    def __init__(self, uow: UnitOfWork, **kwargs: Any) -> None:
        self.uow = uow
        super().__init__(**kwargs)

    @sync_to_async()
    def get_users(self):
        with self.uow:
            users = self.uow[UserRepository].search_users(page_size=10, page=1)
            return [u.to_dict() for u in users.items]

    async def get(self, request: AsyncRequest):
        res: PaginatedResultDTO = await dispatch_query_async(
            SearchUsersQuery(page=1, page_size=10, paginated=True)
        )
        return Response([asdict(u) for u in res.items], status=status.HTTP_200_OK)
