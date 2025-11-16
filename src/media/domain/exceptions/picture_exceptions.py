"""
Domain exceptions for picture entity.
"""

from shared.domain.exceptions import DomainEntityNotFoundError, DomainValidationError

__all__ = (
    "PictureNotFoundError",
    "PictureValidationError",
)


class PictureNotFoundError(DomainEntityNotFoundError):
    """Raised when picture not found in the repository."""


class PictureValidationError(DomainValidationError):
    """Raised when picture validation fails."""

