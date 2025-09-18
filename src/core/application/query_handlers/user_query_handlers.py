"""
User Query Handlers for CQRS implementation
"""

from __future__ import annotations

from injector import inject
import logging

from core.application.dtos.user_dtos import UserDTO
from core.application.queries.user_queries import *
from core.domain.entities import User
from core.domain.exceptions import UserNotFoundError
from core.domain.repositories import UserRepository
from shared.application.cqrs import *
from shared.domain.repositories import UnitOfWork
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

__all__ = ("GetUserByIdQueryHandler",)

logger = logging.getLogger(__file__)


class BaseUserQueryHandler:
    """Base class for user query handlers with common functionalities."""

    def _to_dto(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,  # type: ignore
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
    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def handle(self, query: GetUserByIdQuery) -> UserDTO:
        try:
            with self.uow:
                user = self.uow[UserRepository].get_by_id(str(query.user_id))
                if user:
                    return self._to_dto(user)

                raise UserNotFoundError(
                    _("User with ID {user_id} not found").format(user_id=query.user_id)
                )
        except Exception as e:
            raise ValidationError(
                _("Failed to get user with ID '{user_id}': {message}").format(
                    user_id=query.user_id, message=str(e)
                )
            )
