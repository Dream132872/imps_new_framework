"""
User Query Handlers for CQRS implementation
"""

from __future__ import annotations

import logging

from django.utils.translation import gettext_lazy as _
from injector import inject

from identity.application.dtos.user_dtos import UserDTO
from identity.application.queries.user_queries import GetUserByIdQuery, SearchUsersQuery
from identity.domain.entities import User
from identity.domain.exceptions import UserNotFoundError
from identity.domain.exceptions.user import UserInvalidError
from identity.domain.repositories import UserRepository
from shared.application.cqrs import QueryHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError, ApplicationValidationError
from shared.application.pagination import (
    PaginatedResultDTO,
    convert_to_paginated_result_dto,
)
from shared.domain.repositories import UnitOfWork

__all__ = (
    "GetUserByIdQueryHandler",
    "GetUserByIdQueryHandler",
    "SearchUsersQueryHandler",
)

logger = logging.getLogger(__file__)


class BaseUserQueryHandler:
    """Base class for user query handlers with common functionalities."""

    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def _to_dto(self, user: User) -> UserDTO:
        """Map the UserEntity to UserDTO

        Args:
            user (User): an instance of User entity.

        Returns:
            UserDTO: an instance of UserDTO
        """
        return UserDTO(
            id=str(user.id),
            username=user.username,
            email=user.email.value if user.email else "",
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class GetUserByIdQueryHandler(
    QueryHandler[GetUserByIdQuery, UserDTO], BaseUserQueryHandler
):
    """Handle GetUserById query."""

    def handle(self, query: GetUserByIdQuery) -> UserDTO:
        try:
            user = self.uow[UserRepository].get_by_id(query.user_id)
            if user:
                return self._to_dto(user)

            raise UserNotFoundError(
                _("User with ID {user_id} not found").format(user_id=query.user_id)
            )
        except Exception as e:
            raise ApplicationValidationError(
                _("Failed to get user with ID '{user_id}': {message}").format(
                    user_id=query.user_id, message=str(e)
                )
            )


class SearchUsersQueryHandler(
    QueryHandler[SearchUsersQuery, PaginatedResultDTO], BaseUserQueryHandler
):
    """Handle SearchUsers query"""

    def handle(self, query: SearchUsersQuery) -> PaginatedResultDTO:
        try:
            paginated_users = self.uow[UserRepository].search_users(
                full_name=query.full_name,
                email=query.email,
                username=query.username,
                page=query.page,
                page_size=query.page_size,
            )

            return convert_to_paginated_result_dto(
                paginated_object=paginated_users,
                items=[self._to_dto(u) for u in paginated_users.items],
            )
        except Exception as e:
            raise ApplicationError(
                _("Failed to search users: {message}").format(message=str(e))
            )
