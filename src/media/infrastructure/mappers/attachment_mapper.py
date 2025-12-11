"""Attachment mapper"""

from media.domain.entities import Attachment as AttachmentEntity
from media.infrastructure.models import Attachment as AttachmentModel
from shared.domain.factories import FileFieldFactory


class AttachmentMapper:
    """Attachment entity mapper"""

    @staticmethod
    def entity_to_model(entity: AttachmentEntity) -> AttachmentModel:
        """Converts attachment entity to model instance"""

        model, created = AttachmentModel.objects.get_or_create(
            id=entity.id,
            defaults={
                "file": entity.file.name,
                "title": entity.title,
                "attachment_type": entity.attachment_type,
                "content_type_id": entity.content_type_id,
                "object_id": entity.object_id,
            },
        )

        # If the model already existed, update its fields
        if not created:
            model.file = entity.file.name  # type: ignore
            model.title = entity.title
            model.attachment_type = entity.attachment_type
            model.content_type_id = entity.content_type_id
            model.object_id = entity.object_id if entity.object_id else None  # type: ignore

        return model

    @staticmethod
    def model_to_entity(model: AttachmentModel) -> AttachmentEntity:
        """Converts attachment model to entity"""

        file = FileFieldFactory.from_file_field(model.file)
        return AttachmentEntity(
            id=str(model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            file=file,
            title=model.title,
            attachment_type=model.attachment_type,
            content_type_id=model.content_type_id,
            object_id=model.object_id
        )
