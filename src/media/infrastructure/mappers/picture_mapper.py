"""Picture related mappers"""

from media.domain.entities import Picture as PictureEntity
from media.infrastructure.models import Picture as PictureModel
from shared.domain.factories import FileFieldFactory


class PictureMapper:
    """Picture mappers"""

    @staticmethod
    def entity_to_model(entity: PictureEntity) -> PictureModel:
        """Converts picture entity to picture model"""

        return PictureModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            image=entity.image.name,
            alternative=entity.alternative,
            title=entity.title,
            picture_type=entity.picture_type,
            content_type_id=entity.content_type_id,
            object_id=entity.object_id,
        )

    @staticmethod
    def model_to_entity(model: PictureModel) -> PictureEntity:
        """Converts picture model to picture entity"""

        image = FileFieldFactory.from_image_field(model.image)

        return PictureEntity(
            id=str(model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            image=image,
            title=model.title,
            alternative=model.alternative,
            picture_type=model.picture_type,
            content_type_id=model.content_type_id,
            object_id=model.object_id,  # type: ignore
        )
