"""FileField related mappers"""

from shared.application.dtos import FileFieldDTO
from shared.domain.entities import FileField as FileFieldEntity
from shared.domain.entities import FileFieldType


class FileFieldDTOMapper:
    """FileField dto mapper"""

    @staticmethod
    def to_dto(file_field: FileFieldEntity, file_type: FileFieldType) -> FileFieldDTO:
        """Converts FileField entity instance to entity instance"""

        url = file_field.url
        name = file_field.name
        size = file_field.size
        content_type = file_field.content_type
        width = None
        height = None

        match file_type:
            case FileFieldType.IMAGE:
                width = file_field.width
                height = file_field.height
            case FileFieldType.FILE:
                pass

        return FileFieldDTO(
            file_type=file_type.value,
            url=url,
            name=name,
            size=size,
            width=width,
            height=height,
            content_type=content_type,
        )
