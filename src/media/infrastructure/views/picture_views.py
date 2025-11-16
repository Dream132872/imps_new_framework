"""
Manage picture views.
"""

import logging
from dataclasses import asdict
from functools import lru_cache
from typing import Any

from django.forms.forms import BaseForm
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from media.application.dtos import PictureDTO
from media.application.queries import GetPictureByIdQuery
from media.infrastructure.forms import UpsertPictureForm
from shared.application.cqrs import dispatch_command, dispatch_query
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreatePictureView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertPictureForm
    template_name = "picture/picture_upsert.html"
    permission_required = ["media_infrastructure.add_picture"]
    return_exc_response_as_json = True

    def get_initial(self) -> dict[str, Any]:
        init = super().get_initial()
        init["content_type"] = self.kwargs["content_type"]
        init["object_id"] = self.kwargs["object_id"]
        init["picture_type"] = self.kwargs["picture_type"]
        return init

    def form_valid(self, form: UpsertPictureForm) -> JsonResponse:
        # get form data
        data = form.get_form_data()
        # get form files
        files = form.files
        # dispatch the requested command for creating picture entity
        picture: PictureDTO = dispatch_command(
            CreatePictureCommand(
                content_type_id=data["content_type"],
                object_id=data["object_id"],
                picture_type=data["picture_type"],
                image=files["image"],  # type: ignore
                title=data["title"],
                alternative=data["alternative"],
            )
        )
        return JsonResponse(
            {
                "status": "success",
                "message": _("Picture has been created successfully"),
                "details": {
                    "picture": asdict(picture),
                    "is_update": False,
                },
            }
        )


class UpdatePictureView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertPictureForm
    template_name = "picture/picture_upsert.html"
    permission_required = ["media_infrastructure.change_picture"]
    return_exc_response_as_json = True

    @lru_cache
    def get_picture_data(self) -> PictureDTO:
        return dispatch_query(
            GetPictureByIdQuery(
                picture_id=self.kwargs.get("picture_id")
            )
        )

    def get_initial(self) -> dict[str, Any]:
        init = super().get_initial()
        picture = self.get_picture_data()
        init["picture_id"] = picture.id
        init["content_type"] = picture.content_type
        init["object_id"] = picture.object_id
        init["picture_type"] = picture.picture_type
        init["title"] = picture.title
        init["alternative"] = picture.alternative
        return init

    def get_form(self, form_class: type | None = None) -> BaseForm:
        form = super().get_form(form_class)
        form.picture_data = self.get_picture_data()
        return form

    def form_valid(self, form: UpsertPictureForm) -> JsonResponse:
        # get form data
        data = form.get_form_data()
        # get form files
        files = form.files
        # dispatch the requested command for updating picture entity
        picture = dispatch_command(
            UpdatePictureCommand(
                picture_id=data["picture_id"],
                content_type_id=data["content_type"],
                alternative=data["alternative"],
                title=data["title"],
                image=files.get("image", None),  # type: ignore
                object_id=data["object_id"],
                picture_type=data["picture_type"],
            )
        )
        return JsonResponse(
            {
                "status": "success",
                "message": _("Picture has been updated successfully"),
                "details": {"picture": asdict(picture), "is_update": True},
            }
        )


class DeletePictureView(views.AdminGenericMixin, views.DeleteView):
    command_class = DeletePictureCommand
    permission_required = ["media_infrastructure.delete_picture"]

