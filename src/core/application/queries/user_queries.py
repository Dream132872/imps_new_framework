"""
User Queries for CQRS implementation.
"""

import uuid
from dataclasses import dataclass

from shared.application.cqrs import Query

__all__ = ("GetUserByIdQuery",)


@dataclass
class GetUserByIdQuery(Query):
    """Query to get user by id"""

    user_id: uuid.UUID
