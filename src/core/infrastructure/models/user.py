"""
Implementation of Custom User model.
"""

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from core.infrastructure.model_managers import UserManager
from shared.infrastructure.models import BaseModel

__all__ = ("User",)


class User(AbstractUser, BaseModel):
    """Model definition for User."""

    manager = UserManager()

    class Meta:
        """Meta definition for User."""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
