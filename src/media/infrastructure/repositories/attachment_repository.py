"""
Django repository implementation for attachment.
"""

from media.domain.entities import Attachment
from media.domain.repositories import AttachmentRepository
from media.infrastructure.models import Attachment as AttachmentModel
from shared.domain.factories import FileFieldFactory
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoAttachmentRepository",)


class DjangoAttachmentRepository(DjangoRepository[Attachment], AttachmentRepository):
    """
    Django implementation of attachment repository.
    """

    def __init__(self) -> None:
        super().__init__(AttachmentModel, Attachment)

    def _model_to_entity(self, model: AttachmentModel) -> Attachment:
        file = FileFieldFactory.from_file_field(model.file)
        return Attachment(
            id=str(model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            file=file,
            title=model.title,
            content_type_id=model.content_type_id,
            object_id=model.object_id,  # type: ignore
        )

    def _entity_to_model(self, entity: Attachment) -> AttachmentModel:
        model, created = AttachmentModel.objects.get_or_create(
            id=entity.id,
            defaults={
                "file": entity.file.name,
                "title": entity.title,
                "content_type_id": entity.content_type,
                "object_id": entity.object_id,
            },
        )

        # If the model already existed, update its fields
        if not created:
            model.file = entity.file.name  # type: ignore
            model.title = entity.title
            model.content_type_id = entity.content_type
            model.object_id = entity.object_id if entity.object_id else None  # type: ignore

        return model

    def search_attachments(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
    ) -> list[Attachment]:
        attachments = self.model_class.objects.all()

        if content_type and content_type is not None:
            attachments = attachments.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            attachments = attachments.filter(object_id=object_id)

        return [
            self._model_to_entity(a)
            for a in list(attachments.order_by("display_order", "created_at"))
        ]

    def search_first_attachment(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
    ) -> Attachment | None:
        attachments = self.model_class.objects.all()

        if content_type and content_type is not None:
            attachments = attachments.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            attachments = attachments.filter(object_id=object_id)

        first_attachment = attachments.order_by("display_order", "created_at").first()
        return self._model_to_entity(first_attachment) if first_attachment else None

