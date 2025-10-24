"""
Django repository implementation for picture.
"""

import uuid

from core.domain.entities import Picture
from core.domain.repositories import PictureRepository
from core.infrastructure.models import Picture as PictureModel
from shared.domain.factories import FileFieldFactory
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoPictureRepository",)


class DjangoPictureRepository(DjangoRepository[Picture], PictureRepository):
    """
    Django implementation of picture repository.
    """

    def __init__(self) -> None:
        super().__init__(PictureModel, Picture)

    def _model_to_entity(self, model: PictureModel) -> Picture:
        image = FileFieldFactory.from_image_field(model.image)
        return Picture(
            id=model.id,  # type: ignore
            created_at=model.created_at,
            updated_at=model.updated_at,
            image=image,
            title=model.title,
            alternative=model.alternative,
            picture_type=model.picture_type,
            content_type=model.content_type_id,
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

    def search_pictures(
        self,
        content_type: int | None = None,
        object_id: int | uuid.UUID | None = None,
        picture_type: str = "",
    ) -> list[Picture]:
        pictures = self.model_class.objects.all()

        if content_type and content_type is not None:
            pictures = pictures.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            pictures = pictures.filter(object_id=object_id)

        if picture_type and picture_type is not None:
            pictures = pictures.filter(picture_type__iexact=picture_type)

        return [
            self._model_to_entity(p) for p in list(pictures.order_by("display_order"))
        ]

    def search_first_picture(
        self,
        content_type: int | None = None,
        object_id: int | uuid.UUID | None = None,
        picture_type: str = "",
    ) -> Picture | None:
        pictures = self.model_class.objects.all()

        if content_type and content_type is not None:
            pictures = pictures.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            pictures = pictures.filter(object_id=object_id)

        if picture_type and picture_type is not None:
            pictures = pictures.filter(picture_type__iexact=picture_type)

        first_picture = pictures.order_by("display_order").first()
        return self._model_to_entity(first_picture) if first_picture else None
