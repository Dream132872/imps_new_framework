"""
Manage attachment views.
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
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.application.dtos import AttachmentDTO
from media.application.queries import GetAttachmentByIdQuery
from media.infrastructure.forms import UpsertAttachmentForm
from shared.application.cqrs import dispatch_command, dispatch_query
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreateAttachmentView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertAttachmentForm
    template_name = "attachment/attachment_upsert.html"
    permission_required = ["media_infrastructure.add_attachment"]
    return_exc_response_as_json = True

    def get_initial(self) -> dict[str, Any]:
        init = super().get_initial()
        init["content_type"] = self.kwargs["content_type"]
        init["object_id"] = self.kwargs["object_id"]
        return init

    def form_valid(self, form: UpsertAttachmentForm) -> JsonResponse:
        # get form data
        data = form.get_form_data()
        # get form files
        files = form.files
        # dispatch the requested command for creating attachment entity
        attachment: AttachmentDTO = dispatch_command(
            CreateAttachmentCommand(
                content_type_id=data["content_type"],
                object_id=data["object_id"],
                file=files["file"],  # type: ignore
                title=data["title"],
            )
        )
        return JsonResponse(
            {
                "status": "success",
                "message": _("Attachment has been created successfully"),
                "details": {
                    "attachment": asdict(attachment),
                    "is_update": False,
                },
            }
        )


class UpdateAttachmentView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertAttachmentForm
    template_name = "attachment/attachment_upsert.html"
    permission_required = ["media_infrastructure.change_attachment"]
    return_exc_response_as_json = True

    @lru_cache
    def get_attachment_data(self) -> AttachmentDTO:
        return dispatch_query(
            GetAttachmentByIdQuery(
                attachment_id=self.kwargs.get("attachment_id")
            )
        )

    def get_initial(self) -> dict[str, Any]:
        init = super().get_initial()
        attachment = self.get_attachment_data()
        init["attachment_id"] = attachment.id
        init["content_type"] = attachment.content_type_id
        init["object_id"] = attachment.object_id
        init["title"] = attachment.title
        return init

    def get_form(self, form_class: type | None = None) -> BaseForm:
        form = super().get_form(form_class)
        form.attachment_data = self.get_attachment_data()
        return form

    def form_valid(self, form: UpsertAttachmentForm) -> JsonResponse:
        # get form data
        data = form.get_form_data()
        # get form files
        files = form.files
        # dispatch the requested command for updating attachment entity
        attachment = dispatch_command(
            UpdateAttachmentCommand(
                attachment_id=data["attachment_id"],
                content_type_id=data["content_type"],
                title=data["title"],
                file=files.get("file", None),  # type: ignore
                object_id=data["object_id"],
            )
        )
        return JsonResponse(
            {
                "status": "success",
                "message": _("Attachment has been updated successfully"),
                "details": {"attachment": asdict(attachment), "is_update": True},
            }
        )


class DeleteAttachmentView(views.AdminGenericMixin, views.DeleteView):
    command_class = DeleteAttachmentCommand
    permission_required = ["media_infrastructure.delete_attachment"]

