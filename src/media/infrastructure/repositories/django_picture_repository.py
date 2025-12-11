"""
Django repository implementation for picture.
"""

from django.utils.translation import gettext_lazy as _

from media.domain.entities import Picture
from media.domain.exceptions import PictureNotFoundError
from media.domain.repositories import PictureRepository
from media.infrastructure.mappers import PictureMapper
from media.infrastructure.models import Picture as PictureModel
from shared.domain.exceptions import DomainEntityNotFoundError
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
        return PictureMapper.model_to_entity(model)

    def _entity_to_model(self, entity: Picture) -> PictureModel:
        return PictureMapper.entity_to_model(entity)

    def get_by_id(self, id: str) -> Picture:
        try:
            return super().get_by_id(id)
        except DomainEntityNotFoundError as e:
            raise PictureNotFoundError(
                _("There is no picture with ID: {picture_id}").format(picture_id=id)
            )

    def search_pictures(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
        picture_type: str = "",
    ) -> list[Picture]:
        pictures = self.model_class.objects.select_related("content_type").all()

        if content_type and content_type is not None:
            pictures = pictures.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            pictures = pictures.filter(object_id=object_id)

        if picture_type and picture_type is not None:
            pictures = pictures.filter(picture_type__iexact=picture_type)

        return [
            self._model_to_entity(p)
            for p in list(pictures.order_by("display_order", "created_at"))
        ]

    def search_first_picture(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
        picture_type: str = "",
    ) -> Picture | None:
        pictures = self.model_class.objects.select_related("content_type").all()

        if content_type and content_type is not None:
            pictures = pictures.filter(content_type_id=content_type)

        if object_id and object_id is not None:
            pictures = pictures.filter(object_id=object_id)

        if picture_type and picture_type is not None:
            pictures = pictures.filter(picture_type__iexact=picture_type)

        first_picture = pictures.order_by("display_order", "created_at").first()
        return self._model_to_entity(first_picture) if first_picture else None
