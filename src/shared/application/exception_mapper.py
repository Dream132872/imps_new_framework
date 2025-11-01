"""
Exception mapping utility for transforming Domain exceptions to Application exceptions.

This module provides utilities to map domain layer exceptions to appropriate
application layer exceptions, maintaining proper exception hierarchy and context.
"""

from typing import Any

from shared.application.exceptions import (
    ApplicationBusinessRuleViolationError,
    ApplicationConcurrencyError,
    ApplicationError,
    ApplicationInvalidEntityError,
    ApplicationNotFoundError,
    ApplicationValidationError,
)
from shared.domain.exceptions import (
    DomainBusinessRuleViolationError,
    DomainConcurrencyError,
    DomainEntityNotFoundError,
    DomainException,
    DomainInvalidEntityError,
    DomainValidationError,
)

__all__ = ("map_domain_exception_to_application",)


# Mapping dictionary: Domain Exception → Application Exception class
DOMAIN_TO_APPLICATION_EXCEPTION_MAP = {
    DomainEntityNotFoundError: ApplicationNotFoundError,
    DomainValidationError: ApplicationValidationError,
    DomainInvalidEntityError: ApplicationInvalidEntityError,
    DomainBusinessRuleViolationError: ApplicationBusinessRuleViolationError,
    DomainConcurrencyError: ApplicationConcurrencyError,
}


def map_domain_exception_to_application(
    domain_exception: DomainException,
    message: str | None = None,
    details: dict[str, Any] | None = None,
) -> ApplicationError:
    """
    Map a Domain exception to the corresponding Application exception.

    This function automatically determines the correct Application exception type
    based on the Domain exception type, preserving the original exception as the
    cause (using 'from e').

    Mapping rules:
    - DomainEntityNotFoundError → ApplicationNotFoundError
    - DomainValidationError → ApplicationValidationError
    - DomainInvalidEntityError → ApplicationInvalidEntityError
    - DomainBusinessRuleViolationError → ApplicationBusinessRuleViolationError
    - DomainConcurrencyError → ApplicationConcurrencyError
    - Other DomainException → ApplicationError (generic)

    Args:
        domain_exception: The domain exception to map
        message: Optional custom message (defaults to str(domain_exception))
        details: Optional additional details dictionary

    Returns:
        The corresponding Application exception

    Example:
        try:
            # domain operation that might raise PictureNotFoundError
            picture = repository.get_by_id(id)
        except PictureNotFoundError as e:
            # Automatically maps to ApplicationNotFoundError
            raise map_domain_exception_to_application(e) from e

        # Or with custom message:
        except PictureNotFoundError as e:
            raise map_domain_exception_to_application(
                e,
                message="Picture not found",
                details={"picture_id": id}
            ) from e
    """
    # Find the matching Application exception class
    app_exception_class = None

    # Check the exception type and its MRO (Method Resolution Order) to find a match
    for exc_type in type(domain_exception).__mro__:
        if exc_type in DOMAIN_TO_APPLICATION_EXCEPTION_MAP:
            app_exception_class = DOMAIN_TO_APPLICATION_EXCEPTION_MAP[exc_type]
            break

    # Fallback to generic ApplicationError if no specific mapping found
    if app_exception_class is None:
        app_exception_class = ApplicationError

    # Use provided message or exception string representation
    exception_message = message if message is not None else str(domain_exception)

    # Return the mapped Application exception
    return app_exception_class(message=exception_message, details=details or {})
