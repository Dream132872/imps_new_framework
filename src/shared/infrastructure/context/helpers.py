"""
Helper functions for common context variable use cases.

This module provides convenient, type-safe helpers for accessing
commonly used context variables.
"""

from typing import Optional

from django.http import HttpRequest

from identity.domain.entities import User

from .context_variables import (
    ContextKeys,
    get_from_request_scope,
    require_from_request_scope,
)


def get_current_user() -> Optional[User]:
    """Get current authenticated user from context.

    Returns:
        The current authenticated User entity, or None if not authenticated

    Example:
        >>> user = get_current_user()
        >>> if user:
        ...     print(f"Current user: {user.email}")
    """
    return get_from_request_scope(ContextKeys.CURRENT_USER)


def require_current_user() -> User:
    """Get current authenticated user from context, raise if not authenticated.

    Use this when the user must be authenticated for the operation to proceed.

    Returns:
        The current authenticated User entity

    Raises:
        KeyError: If no user is found in context (not authenticated)

    Example:
        >>> try:
        ...     user = require_current_user()
        ...     # Proceed with authenticated operation
        ... except KeyError:
        ...     # Handle unauthenticated case
    """
    return require_from_request_scope(ContextKeys.CURRENT_USER)


def get_current_request() -> Optional[HttpRequest]:
    """Get current Django request from context.

    Returns:
        The current HttpRequest object, or None if not set

    Example:
        >>> request = get_current_request()
        >>> if request:
        ...     method = request.method
    """
    return get_from_request_scope(ContextKeys.CURRENT_REQUEST)


def require_current_request() -> HttpRequest:
    """Get current Django request from context, raise if not set.

    Returns:
        The current HttpRequest object

    Raises:
        KeyError: If no request is found in context

    Example:
        >>> request = require_current_request()
        >>> method = request.method
    """
    return require_from_request_scope(ContextKeys.CURRENT_REQUEST)

