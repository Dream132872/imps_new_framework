from dataclasses import asdict
import logging
from typing import Any

from adrf.mixins import sync_to_async
from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.http.response import HttpResponse as HttpResponse
from rest_framework import status
from rest_framework.response import Response

from core.application.queries import *
from core.application.queries.user_queries import SearchUsersQuery
from core.domain.repositories import UserRepository
from core.infrastructure.forms import TestWidgetsForm
from shared.application.cqrs import dispatch_query_async
from shared.application.dtos import PaginatedResultDTO
from shared.domain.repositories import UnitOfWork
from shared.infrastructure.ioc import inject_dependencies
from shared.infrastructure.views import TemplateView
from shared.infrastructure.views.mixins import *

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

        # if form.is_valid():
        #     form.add_error("text_input", "this is error")

        base_context.update(form=form)
        return base_context


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
