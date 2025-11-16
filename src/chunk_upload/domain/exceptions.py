"""
Domain exceptions for chunk upload entity (moved from core bounded context).
"""

from shared.domain.exceptions import (
    DomainBusinessRuleViolationError,
    DomainConcurrencyError,
    DomainEntityNotFoundError,
    DomainInvalidEntityError,
    DomainValidationError,
)

__all__ = (
    "ChunkUploadBuisinessRuleViolationError",
    "ChunkUploadConcurrencyError",
    "ChunkUploadNotFoundError",
    "ChunkUploadInvalidEntityError",
    "ChunkUploadValidationError",
)


class ChunkUploadBuisinessRuleViolationError(DomainBusinessRuleViolationError):
    """Raised when chunk upload business rule is violated."""


class ChunkUploadConcurrencyError(DomainConcurrencyError):
    """Raised when chunk upload concurrency conflict occurs."""


class ChunkUploadNotFoundError(DomainEntityNotFoundError):
    """Raised when chunk upload not found in the repository."""


class ChunkUploadInvalidEntityError(DomainInvalidEntityError):
    """Raised when chunk upload entity is in an invalid state."""


class ChunkUploadValidationError(DomainValidationError):
    """Raised when chunk upload validation fails."""


