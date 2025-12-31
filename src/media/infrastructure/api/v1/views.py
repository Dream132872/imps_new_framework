"""
Media api views.
"""

from typing import Any

from django.core.cache import cache
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ninja_extra import ControllerBase, api_controller, permissions, route, status

from identity.application.queries.user_queries import SearchUsersQuery
from shared.application.cqrs import dispatch_query_async
from shared.application.dtos import PaginatedResultDTO


class HasRole(permissions.BasePermission):
    def __init__(self, required_role: str):
        self.required_role = required_role

    def has_permission(self, request: HttpRequest, controller: ControllerBase):
        if controller.context:
            controller.context.compute_route_parameters()
            print(controller.context.args, controller.context.kwargs)

        return controller.context.request.user.is_authenticated


@api_controller(
    "media/pictures/",
    tags=["Picture"],
    urls_namespace="media",
)
class PictureController(ControllerBase):
    """Picutre related api endpoints."""

    @route.get("users/", response={200: PaginatedResultDTO}, summary=_("Submit"))
    async def get_users(self, page: int = 1, page_size: int = 20) -> PaginatedResultDTO:
        return await dispatch_query_async(
            SearchUsersQuery(page=page, page_size=page_size, paginated=True)
        )
        ## cached scenario
        # cached_data = await cache.aget("cached_users")
        # if not cached_data:
        #     res: PaginatedResultDTO = await dispatch_query_async(
        #         SearchUsersQuery(page=page, page_size=page_size, paginated=True)
        #     )
        #     await cache.aset("cached_users", res)
        #     return res
        # return cached_data
