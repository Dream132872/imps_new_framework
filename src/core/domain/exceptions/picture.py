"""
Domain exceptions for picture entity.
"""

from shared.domain.exceptions import DomainEntityNotFoundError

__all__ = ("PictureNotFoundError",)


class PictureNotFoundError(DomainEntityNotFoundError):
    """Raised when picure not found in the repository."""
