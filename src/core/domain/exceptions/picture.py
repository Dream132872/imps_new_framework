"""
Domain exceptions for picture entity.
"""

from shared.domain.exceptions import EntityNotFoundError

__all__ = ("PictureNotFoundError",)


class PictureNotFoundError(EntityNotFoundError):
    """Raised when picure not found in the repository."""
