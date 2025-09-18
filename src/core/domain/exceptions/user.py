"""
Domain exceptions for user entity.
"""

from shared.domain.exceptions import *

__all__ = ("UserNotFoundError",)


class UserNotFoundError(EntityNotFoundError):
    """Raised when user not found in the repository."""
