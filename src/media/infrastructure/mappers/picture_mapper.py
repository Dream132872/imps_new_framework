"""Picture related mappers"""

from media.domain.entities import Picture as PictureEntity
from media.infrastructure.models import Picture as PictureModel
from shared.domain.factories import FileFieldFactory


class PictureMapper:
    """Picture mappers"""

    @staticmethod
    def entity_to_model(entity: PictureEntity) -> PictureModel:
        """Converts picture entity to picture model"""

        model, created = PictureModel.objects.get_or_create(
            id=entity.id,
            defaults={
                "image": entity.image.name,
                "alternative": entity.alternative,
                "title": entity.title,
                "picture_type": entity.picture_type,
                "content_type_id": entity.content_type_id,
                "object_id": entity.object_id,
            },
        )

        # If the model already existed, update its fields
        if not created:
            model.image = entity.image.name  # type: ignore
            model.alternative = entity.alternative
            model.title = entity.title
            model.picture_type = entity.picture_type
            model.content_type_id = entity.content_type_id
            model.object_id = entity.object_id if entity.object_id else None  # type: ignore

        return model

    @staticmethod
    def model_to_entity(model: PictureModel) -> PictureEntity:
        """Converts picture model to picture entity"""

        image = FileFieldFactory.from_image_field(model.image)

        return PictureModel(
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
