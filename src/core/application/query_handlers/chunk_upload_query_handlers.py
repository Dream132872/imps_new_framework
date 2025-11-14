"""
Chunk Upload Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging
from typing import Any

from django.utils.translation import gettext_lazy as _
from injector import inject

from core.application.queries import chunk_upload_queries
from core.domain.repositories import ChunkUploadRepository
from shared.application.cqrs import QueryHandler
from shared.application.exceptions import ApplicationError
from shared.domain.repositories import UnitOfWork

__all__ = ("GetChunkUploadStatusQueryHandler",)

logger = logging.getLogger(__file__)


class BaseChunkUploadQueryHandler:
    """Base class for chunk upload query handlers with common functionalities"""

    @inject
    def __init__(
        self, uow: UnitOfWork
    ) -> None:
        self.uow = uow


class GetChunkUploadStatusQueryHandler(
    QueryHandler[chunk_upload_queries.GetChunkUploadStatusQuery, dict[str, Any]],
    BaseChunkUploadQueryHandler,
):
    def handle(
        self, query: chunk_upload_queries.GetChunkUploadStatusQuery
    ) -> dict[str, Any]:
        try:
            chunk_upload = self.uow[ChunkUploadRepository].get_by_upload_id(query.upload_id)
            if not chunk_upload:
                raise ApplicationError(_("Chunk upload not found"))

            return {
                "upload_id": chunk_upload.upload_id,
                "filename": chunk_upload.filename,
                "total_size": chunk_upload.total_size,
                "uploaded_size": chunk_upload.uploaded_size,
                "chunk_count": chunk_upload.chunk_count,
                "status": chunk_upload.status,
                "progress": chunk_upload.get_progress_percent(),
                "completed": chunk_upload.is_complete(),
            }
        except Exception as e:
            raise ApplicationError(
                _("Could not get chunk upload status: {message}").format(message=str(e))
            ) from e


