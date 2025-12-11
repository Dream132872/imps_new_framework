"""
Attachment Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.dtos import AttachmentDTO
from media.application.mappers import AttachmentDTOMapper
from media.application.queries import (
    GetAttachmentByIdQuery,
    SearchAttachmentsQuery,
    SearchFirstAttachmentQuery,
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


class SearchAttachmentsQueryHandler(
    QueryHandler[SearchAttachmentsQuery, list[AttachmentDTO]],
    BaseAttachmentQueryHandler,
):
    """Searches between all attachments based on query inputs."""

    def handle(self, query: SearchAttachmentsQuery) -> list[AttachmentDTO]:
        attachments = self.uow[AttachmentRepository].search_attachments(
            content_type=query.content_type_id,
            object_id=query.object_id,
            attachment_type=query.attachment_type,
        )

        return AttachmentDTOMapper.list_to_dto(attachments)


class SearchFirstAttachmentQueryHandler(
    QueryHandler[SearchFirstAttachmentQuery, AttachmentDTO | None],
    BaseAttachmentQueryHandler,
):
    """Finds the first attachment based on query inputs."""

    def handle(self, query: SearchFirstAttachmentQuery) -> AttachmentDTO | None:
        attachment = self.uow[AttachmentRepository].search_first_attachment(
            content_type=query.content_type_id,
            object_id=query.object_id,
            attachment_type=query.attachment_type,
        )

        return AttachmentDTOMapper.to_dto(attachment) if attachment else None


class GetAttachmentByIdQueryHandler(
    QueryHandler[GetAttachmentByIdQuery, AttachmentDTO],
    BaseAttachmentQueryHandler,
):
    def handle(self, query: GetAttachmentByIdQuery) -> AttachmentDTO:
        try:
            attachment = self.uow[AttachmentRepository].get_by_id(
                str(query.attachment_id)
            )

            return AttachmentDTOMapper.to_dto(attachment)
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
