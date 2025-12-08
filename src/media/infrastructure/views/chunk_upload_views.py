"""
Chunk upload views for handling chunked file uploads.
"""

import logging
import uuid
from dataclasses import asdict

from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _

from media.application import commands as chunk_upload_commands
from media.application import queries as chunk_upload_queries
from media.application.commands import (
    CreateAttachmentCommand,
    CreatePictureCommand,
    UpdateAttachmentCommand,
    UpdatePictureCommand,
)
from shared.application.cqrs import dispatch_command, dispatch_query
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreateChunkUploadView(views.AdminGenericMixin, views.View):
    permission_required = [
        "media_infrastructure.add_picture",
        "media_infrastructure.add_attachment",
    ]
    return_exc_response_as_json = True

    def post(self, request: HttpRequest) -> JsonResponse:
        filename = request.POST.get("filename")
        total_size = request.POST.get("total_size")

        if not filename or not total_size:
            return JsonResponse(
                {"error": _("Filename and total_size are required")}, status=400
            )

        result = dispatch_command(
            chunk_upload_commands.CreateChunkUploadCommand(
                filename=filename,
                total_size=int(total_size),
            )
        )
        return JsonResponse(result)


class UploadChunkView(views.AdminGenericMixin, views.View):
    permission_required = [
        "media_infrastructure.add_picture",
        "media_infrastructure.add_attachment",
    ]
    return_exc_response_as_json = True

    def post(self, request: HttpRequest) -> JsonResponse:
        upload_id = request.POST.get("upload_id")
        offset = request.POST.get("offset")
        chunk = request.FILES.get("chunk")

        if not upload_id or not chunk or offset is None:
            return JsonResponse(
                {"error": _("upload_id, chunk, and offset are required")}, status=400
            )

        result = dispatch_command(
            chunk_upload_commands.UploadChunkCommand(
                upload_id=upload_id,
                chunk=chunk,
                offset=int(offset),
                chunk_size=chunk.size,
            )
        )
        return JsonResponse(result)


class GetChunkUploadStatusView(views.AdminGenericMixin, views.View):
    permission_required = ["media_infrastructure.add_picture"]
    return_exc_response_as_json = True

    def get(self, request: HttpRequest, upload_id: str) -> JsonResponse:
        result = dispatch_query(
            chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        )
        return JsonResponse(result)


class CompletePictureChunkUploadView(views.AdminGenericMixin, views.View):
    permission_required = [
        "media_infrastructure.add_picture",
        "media_infrastructure.change_picture",
    ]
    return_exc_response_as_json = True

    def post(self, request: HttpRequest) -> JsonResponse:
        upload_id = request.POST.get("upload_id")
        content_type_id = request.POST.get("content_type_id")
        object_id = request.POST.get("object_id")
        picture_type = request.POST.get("picture_type")
        title = request.POST.get("title", "")
        alternative = request.POST.get("alternative", "")
        picture_id = request.POST.get("picture_id")

        if not upload_id or not content_type_id or not object_id or not picture_type:
            return JsonResponse({"error": _("Missing required fields")}, status=400)

        completed_file = dispatch_command(
            chunk_upload_commands.CompleteChunkUploadCommand(
                upload_id=upload_id,
            )
        )

        if picture_id:
            # Update existing picture
            picture = dispatch_command(
                UpdatePictureCommand(
                    picture_id=uuid.UUID(picture_id),
                    content_type_id=int(content_type_id),
                    object_id=uuid.UUID(object_id),
                    picture_type=picture_type,
                    image=completed_file,
                    title=title,
                    alternative=alternative,
                )
            )
            is_update = True
        else:
            # Create new picture
            picture = dispatch_command(
                CreatePictureCommand(
                    content_type_id=int(content_type_id),
                    object_id=uuid.UUID(object_id),
                    picture_type=picture_type,
                    image=completed_file,
                    title=title,
                    alternative=alternative,
                )
            )
            is_update = False

        return JsonResponse(
            {
                "status": "success",
                "message": (
                    _("Picture has been created successfully")
                    if not is_update
                    else _("Picture has been updated successfully")
                ),
                "details": {
                    "picture": asdict(picture),
                    "is_update": is_update,
                },
            }
        )


class CompleteAttachmentChunkUploadView(views.AdminGenericMixin, views.View):
    permission_required = [
        "media_infrastructure.add_attachment",
        "media_infrastructure.change_attachment",
    ]
    return_exc_response_as_json = True

    def post(self, request: HttpRequest) -> JsonResponse:
        upload_id = request.POST.get("upload_id")
        content_type_id = request.POST.get("content_type_id")
        object_id = request.POST.get("object_id")
        attachment_type = request.POST.get("attachment_type", "")
        title = request.POST.get("title", "")
        attachment_id = request.POST.get("attachment_id")

        if not upload_id or not content_type_id or not object_id:
            return JsonResponse({"error": _("Missing required fields")}, status=400)

        completed_file = dispatch_command(
            chunk_upload_commands.CompleteChunkUploadCommand(
                upload_id=upload_id,
            )
        )

        if attachment_id:
            # Update existing attachment
            attachment = dispatch_command(
                UpdateAttachmentCommand(
                    attachment_id=uuid.UUID(attachment_id),
                    content_type_id=int(content_type_id),
                    object_id=uuid.UUID(object_id),
                    attachment_type=attachment_type,
                    file=completed_file,
                    title=title,
                )
            )
            is_update = True
        else:
            # Create new attachment
            attachment = dispatch_command(
                CreateAttachmentCommand(
                    content_type_id=int(content_type_id),
                    object_id=uuid.UUID(object_id),
                    attachment_type=attachment_type,
                    file=completed_file,
                    title=title,
                )
            )
            is_update = False

        return JsonResponse(
            {
                "status": "success",
                "message": (
                    _("Attachment has been created successfully")
                    if not is_update
                    else _("Attachment has been updated successfully")
                ),
                "details": {
                    "attachment": asdict(attachment),
                    "is_update": is_update,
                },
            }
        )
