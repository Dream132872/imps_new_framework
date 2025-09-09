"""
Shared application errors.
"""

from typing import Any, Dict, Optional


class ApplicationError(Exception):
    """Base exception for application layer errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Exception raised when validation fails."""


class BusinessRuleViolationError(ApplicationError):
    """Exception raised when business rules are violated."""


class ResourceNotFoundError(ApplicationError):
    """Exception raised when a requested resource is not found."""


class UnAuthorizedError(ApplicationError):
    """Exception raised when access is unauthorized"""


class ConflictError(ApplicationError):
    """Exception raised when there's a conflict (e.g. duplicate resources)"""


class ConfigurationError(ApplicationError):
    """Exception raised when there's configuration error"""
