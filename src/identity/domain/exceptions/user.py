"""
Domain exceptions for user entity.
"""

from shared.domain.exceptions import (
    DomainBusinessRuleViolationError,
    DomainConcurrencyError,
    DomainEntityNotFoundError,
    DomainInvalidEntityError,
    DomainValidationError,
)

__all__ = ("UserNotFoundError",)


class UserNotFoundError(DomainEntityNotFoundError):
    """Raised when a user is not found in the repository."""


class UserInvalidError(DomainInvalidEntityError):
    """Raised when user in an invalid state."""


class UserValidationError(DomainValidationError):
    """Raised when user validation fails."""


class UserBusinessRuleViolationError(DomainBusinessRuleViolationError):
    """Raised when a business rule is violated for user entity."""


class UserConcurrencyError(DomainConcurrencyError):
    """Raised when there's a concurrency conflict for user entity."""

