"""
Domain base exceptions.
"""

__all__ = (
    "DomainException",
    "DomainEntityNotFoundError",
    "DomainInvalidEntityError",
    "DomainBusinessRuleViolationError",
    "DomainConcurrencyError",
    "DomainValidationError",
)


class DomainException(Exception):
    """Base exception for domain-related errors."""


class DomainEntityNotFoundError(DomainException):
    """Raised when an entity is not found in the repository."""


class DomainInvalidEntityError(DomainException):
    """Raised when an entity is in an invalid state."""


class DomainBusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""


class DomainConcurrencyError(DomainException):
    """Raised when there's a concurrency conflict."""


class DomainValidationError(DomainException):
    """Raised when validation fails."""
