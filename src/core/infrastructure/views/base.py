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

    @inject_dependencies()
    def __init__(self, uow: UnitOfWork, **kwargs: dict[str, Any]) -> None:
        self.uow: UnitOfWork = uow
        super().__init__(**kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        with self.uow:
            user = self.uow[UserRepository].get_by_id(
                "2b8b8212-ef3f-4eb5-9893-c29675297087"
            )
            if user:
                return JsonResponse(user.to_dict())
        return super().get(request, *args, **kwargs)


class UsersApiView(APIView):
    @inject_dependencies()
    def __init__(self, uow: UnitOfWork, **kwargs: dict[str, Any]) -> None:
        self.uow = uow
        super().__init__(**kwargs)

    async def get(self, request: AsyncRequest):
        try:
            async with self.uow:
                users = await self.uow[UserRepository].get_all_async()
                return Response([u.to_dict() for u in users], status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
