"""Attachment DTO mappers"""

import uuid

from media.application.dtos import AttachmentDTO
from media.domain.entities import Attachment as AttachmentEntity
from shared.application.mappers import FileFieldDTOMapper
from shared.domain.entities import FileFieldType


class AttachmentDTOMapper:
    """Attachment DTO mapper"""

    @staticmethod
    def to_dto(attachment: AttachmentEntity) -> AttachmentDTO:
        """Converts attachment entity instance to dto instance"""

        return AttachmentDTO(
            id=uuid.UUID(attachment.id),
            file=FileFieldDTOMapper.to_dto(attachment.file, FileFieldType.FILE),
            attachment_type=attachment.attachment_type,
            title=attachment.title,
            content_type_id=attachment.content_type_id,
            object_id=attachment.object_id,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )

    @staticmethod
    def list_to_dto(attachments: list[AttachmentEntity]) -> list[AttachmentDTO]:
        """Converts a list of attachment entities to dtos"""

        return [AttachmentDTOMapper.to_dto(attachment) for attachment in attachments]
