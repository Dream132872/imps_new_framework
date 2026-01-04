"""
Context variable management for request-scoped data.

This module provides utilities for managing context variables that are
scoped to the current request/async context using Python's contextvars.
"""

import contextvars
from typing import Any


class ContextKeys:
    """Constants for request scope keys.

    Use these constants instead of magic strings to avoid typos and
    ensure consistency across the codebase.
    """

    CURRENT_REQUEST = "__current_request__"
    CURRENT_USER = "__current_user__"
    UNIT_OF_WORK = "__unit_of_work__"


# Main context variable for request-scoped data
request_scope: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "_request_scope", default={}
)


def get_from_request_scope(key: str, default: Any = None) -> Any:
    """Get value from request scope with optional default.

    Args:
        key: The key to look up in the request scope
        default: Default value to return if key is not found

    Returns:
        The value associated with the key, or default if not found

    Example:
        >>> user = get_from_request_scope(ContextKeys.CURRENT_USER)
        >>> user = get_from_request_scope(ContextKeys.CURRENT_USER, None)
    """
    scope = request_scope.get()
    return scope.get(key, default)


def require_from_request_scope(key: str) -> Any:
    """Get value from request scope, raise KeyError if not found.

    Use this when the value is required and its absence indicates
    a programming error or misconfiguration.

    Args:
        key: The key to look up in the request scope

    Returns:
        The value associated with the key

    Raises:
        KeyError: If the key is not found in the request scope

    Example:
        >>> user = require_from_request_scope(ContextKeys.CURRENT_USER)
    """
    scope = request_scope.get()
    if key not in scope:
        raise KeyError(f"Key '{key}' not found in request scope")
    return scope[key]


def set_in_request_scope(key: str, value: Any) -> None:
    """Set value in request scope.

    Args:
        key: The key to store the value under
        value: The value to store

    Example:
        >>> set_in_request_scope(ContextKeys.CURRENT_USER, user)
    """
    scope = request_scope.get()
    scope[key] = value


def clear_request_scope() -> None:
    """Clear all request-scoped values.

    This should be called at the end of each request to ensure
    services are properly cleaned up and not leaked between requests.
    Typically called by RequestScopeMiddleware.
    """
    scope = request_scope.get()
    scope.clear()

