"""
Domain base exceptions.
"""

__all__ = (
    "EntityNotFoundError",
    "InvalidEntityError",
    "BusinessRuleViolationError",
    "ConcurrencyError",
    "DomainValidationError",
)


class DomainException(Exception):
    """Base exception for domain-related errors."""


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found in the repository."""


class InvalidEntityError(DomainException):
    """Raised when an entity is in an invalid state."""


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""


class ConcurrencyError(DomainException):
    """Raised when there's a concurrency conflict."""


class DomainValidationError(DomainException):
    """Raised when validation fails."""
