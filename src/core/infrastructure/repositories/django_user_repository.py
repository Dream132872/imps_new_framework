"""
Django repository implementation for user.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import F, Value
from django.db.models.functions import Concat

from core.domain.entities import User
from core.domain.repositories import UserRepository
from shared.domain.pagination import DomainPaginator
from shared.infrastructure.repositories import DjangoRepository
from shared.infrastructure.pagination import DjangoPaginatorFactory

__all__ = ("DjangoUserRepository",)

UserModel = get_user_model()


class DjangoUserRepository(DjangoRepository[User], UserRepository):
    """
    Django implementation of uesr repository.
    """

    def __init__(self) -> None:
        super().__init__(UserModel, User)

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

        # Return domain paginator
        return DjangoPaginatorFactory.create_domain_paginator(
            queryset=query,
            page=page,
            page_size=page_size,
            entity_converter=self._model_to_entity,
        )

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

    def _entity_to_model(self, entity: User) -> UserModel:  # type: ignore
        user, created = self.model_class.objects.get_or_create(
            pk=entity.id,
            defaults={
                "username": entity.username,
                "password": entity.password,
                "first_name": entity.first_name,
                "last_name": entity.last_name,
                "email": entity.email.value if entity.email else "",
                "is_staff": entity.is_staff,
                "is_superuser": entity.is_superuser,
                "is_active": entity.is_active,
            },
        )

        if not created:
            user.username = entity.username
            user.password = entity.password
            user.first_name = entity.first_name
            user.last_name = entity.last_name
            user.email = entity.email
            user.is_staff = entity.is_staff
            user.is_superuser = entity.is_superuser
            user.is_active = entity.is_active

        return user
