"""Attachment mapper"""

from media.domain.entities import Attachment as AttachmentEntity
from media.infrastructure.models import Attachment as AttachmentModel
from shared.domain.factories import FileFieldFactory


class AttachmentMapper:
    """Attachment entity mapper"""

    @staticmethod
    def entity_to_model(entity: AttachmentEntity) -> AttachmentModel:
        """Converts attachment entity to model instance"""

        return AttachmentModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            file=entity.file.name,
            title=entity.title,
            attachment_type=entity.attachment_type,
            content_type_id=entity.content_type_id,
            object_id=entity.object_id,
        )

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
            object_id=model.object_id,
        )
