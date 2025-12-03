"""
Attachment Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging
from typing import Any

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.dtos import AttachmentDTO
from media.application.queries import (
    GetAttachmentByIdQuery,
    SearchFirstAttachmentQuery,
    SearchAttachmentsQuery,
)
from media.domain.entities import Attachment
from media.domain.exceptions import AttachmentNotFoundError
from media.domain.repositories import AttachmentRepository
from shared.application.cqrs import QueryHandler
from shared.application.dtos import FileFieldDTO
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.repositories import UnitOfWork

logger = logging.getLogger(__file__)


class BaseAttachmentQueryHandler:
    """Base class for attachment query handlers with common functionalities"""

    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def _to_dto(self, attachment: Attachment) -> AttachmentDTO:
        file = FileFieldDTO(
            file_type="file",
            url=attachment.file.url,
            name=attachment.file.name,
            size=attachment.file.size,
            width=None,
            height=None,
            content_type=attachment.file.content_type,
        )
        return AttachmentDTO(
            id=attachment.id,
            file=file,
            title=attachment.title,
            content_type_id=attachment.content_type,
            object_id=attachment.object_id,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )


class SearchAttachmentsQueryHandler(
    QueryHandler[SearchAttachmentsQuery, list[AttachmentDTO]],
    BaseAttachmentQueryHandler,
):
    """Searches between all attachments based on query inputs."""

    def handle(self, query: SearchAttachmentsQuery) -> list[AttachmentDTO]:
        with self.uow:
            attachments = self.uow[AttachmentRepository].search_attachments(
                content_type=query.content_type_id,
                object_id=query.object_id,
            )

            return [self._to_dto(a) for a in attachments]


class SearchFirstAttachmentQueryHandler(
    QueryHandler[SearchFirstAttachmentQuery, AttachmentDTO | None],
    BaseAttachmentQueryHandler,
):
    """Finds the first attachment based on query inputs."""

    def handle(
        self, query: SearchFirstAttachmentQuery
    ) -> AttachmentDTO | None:
        with self.uow:
            attachment = self.uow[AttachmentRepository].search_first_attachment(
                content_type=query.content_type_id,
                object_id=query.object_id,
            )

            return self._to_dto(attachment) if attachment else None


class GetAttachmentByIdQueryHandler(
    QueryHandler[GetAttachmentByIdQuery, AttachmentDTO],
    BaseAttachmentQueryHandler,
):
    def handle(self, query: GetAttachmentByIdQuery) -> AttachmentDTO:
        try:
            with self.uow:
                attachment = self.uow[AttachmentRepository].get_by_id(str(query.attachment_id))
                if not attachment:
                    raise AttachmentNotFoundError(
                        _("There is no attachment with ID: {attachment_id}").format(
                            attachment_id=query.attachment_id
                        )
                    )

                return self._to_dto(attachment)
        except AttachmentNotFoundError as e:
            raise map_domain_exception_to_application(
                e, message=_("Attachment not found: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("Could not get attachment with ID: {attachment_id}").format(
                    attachment_id=query.attachment_id
                )
            ) from e

