"""
Middleware for managing request-scoped services.

This middleware initializes and cleans up the request scope, ensuring
that services like UnitOfWork are properly scoped per request (similar to
ASP.NET Core's scoped services).
"""

from adrf.requests import AsyncRequest, Request
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from shared.infrastructure.ioc import clear_request_scope


class RequestScopeMiddleware(MiddlewareMixin):
    """
    Middleware that manages request-scoped services.

    This ensures that services like UnitOfWork are created once per request
    and properly cleaned up after the request completes, similar to ASP.NET Core's
    scoped service lifetime.
    """

    def process_request(self, request: HttpRequest | AsyncRequest | Request) -> None:
        """Initialize request scope at the start of the request."""
        # The context variable is automatically initialized with an empty dict
        # when accessed for the first time in a new context
        pass

    def process_response(self, request: HttpRequest | AsyncRequest | Request, response) -> None:
        """Clean up request scope after the request completes."""
        clear_request_scope()
        return response

    def process_exception(
        self, request: HttpRequest | AsyncRequest | Request, exception: Exception
    ) -> None:
        """Clean up request scope even if an exception occurs."""
        clear_request_scope()

