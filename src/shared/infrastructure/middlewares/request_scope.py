"""
Middleware for managing request-scoped services.

This middleware initializes and cleans up the request scope, ensuring
that services like UnitOfWork are properly scoped per request (similar to
ASP.NET Core's scoped services).
"""

from adrf.requests import AsyncRequest, Request
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from shared.infrastructure.context import (
    ContextKeys,
    clear_request_scope,
    set_in_request_scope,
)


class RequestScopeMiddleware(MiddlewareMixin):
    """
    Middleware that manages request-scoped services.

    This ensures that services like UnitOfWork are created once per request
    and properly cleaned up after the request completes, similar to ASP.NET Core's
    scoped service lifetime.
    """

    def process_request(self, request: HttpRequest | AsyncRequest | Request) -> None:
        """Initialize request scope at the start of the request."""
        # Set the current request in context
        set_in_request_scope(ContextKeys.CURRENT_REQUEST, request)
        
        # Set user if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_in_request_scope(ContextKeys.CURRENT_USER, request.user)

    def process_response(
        self, request: HttpRequest | AsyncRequest | Request, response: HttpResponse
    ) -> HttpResponse:
        """Clean up request scope after the request completes."""
        clear_request_scope()
        return response

    def process_exception(
        self, request: HttpRequest | AsyncRequest | Request, exception: Exception
    ) -> None:
        """Clean up request scope even if an exception occurs."""
        clear_request_scope()
