"""
User Query Handlers for CQRS implementation
"""

from __future__ import annotations

from injector import inject

from core.domain.entities import User
from core.domain.repositories import UserRepository
from shared.application.cqrs import *
from shared.domain.repositories import UnitOfWork

from ..queries.user_queries import *

__all__ = ("GetUserByIdQueryHandler",)


class GetUserByIdQueryHandler(QueryHandler[GetUserByIdQuery, User]):
    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def handle(self, query: GetUserByIdQuery) -> User:
        with self.uow:
            user = self.uow[UserRepository].get_by_id(str(query.user_id))
            if user:
                return user

            raise Exception("user not found")
