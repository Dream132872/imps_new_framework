"""
Context variable management for request-scoped data.

This module provides utilities for managing context variables that are
scoped to the current request/async context. This is used for:
- Dependency injection scoping (UnitOfWork, etc.)
- Request object access
- User context
- Other per-request state
"""

from .context_variables import (
    ContextKeys,
    clear_request_scope,
    get_from_request_scope,
    require_from_request_scope,
    request_scope,
    set_in_request_scope,
)
from .helpers import (
    get_current_request,
    get_current_user,
    require_current_request,
    require_current_user,
)

__all__ = [
    "ContextKeys",
    "clear_request_scope",
    "get_current_request",
    "get_current_user",
    "get_from_request_scope",
    "require_current_request",
    "require_current_user",
    "require_from_request_scope",
    "request_scope",
    "set_in_request_scope",
]

