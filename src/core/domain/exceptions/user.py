"""
Domain exceptions for user entity.
"""

from shared.domain.exceptions import EntityNotFoundError

__all__ = ("UserNotFoundError",)


class UserNotFoundError(EntityNotFoundError):
    """Raised when user not found in the repository."""
