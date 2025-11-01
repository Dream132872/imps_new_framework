"""
Domain exceptions for user entity.
"""

from shared.domain.exceptions import DomainEntityNotFoundError

__all__ = ("UserNotFoundError",)


class UserNotFoundError(DomainEntityNotFoundError):
    """Raised when user not found in the repository."""
