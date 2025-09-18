"""
Django repository implementation for user.
"""

from typing import Any

from django.contrib.auth import get_user_model

from core.domain.entities import User
from core.domain.repositories import UserRepository
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoUserRepository",)

UserModel = get_user_model()


class DjangoUserRepository(DjangoRepository[User], UserRepository):
    """
    Django implementation of uesr repository.
    """

    def __init__(self) -> None:
        super().__init__(UserModel, User)

    def _model_to_entity(self, model: Any) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            is_active=model.is_active,
            first_name=model.first_name,
            last_name=model.last_name,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
