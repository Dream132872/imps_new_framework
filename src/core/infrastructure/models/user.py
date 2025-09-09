from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.models import BaseModel

__all__ = ("User",)


class User(AbstractUser, BaseModel):
    """Model definition for User."""

    class Meta:
        """Meta definition for User."""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
