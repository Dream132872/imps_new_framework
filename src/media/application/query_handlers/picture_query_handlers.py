"""
Picture Query Handlers for CQRS implementation.
"""

from __future__ import annotations

import logging

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.dtos import PictureDTO
from media.application.mappers import PictureDTOMapper
from media.application.queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from media.domain.exceptions import PictureNotFoundError
from media.domain.repositories import PictureRepository
from shared.application.cqrs import QueryHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.repositories import UnitOfWork

logger = logging.getLogger(__file__)


class BasePictureQueryHandler:
    """Base class for picture query handlers with common functionalities"""

    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow


class SearchPicturesQueryHandler(
    QueryHandler[SearchPicturesQuery, list[PictureDTO]],
    BasePictureQueryHandler,
):
    """Searches between all pictures based on query inputs."""

    def handle(self, query: SearchPicturesQuery) -> list[PictureDTO]:
        pictures = self.uow[PictureRepository].search_pictures(
            content_type=query.content_type_id,
            object_id=query.object_id,
            picture_type=query.picture_type,
        )

        return PictureDTOMapper.list_to_dto(pictures)


class SearchFirstPictureQueryHandler(
    QueryHandler[SearchFirstPictureQuery, PictureDTO | None],
    BasePictureQueryHandler,
):
    """Finds the first picture based on query inputs."""

    def handle(self, query: SearchFirstPictureQuery) -> PictureDTO | None:
        picture = self.uow[PictureRepository].search_first_picture(
            content_type=query.content_type_id,
            object_id=query.object_id,
            picture_type=query.picture_type,
        )

        return PictureDTOMapper.to_dto(picture) if picture else None


class GetPictureByIdQueryHandler(
    QueryHandler[GetPictureByIdQuery, PictureDTO],
    BasePictureQueryHandler,
):
    def handle(self, query: GetPictureByIdQuery) -> PictureDTO:
        try:
            picture = self.uow[PictureRepository].get_by_id(str(query.picture_id))
            return PictureDTOMapper.to_dto(picture)
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
