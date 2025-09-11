"""
User Query Handlers for CQRS implementation
"""

from core.domain.entities import User
from core.domain.repositories import UserRepository
from shared.application.cqrs import *
from shared.domain.repositories import UnitOfWork
from shared.infrastructure.ioc import inject_dependencies

from ..queries import GetUserByIdQuery

__all__ = ("GetProductByIdQueryHandler",)


class GetProductByIdQueryHandler(QueryHandler[GetUserByIdQuery, User]):
    # @inject_dependencies()
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def handle(self, query: GetUserByIdQuery) -> User:
        with self.uow:
            user = self.uow[UserRepository].get_by_id(str(query.user_id))
            if user:
                return user

            raise Exception("user not found")
