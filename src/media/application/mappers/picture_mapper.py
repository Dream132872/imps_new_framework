"""Picture DTO mappers"""

import uuid

from media.application.dtos import PictureDTO
from media.domain.entities import Picture as PictureEntity
from shared.application.mappers import FileFieldDTOMapper
from shared.domain.entities import FileFieldType


class PictureDTOMapper:
    """Picture DTO mapper class"""

    @staticmethod
    def to_dto(picture: PictureEntity) -> PictureDTO:
        """Converts picture entity instance to picture dto instance"""

        return PictureDTO(
            id=uuid.UUID(picture.id),
            image=FileFieldDTOMapper.to_dto(picture.image, FileFieldType.IMAGE),
            picture_type=picture.picture_type,
            title=picture.title,
            alternative=picture.alternative,
            content_type_id=picture.content_type_id,
            object_id=picture.object_id,
            created_at=picture.created_at,
            updated_at=picture.updated_at,
        )

    @staticmethod
    def list_to_dto(pictures: list[PictureEntity]) -> list[PictureDTO]:
        """Converts a list of picture entities to dtos"""

        return [PictureDTOMapper.to_dto(picture) for picture in pictures]
