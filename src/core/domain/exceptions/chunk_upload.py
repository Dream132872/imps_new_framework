"""
Domain exceptions for chunk upload entity.
"""

from shared.domain.exceptions import (
    DomainBusinessRuleViolationError,
    DomainConcurrencyError,
    DomainEntityNotFoundError,
    DomainInvalidEntityError,
    DomainValidationError,
)


class ChunkUploadBuisinessRuleViolationError(DomainBusinessRuleViolationError):
    """Raised when a business rule for chunk upload is violated."""


class ChunkUploadConcurrencyError(DomainConcurrencyError):
    """Raised when there's a concurrency conflict in chunk uploads."""


class ChunkUploadNotFoundError(DomainEntityNotFoundError):
    """Raised when a chunk upload entity is not found in the repository."""


class ChunkUploadInvalidEntityError(DomainInvalidEntityError):
    """Raised when a chunk upload entity is in an invalid state."""


class ChunkUploadValidationError(DomainValidationError):
    """Raised when validation for chunk upload fails."""
