"""
This is inversion of control manager of infrastructure.
"""

import functools
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, Hashable, Tuple, TypeVar, Union

from asgiref.sync import iscoroutinefunction
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpRequest
from injector import Binder, Injector, Module

from shared.domain.entities import Entity
from shared.domain.repositories import UnitOfWork
from shared.infrastructure.repositories import DjangoUnitOfWork

T = TypeVar("T", bound=Entity)


__all__ = (
    "get_injector",
    "inject_dependencies",
    "SharedModule",
)

logger = logging.getLogger(__name__)


def get_injector() -> Injector:
    """
    Returns the default injector that all Injector Modules are managed by it.
    """

    try:
        django_injector = apps.get_app_config("shared_infrastructure")
        return getattr(django_injector, "injector")
    except:
        raise ImproperlyConfigured(
            "shared.infrastructure is not installed or loaded yet"
        )


@functools.lru_cache(maxsize=512)
def get_function_signature(func: Callable) -> inspect.Signature:
    return inspect.signature(func)


def inject_dependencies():
    """
    Decorator for automatic dependency injection.

    Usage:
        @inject_dependencies()
        async def my_method(self, request, user_service: UserService):
            return user_service.get_data()

    Supports both sync and async functions.
    you can also use it on __init__ method of classes.
    """

    def decorator(func: Callable) -> Union[Callable, Awaitable]:
        @functools.wraps(func)
        def sync_wrapper(*args: Tuple[Any], **kwargs: Dict[Hashable, Any]):
            # Get function signature
            sig = get_function_signature(func)
            # injector instance
            injector = get_injector()
            # For each parameter, if not provided in kwargs, try to get from injector
            for name, param in sig.parameters.items():
                if (
                    name not in kwargs
                    and param.annotation != inspect.Parameter.empty
                    and param.annotation not in (HttpRequest, ASGIRequest)
                    and name != "self"
                ):
                    try:
                        kwargs[name] = injector.get(param.annotation)
                    except Exception as e:
                        # If injector can't provide, just skip
                        logger.debug(
                            f"there is no provider for {param.annotation}: {e}"
                        )

            return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Tuple[Any], **kwargs: Dict[Hashable, Any]):
            # read_and_store_bindings(func, get_bindings(func))
            # Get function signature
            sig = inspect.signature(func)
            # injector instance
            injector = get_injector()
            # For each parameter, if not provided in kwargs, try to get from injector
            for name, param in sig.parameters.items():
                if (
                    name not in kwargs
                    and param.annotation != inspect.Parameter.empty
                    and name != "self"
                ):
                    try:
                        kwargs[name] = injector.get(param.annotation)
                    except Exception as e:
                        # If injector can't provide, just skip
                        logger.debug(
                            f"there is no provider for {param.annotation}: {e}"
                        )

            return await func(*args, **kwargs)

        # Check if the function is async
        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class SharedModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UnitOfWork, DjangoUnitOfWork)
