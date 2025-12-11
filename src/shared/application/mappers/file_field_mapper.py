"""FileField related mappers"""

from shared.application.dtos import FileFieldDTO
from shared.domain.entities import FileField as FileFieldEntity


class FileFieldDTOMapper:
    """FileField dto mapper"""

    @staticmethod
    def entity_to_dto(file_field: FileFieldEntity, file_type: str) -> FileFieldDTO:
        """Converts FileField entity instance to entity instance"""

        return FileFieldDTO(
            file_type=file_type,
            url=file_field.image.url,
            name=file_field.image.name,
            size=file_field.image.size,
            width=file_field.image.width,
            height=file_field.image.height,
            content_type=file_field.image.content_type,
        )
