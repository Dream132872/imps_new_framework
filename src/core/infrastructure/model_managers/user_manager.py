"""
Custom model manager for user.
"""

from django.contrib.auth.models import BaseUserManager

__all__ = ("UserManager",)


class UserManager(BaseUserManager):
    pass
