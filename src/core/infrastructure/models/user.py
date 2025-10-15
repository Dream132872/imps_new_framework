"""
Implementation of Custom User model.
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _

from core.infrastructure.models.managers.user_manager import UserManager
from shared.infrastructure.models import BaseModel

__all__ = ("User",)


class User(AbstractUser, BaseModel):
    """Model definition for User."""

    # user avatar
    avatar = GenericRelation("core_infrastructure.Picture")

    manager = UserManager()

    class Meta:
        """Meta definition for User."""

        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username
