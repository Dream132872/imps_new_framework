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
    """
    Base exception for domain-related errors.
    """


class DomainEntityNotFoundError(DomainException):
    """
    Raised when an entity is not found in the repository.

    When to use: When an entity cannot be found in the repository.
    Where to use: In the infrastructure layer (repositories) when a lookup fails.
    """


class DomainInvalidEntityError(DomainException):
    """
    Raised when an entity is in an invalid state.

    When to use: When an entity is in an invalid state (e.g., inconsistent internal data, missing required fields after construction).
    Where to use: In domain entities or value objects to guard invariants.
    Example scenario: An Order entity missing a customer ID when it should be required.
    """


class DomainBusinessRuleViolationError(DomainException):
    """
    Raised when a business rule is violated.

    When to use: When a business/invariant rule is violated.
    Where to use: In domain entities or domain services when enforcing rules.
    Example scenarios:
    "Order total cannot exceed customer credit limit"
    "Product cannot be discontinued if it has active orders"
    Difference from ValidationError: ValidationError is for format/syntax; BusinessRuleViolationError is for domain rules that make business sense but are not allowed.
    """


class DomainConcurrencyError(DomainException):
    """
    Raised when there's a concurrency conflict.

    When to use: When a concurrency conflict occurs (e.g., optimistic locking violation, version mismatch).
    Where to use: In repositories or UoW when version/optimistic locking checks fail.
    Example scenario: Two users modify the same entity simultaneously, causing a version conflict.
    """


class DomainValidationError(DomainException):
    """
    Raised when validation fails.

    When to use: When validation fails (format, data type, required fields, simple constraints).
    Where to use: In domain entities when validating input data.
    """
