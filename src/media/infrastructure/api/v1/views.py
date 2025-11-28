"""
Media api views.
"""

from dataclasses import asdict
from typing import Any

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from ninja.decorators import decorate_view
from ninja_extra import ControllerBase, api_controller, permissions, route, status

from identity.application.queries.user_queries import SearchUsersQuery
from shared.application.cqrs import dispatch_query_async
from shared.application.dtos import PaginatedResultDTO
from . import schemas


class HasRole(permissions.BasePermission):
    def __init__(self, required_role: str):
        self.required_role = required_role

    def has_permission(self, request: HttpRequest, controller: ControllerBase):
        if controller.context:
            controller.context.compute_route_parameters()
            print(controller.context.args, controller.context.kwargs)

        return True


@api_controller(
    "media/pictures/",
    tags=["Picture"],
    urls_namespace="media",
)
class PictureController(ControllerBase):

    @route.get(
        "",
        response={200: dict[str, str]},
        url_name="images_list",
        permissions=[HasRole("articles.view")],
    )
    @decorate_view(cache_page(20))
    async def get_images(self):
        """Get list of all images."""

        return {"key": reverse("api_v1:media:images_list")}

    @route.post("create/", response={status.HTTP_200_OK: Any})
    async def create_picture(self, data: str):
        """Create new picture."""

        return {"picture_id": "123"}

    @route.get("users/", response={200: Any}, summary=_("Submit"))
    async def get_users(self):
        res: PaginatedResultDTO = await dispatch_query_async(
            SearchUsersQuery(page=1, page_size=1000, paginated=True)
        )
        # users = [asdict(u) for u in res.items]
        return res
