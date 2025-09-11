import logging
import uuid
from typing import Any

from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from rest_framework import status
from rest_framework.response import Response

from core.application.queries import GetUserByIdQuery
from core.domain.entities.user import User
from shared.application.cqrs import dispatch_query_async
from shared.infrastructure.views import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/admin/home.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


class UsersApiView(APIView):
    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)

    async def get(self, request: AsyncRequest):
        query = GetUserByIdQuery(uuid.UUID("2b8b8212-ef3f-4eb5-9893-c29675297087"))
        res: User = await dispatch_query_async(query)
        return Response(res.to_dict(), status=status.HTTP_200_OK)
