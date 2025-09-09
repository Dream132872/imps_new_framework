from typing import Any

from django.contrib.auth import get_user_model

from core.domain.entities import User
from core.domain.repositories import UserRepository
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoUserRepository",)

UserModel = get_user_model()


class DjangoUserRepository(DjangoRepository[User], UserRepository):
    def __init__(self) -> None:
        super().__init__(UserModel, User)

    async def _model_to_entity(self, model: Any) -> User:
        return User(
            id=model.id,
            username=model.username,
        )
