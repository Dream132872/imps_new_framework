"""
Shared application exceptions.
"""

from typing import Any

__all__ = (
    "ApplicationError",
    "ApplicationValidationError",
    "ApplicationNotFoundError",
    "ApplicationConfigurationError",
    "ApplicationConcurrencyError",
    "ApplicationInvalidEntityError",
    "ApplicationBusinessRuleViolationError",
)


class ApplicationError(Exception):
    """Base exception for application layer errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ApplicationValidationError(ApplicationError):
    """Exception raised when there's a validation error."""


class ApplicationNotFoundError(ApplicationError):
    """Exception raised when expected item is not found."""


class ApplicationConfigurationError(ApplicationError):
    """Exception raised when there's a configuration error."""


class ApplicationConcurrencyError(ApplicationError):
    """Exception raised when there's a concurrency conflict (e.g., optimistic locking)."""


class ApplicationInvalidEntityError(ApplicationError):
    """Exception raised when an entity is in an invalid state."""


class ApplicationBusinessRuleViolationError(ApplicationError):
    """Exception raised when a business rule is violated."""
