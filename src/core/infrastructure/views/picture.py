"""
Manage picture views.
"""

import logging
from dataclasses import asdict
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from core.application.commands import picture_commands
from core.application.dtos.picture_dtos import PictureDTO
from core.infrastructure.forms.picture import UpsertPictureForm
from shared.application.cqrs import dispatch_command
from shared.application.exceptions import ApplicationNotFoundError
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreatePictureView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertPictureForm
    template_name = "core/picture/picture_upsert.html"
    permission_required = ["core_infrastructure.add_picture"]
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
            picture_commands.CreatePictureCommand(
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
                "details": {"picture": asdict(picture)},
            }
        )


class UpdatePictureView(views.FormView):
    form_class = UpsertPictureForm
    template_name = "core/picture/picture_upsert.html"
    permission_required = ["core_infrastructure.change_picture"]

    def get_initial(self) -> dict[str, Any]:
        picture_id = self.kwargs.get("picture_id")
        # picture =
        return super().get_initial()

    def form_valid(self, form: UpsertPictureForm) -> JsonResponse:
        return JsonResponse({"status": "success"})

    def form_invalid(self, form: UpsertPictureForm) -> JsonResponse:
        return JsonResponse({"status": "error"})


class DeletePictureView(views.AdminGenericMixin, views.DeleteView):
    command_class = picture_commands.DeletePictureCommand
    permission_required = ["core_infrastructure.delete_picture"]
