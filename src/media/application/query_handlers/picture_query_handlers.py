"""
Picture Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging
from typing import Any

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.dtos import PictureDTO
from media.application.queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from media.domain.entities import Picture
from media.domain.exceptions import PictureNotFoundError
from media.domain.repositories import PictureRepository
from shared.application.cqrs import QueryHandler
from shared.application.dtos import FileFieldDTO
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
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
            content_type_id=picture.content_type_id,
            object_id=picture.object_id,
            created_at=picture.created_at,
            updated_at=picture.updated_at,
        )


class SearchPicturesQueryHandler(
    QueryHandler[SearchPicturesQuery, list[PictureDTO]],
    BasePictureQueryHandler,
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
    QueryHandler[SearchFirstPictureQuery, PictureDTO | None],
    BasePictureQueryHandler,
):
    """Finds the first picture based on query inputs."""

    def handle(
        self, query: SearchFirstPictureQuery
    ) -> PictureDTO | None:
        with self.uow:
            picture = self.uow[PictureRepository].search_first_picture(
                content_type=query.content_type_id,
                object_id=query.object_id,
                picture_type=query.picture_type,
            )

            return self._to_dto(picture) if picture else None


class GetPictureByIdQueryHandler(
    QueryHandler[GetPictureByIdQuery, PictureDTO],
    BasePictureQueryHandler,
):
    def handle(self, query: GetPictureByIdQuery) -> PictureDTO:
        try:
            with self.uow:
                picture = self.uow[PictureRepository].get_by_id(str(query.picture_id))
                if not picture:
                    raise PictureNotFoundError(
                        _("There is no picture with ID: {picture_id}").format(
                            picture_id=query.picture_id
                        )
                    )

                return self._to_dto(picture)
        except PictureNotFoundError as e:
            raise map_domain_exception_to_application(
                e, message=_("Picture not found: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("Could not get picture with ID: {picture_id}").format(
                    picture_id=query.picture_id
                )
            ) from e

