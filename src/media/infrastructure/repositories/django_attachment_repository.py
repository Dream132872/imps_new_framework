"""
Django repository implementation for attachment.
"""

from django.utils.translation import gettext_lazy as _

from media.domain.entities import Attachment
from media.domain.exceptions import AttachmentNotFoundError
from media.domain.repositories import AttachmentRepository
from media.infrastructure.mappers import AttachmentMapper
from media.infrastructure.models import Attachment as AttachmentModel
from shared.domain.exceptions import DomainEntityNotFoundError
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoAttachmentRepository",)


class DjangoAttachmentRepository(DjangoRepository[Attachment], AttachmentRepository):
    """
    Django implementation of attachment repository.
    """

    def __init__(self) -> None:
        super().__init__(AttachmentModel, Attachment)

    def _model_to_entity(self, model: AttachmentModel) -> Attachment:
        return AttachmentMapper.model_to_entity(model)

    def _entity_to_model(self, entity: Attachment) -> AttachmentModel:
        return AttachmentMapper.entity_to_model(entity)

    def get_by_id(self, id: str) -> Attachment:
        try:
            return super().get_by_id(id)
        except DomainEntityNotFoundError as e:
            raise AttachmentNotFoundError(
                _("There is no attachment with ID: {attachment_id}").format(
                    attachment_id=id
                )
            ) from e

    def search_attachments(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
        attachment_type: str = "",
    ) -> list[Attachment]:
        attachments = self.model_class.objects.select_related("content_type").all()

        if content_type and content_type is not None:
            attachments = attachments.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            attachments = attachments.filter(object_id=object_id)

        if attachment_type and attachment_type is not None:
            attachments = attachments.filter(attachment_type__iexact=attachment_type)

        return [
            self._model_to_entity(a)
            for a in list(attachments.order_by("display_order", "created_at"))
        ]

    def search_first_attachment(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
        attachment_type: str = "",
    ) -> Attachment | None:
        attachments = self.model_class.objects.select_related("content_type").all()

        if content_type and content_type is not None:
            attachments = attachments.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            attachments = attachments.filter(object_id=object_id)

        if attachment_type and attachment_type is not None:
            attachments = attachments.filter(attachment_type__iexact=attachment_type)

        first_attachment = attachments.order_by("display_order", "created_at").first()
        return self._model_to_entity(first_attachment) if first_attachment else None
