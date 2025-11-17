"""
Domain exceptions for attachment entity.
"""

from shared.domain.exceptions import DomainEntityNotFoundError, DomainValidationError

__all__ = (
    "AttachmentNotFoundError",
    "AttachmentValidationError",
)


class AttachmentNotFoundError(DomainEntityNotFoundError):
    """Raised when attachment not found in the repository."""


class AttachmentValidationError(DomainValidationError):
    """Raised when attachment validation fails."""

