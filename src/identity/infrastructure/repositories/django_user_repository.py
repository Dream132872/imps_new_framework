"""
Django repository implementation for user.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _

from identity.domain.entities import User
from identity.domain.exceptions import UserNotFoundError
from identity.domain.repositories import UserRepository
from identity.infrastructure.mappers import UserMapper
from shared.domain.exceptions import DomainEntityNotFoundError
from shared.domain.pagination import DomainPaginator
from shared.infrastructure.pagination import DjangoPaginatorFactory
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoUserRepository",)

UserModel = get_user_model()


class DjangoUserRepository(DjangoRepository[User], UserRepository):
    """
    Django implementation of user repository.
    """

    def __init__(self) -> None:
        super().__init__(UserModel, User)

    def _model_to_entity(self, model: Any) -> User:
        return UserMapper.model_to_entity(model)

    def _entity_to_model(self, entity: User) -> UserModel:  # type: ignore
        return UserMapper.entity_to_model(entity)

    def get_by_id(self, id: str) -> User:
        try:
            return super().get_by_id(id)
        except DomainEntityNotFoundError as e:
            raise UserNotFoundError(
                _("There is no user with ID: {user_id}").format(user_id=id)
            )

    def search_users(
        self,
        full_name: str = "",
        email: str = "",
        username: str = "",
        page: int = 1,
        page_size: int = 25,
    ) -> DomainPaginator[User]:
        """
        Search users with pagination using domain paginator.
        """
        # Build the base query
        query = self.model_class.objects.annotate(
            full_name=Concat(F("first_name"), Value(" "), F("last_name"))
        ).all()

        # Apply filters
        if full_name:
            query = query.filter(full_name__icontains=full_name)
        if email:
            query = query.filter(email__icontains=email)
        if username:
            query = query.filter(username__icontains=username)

        query = query.order_by("-created_at")
        # Return domain paginator
        return DjangoPaginatorFactory.create_domain_paginator(
            queryset=query,
            page=page,
            page_size=page_size,
            entity_converter=self._model_to_entity,
        )
