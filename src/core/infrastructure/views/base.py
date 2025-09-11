import logging
from typing import Any

from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from rest_framework import status
from rest_framework.response import Response

from core.domain.repositories import UserRepository
from shared.domain.repositories import UnitOfWork
from shared.infrastructure.ioc import inject_dependencies
from shared.infrastructure.views import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/admin/home.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


class UsersApiView(APIView):
    @inject_dependencies()
    def __init__(self, uow: UnitOfWork, **kwargs: dict[str, Any]) -> None:
        self.uow = uow
        super().__init__(**kwargs)

    async def get(self, request: AsyncRequest):
        return Response(None, status=status.HTTP_200_OK)
