"""
Custom model manager for user.
"""

from django.contrib.auth.models import UserManager

__all__ = ("CustomUserManager",)


class CustomUserManager(UserManager):
    pass

