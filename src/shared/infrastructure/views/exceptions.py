"""
Exception handling for infrastructure layer.

This module provides exception handlers for both Django REST Framework (DRF) API views
and Django web views. It handles Application layer exceptions and converts them
to appropriate HTTP responses or user-friendly messages.
"""

import logging
from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateResponseMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from shared.application.exceptions import (
    ApplicationBusinessRuleViolationError,
    ApplicationConcurrencyError,
    ApplicationError,
    ApplicationInvalidEntityError,
    ApplicationNotFoundError,
    ApplicationValidationError,
)

logger = logging.getLogger(__name__)

__all__ = ("drf_custom_exception_handler", "ApplicationExceptionHandlerMixin")


def drf_custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """
    Custom exception handler for Django REST Framework.

    This handler catches Application layer exceptions and converts them to
    appropriate HTTP responses. Domain exceptions should never reach this handler
    as they should be transformed to Application exceptions in the Application layer.

    Args:
        exc: The exception that was raised
        context: Dictionary containing request context information

    Returns:
        Response object or None if exception should be handled by default DRF handler
    """
    # Let DRF handle its own exceptions first
    response = drf_exception_handler(exc, context)

    # Handle Application layer exceptions
    if isinstance(exc, ApplicationNotFoundError):
        logger.warning(
            "ApplicationNotFoundError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_404_NOT_FOUND,
        )

    elif isinstance(exc, ApplicationValidationError):
        logger.warning(
            "ApplicationValidationError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif isinstance(exc, ApplicationInvalidEntityError):
        logger.warning(
            "ApplicationInvalidEntityError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif isinstance(exc, ApplicationBusinessRuleViolationError):
        logger.warning(
            "ApplicationBusinessRuleViolationError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    elif isinstance(exc, ApplicationConcurrencyError):
        logger.warning(
            "ApplicationConcurrencyError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_409_CONFLICT,
        )

    elif isinstance(exc, ApplicationError):
        logger.error(
            "ApplicationError occurred: %s (details: %s)",
            exc.message,
            exc.details,
            exc_info=True,
        )
        return Response(
            {"error": exc.message, "details": exc.details},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # If response is None, DRF couldn't handle it and we couldn't either
    # Return None to let Django handle it (will result in 500)
    return response


class ApplicationExceptionHandlerMixin:
    """
    Mixin for Django views to handle Application layer exceptions.

    This mixin should be added to Django views (FormView, TemplateView, etc.)
    to automatically handle Application exceptions that bubble up from the
    Application layer. Domain exceptions should never reach this mixin as they
    should be transformed to Application exceptions in the Application layer.

    Usage:
        class MyView(ApplicationExceptionHandlerMixin, FormView):
            pass
    """

    # Override these attributes in your view to customize behavior
    error_redirect_url: str | None = (
        None  # URL to redirect on error (default: stay on page)
    )
    show_error_messages: bool = (
        True  # Whether to show error messages via Django messages
    )

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """
        Override dispatch to catch Application exceptions.

        Returns:
            HttpResponse or raises exception if not an Application exception
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except ApplicationNotFoundError as e:
            return self._handle_not_found_error(request, e)
        except ApplicationValidationError as e:
            return self._handle_validation_error(request, e)
        except ApplicationInvalidEntityError as e:
            return self._handle_validation_error(request, e)  # Similar handling
        except ApplicationBusinessRuleViolationError as e:
            return self._handle_validation_error(request, e)  # Similar handling
        except ApplicationConcurrencyError as e:
            return self._handle_concurrency_error(request, e)
        except ApplicationError as e:
            return self._handle_application_error(request, e)

    def _handle_not_found_error(
        self, request: HttpRequest, exc: ApplicationNotFoundError
    ) -> Any:
        """Handle ApplicationNotFoundError."""
        logger.warning(
            "ApplicationNotFoundError in view %s: %s (details: %s)",
            self.__class__.__name__,
            exc.message,
            exc.details,
            exc_info=True,
        )

        if self.show_error_messages:
            messages.error(request, exc.message)

        # For FormView, add error to form
        if hasattr(self, "form_class") and hasattr(self, "get_form"):
            form = self.get_form()
            form.add_error(None, exc.message)
            if hasattr(self, "form_invalid"):
                return self.form_invalid(form)

        # Redirect if specified
        if self.error_redirect_url:
            return redirect(self.error_redirect_url)

        # Default: re-render the page (for TemplateView, FormView, etc.)
        # For TemplateView/FormView, render the template directly
        if isinstance(self, TemplateResponseMixin) and hasattr(
            self, "get_template_names"
        ):
            return self.render_to_response(self.get_context_data())

        # Fallback: return a simple response (should not happen in normal flow)
        return HttpResponse("An error occurred. Please try again.")

    def _handle_validation_error(
        self, request: HttpRequest, exc: ApplicationValidationError
    ) -> Any:
        """Handle ApplicationValidationError."""
        logger.warning(
            "ApplicationValidationError in view %s: %s (details: %s)",
            self.__class__.__name__,
            exc.message,
            exc.details,
            exc_info=True,
        )

        if self.show_error_messages:
            messages.error(request, exc.message)

        # For FormView, add error to form
        if hasattr(self, "form_class") and hasattr(self, "get_form"):
            form = self.get_form()
            # Add field-specific errors from details if available
            if exc.details:
                for field, error_msg in exc.details.items():
                    if isinstance(error_msg, str):
                        form.add_error(field, error_msg)
                    elif isinstance(error_msg, list):
                        for msg in error_msg:
                            form.add_error(field, msg)
            else:
                form.add_error(None, exc.message)

            if hasattr(self, "form_invalid"):
                return self.form_invalid(form)

        # Redirect if specified
        if self.error_redirect_url:
            return redirect(self.error_redirect_url)

        # Default: re-render the page
        # For TemplateView/FormView, render the template directly
        if isinstance(self, TemplateResponseMixin) and hasattr(
            self, "get_template_names"
        ):
            return self.render_to_response(self.get_context_data())

        # Fallback: return a simple response (should not happen in normal flow)
        return HttpResponse("An error occurred. Please try again.")

    def _handle_concurrency_error(
        self, request: HttpRequest, exc: ApplicationConcurrencyError
    ) -> Any:
        """Handle ApplicationConcurrencyError."""
        logger.warning(
            "ApplicationConcurrencyError in view %s: %s (details: %s)",
            self.__class__.__name__,
            exc.message,
            exc.details,
            exc_info=True,
        )

        if self.show_error_messages:
            messages.warning(
                request,
                exc.message
                or "The resource was modified by another user. Please refresh and try again.",
            )

        # For FormView, add error to form
        if hasattr(self, "form_class") and hasattr(self, "get_form"):
            form = self.get_form()
            form.add_error(
                None,
                exc.message
                or "The resource was modified by another user. Please refresh and try again.",
            )
            if hasattr(self, "form_invalid"):
                return self.form_invalid(form)

        # Redirect if specified
        if self.error_redirect_url:
            return redirect(self.error_redirect_url)

        # Default: re-render the page
        # For TemplateView/FormView, render the template directly
        if isinstance(self, TemplateResponseMixin) and hasattr(
            self, "get_template_names"
        ):
            return self.render_to_response(self.get_context_data())

        # Fallback: return a simple response (should not happen in normal flow)
        return HttpResponse(
            "A concurrency conflict occurred. Please refresh and try again."
        )

    def _handle_application_error(
        self, request: HttpRequest, exc: ApplicationError
    ) -> Any:
        """Handle generic ApplicationError."""
        logger.error(
            "ApplicationError in view %s: %s (details: %s)",
            self.__class__.__name__,
            exc.message,
            exc.details,
            exc_info=True,
        )

        if self.show_error_messages:
            messages.error(
                request,
                exc.message or "An error occurred. Please try again later.",
            )

        # For FormView, add error to form
        if hasattr(self, "form_class") and hasattr(self, "get_form"):
            form = self.get_form()
            form.add_error(
                None,
                exc.message or "An error occurred. Please try again later.",
            )
            if hasattr(self, "form_invalid"):
                return self.form_invalid(form)

        # Redirect if specified
        if self.error_redirect_url:
            return redirect(self.error_redirect_url)

        # Default: re-render the page
        # For TemplateView/FormView, render the template directly
        if isinstance(self, TemplateResponseMixin) and hasattr(
            self, "get_template_names"
        ):
            return self.render_to_response(self.get_context_data())

        # Fallback: return a simple response (should not happen in normal flow)
        return HttpResponse("An error occurred. Please try again.")
