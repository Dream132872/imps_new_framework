"""
Chunk upload views for handling chunked file uploads.
"""

import logging
from dataclasses import asdict

from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _

from core.application.commands import chunk_upload_commands
from core.application.queries import chunk_upload_queries
from shared.application.cqrs import dispatch_command, dispatch_query
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreateChunkUploadView(views.AdminGenericMixin, views.View):
    """View to create a new chunked upload session."""

    permission_required = ["picture_infrastructure.add_picture"]
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
    """View to upload a chunk of the file."""

    permission_required = ["picture_infrastructure.add_picture"]
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


class CompleteChunkUploadView(views.AdminGenericMixin, views.View):
    """View to complete the chunked upload and create/update picture."""

    permission_required = [
        "picture_infrastructure.add_picture",
        "picture_infrastructure.change_picture",
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

        picture = dispatch_command(
            chunk_upload_commands.CompleteChunkUploadCommand(
                upload_id=upload_id,
                content_type_id=int(content_type_id),
                object_id=object_id,
                picture_type=picture_type,
                title=title,
                alternative=alternative,
                picture_id=picture_id if picture_id else None,
            )
        )

        return JsonResponse(
            {
                "status": "success",
                "message": _("Picture has been created successfully"),
                "details": {
                    "picture": asdict(picture),
                    "is_update": bool(picture_id),
                },
            }
        )


class GetChunkUploadStatusView(views.AdminGenericMixin, views.View):
    """View to get the status of a chunked upload."""

    permission_required = ["picture_infrastructure.add_picture"]
    return_exc_response_as_json = True

    def get(self, request: HttpRequest, upload_id: str) -> JsonResponse:
        result = dispatch_query(
            chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        )
        return JsonResponse(result)
