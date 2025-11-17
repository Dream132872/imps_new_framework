"""
Attachment Queries for CQRS implementation.
"""

import uuid
from dataclasses import dataclass

from shared.application.cqrs import Query


@dataclass
class GetAttachmentByIdQuery(Query):
    # attachment id
    attachment_id: str


@dataclass
class SearchAttachmentsQuery(Query):
    # django content type foreign key
    content_type_id: int | None = None
    # object id of related model
    object_id: str | int | None = None


@dataclass
class SearchFirstAttachmentQuery(SearchAttachmentsQuery):
    pass

