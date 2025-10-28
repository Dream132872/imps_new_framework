"""
Picture Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging

from injector import inject

from core.application.dtos.picture_dtos import PictureDTO
from core.application.queries.picture_queries import (
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from core.domain.entities import Picture
from core.domain.exceptions.picture import *
from core.domain.repositories import PictureRepository
from shared.application.cqrs import QueryHandler
from shared.application.dtos import FileFieldDTO
from shared.domain.repositories import UnitOfWork

logger = logging.getLogger(__file__)


class BasePictureQueryHandler:
    """Base class for picture query handlers with common functionalities"""

    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def _to_dto(self, picture: Picture) -> PictureDTO:
        image = FileFieldDTO(
            file_type="image",
            url=picture.image.url,
            name=picture.image.name,
            size=picture.image.size,
            width=picture.image.width,
            height=picture.image.height,
            content_type=picture.image.content_type,
        )
        return PictureDTO(
            id=picture.id,
            image=image,
            picture_type=picture.picture_type,
            title=picture.title,
            alternative=picture.alternative,
            content_type=picture.content_type,
            object_id=picture.object_id,
            created_at=picture.created_at,
            updated_at=picture.updated_at,
        )


class SearchPicturesQueryHandler(
    QueryHandler[SearchPicturesQuery, list[PictureDTO]], BasePictureQueryHandler
):
    """Searches between all pictures based on query inputs."""

    def handle(self, query: SearchPicturesQuery) -> list[PictureDTO]:
        with self.uow:
            pictures = self.uow[PictureRepository].search_pictures(
                content_type=query.content_type_id,
                object_id=query.object_id,
                picture_type=query.picture_type,
            )

            return [self._to_dto(p) for p in pictures]


class SearchFirstPictureQueryHandler(
    QueryHandler[SearchFirstPictureQuery, PictureDTO | None], BasePictureQueryHandler
):
    """Finds the first picture based on query inputs."""

    def handle(self, query: SearchFirstPictureQuery) -> PictureDTO | None:
        with self.uow:
            picture = self.uow[PictureRepository].search_first_picture(
                content_type=query.content_type_id,
                object_id=query.object_id,
                picture_type=query.picture_type,
            )

            return self._to_dto(picture) if picture else None
