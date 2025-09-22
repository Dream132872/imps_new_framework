"""
Django repository implementation for picture.
"""

import uuid
from core.domain.entities import Picture
from core.domain.repositories import PictureRepository
from core.infrastructure.models import Picture as PictureModel
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoPictureRepository",)


class DjangoPictureRepository(DjangoRepository[Picture], PictureRepository):
    """
    Django implementation of picture repository.
    """

    def __init__(self) -> None:
        super().__init__(PictureModel, Picture)

    def _model_to_entity(self, model: PictureModel) -> Picture:
        return Picture(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            image=str(model.image),
            title=model.title,
            alternative=model.alternative,
            picture_type=model.picture_type,
            content_type=model.content_type_id,  # type: ignore
            object_id=model.object_id,
        )

    def _entity_to_model(self, entity: Picture) -> PictureModel:
        model, created = PictureModel.objects.get_or_create(
            id=entity.id,
            defaults={
                "image": entity.image,
                "alternative": entity.alternative,
                "title": entity.title,
                "picture_type": entity.picture_type,
                "content_type": entity.content_type,
                "object_id": entity.object_id,
            },
        )

        # If the model already existed, update its fields
        if not created:
            model.image = entity.image  # type: ignore
            model.alternative = entity.alternative
            model.title = entity.title
            model.picture_type = entity.picture_type
            model.content_type_id = uuid.UUID(entity.content_type)  # type: ignore
            model.object_id = uuid.UUID(entity.object_id) if entity.object_id else None

        return model
