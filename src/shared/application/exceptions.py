"""
Shared application exceptions.
"""

from typing import Any

__all__ = ("ConfigurationError",)


class ApplicationError(Exception):
    """Base exception for application layer errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(ApplicationError):
    """Exception raised when there's a configuration error."""
