"""
Custom model manager for user.
"""

from django.db import models

__all__ = ("UserManager",)


class UserManager(models.Manager):
    pass
