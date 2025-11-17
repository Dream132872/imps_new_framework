"""
User Queries for CQRS implementation.
"""

import uuid
from dataclasses import dataclass

from shared.application.cqrs import Query

__all__ = (
    "GetUserByIdQuery",
    "GetActiveUsersQuery",
    "SearchUsersQuery",
)


@dataclass
class GetUserByIdQuery(Query):
    """Query to get user by id."""

    user_id: str


@dataclass
class GetActiveUsersQuery(Query):
    """Query to get all active users."""


@dataclass
class SearchUsersQuery(Query):
    # pagination parameters
    page: int
    page_size: int
    paginated: bool = True

    # filter parameters
    full_name: str = ""
    email: str = ""
    username: str = ""

