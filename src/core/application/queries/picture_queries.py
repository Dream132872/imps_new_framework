"""
Picture Queries for CQRS implementation.
"""

import uuid
from dataclasses import dataclass

from shared.application.cqrs import Query

__all__ = (
    "SearchPicturesQuery",
    "SearchFirstPictureQuery",
)


@dataclass
class SearchPicturesQuery(Query):
    # django content type foreign key
    content_type_id: int | None = None
    # object id of related model
    object_id: uuid.UUID | int | None = None
    # picture type
    picture_type: str = "main"


@dataclass
class SearchFirstPictureQuery(SearchPicturesQuery):
    pass
