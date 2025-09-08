import logging
from typing import Any, Dict, Hashable

from adrf.requests import AsyncRequest
from adrf.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.infrastructure.ioc import UserServiceBase
from core.infrastructure.models import Todo
from shared.infrastructure.ioc import inject_dependencies
from shared.infrastructure.repositories import DjangoUnitOfWork
from shared.infrastructure.views import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/admin/home.html"


class TodosApiView(APIView):
    @inject_dependencies()
    def __init__(
        self, user_service: UserServiceBase, **kwargs: Dict[Hashable, Any]
    ) -> None:
        self.user_service = user_service
        super().__init__(**kwargs)

    async def get(self, request: AsyncRequest) -> Response:
        res = []
        async with DjangoUnitOfWork():
            res = [
                {"title": t.title, "path": request.path}
                async for t in Todo.objects.all()
            ]

        return Response(res, status=status.HTTP_200_OK)
