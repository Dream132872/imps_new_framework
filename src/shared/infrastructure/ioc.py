"""
This is inversion of control manager of infrastructure.
"""

from injector import Injector
from django.apps import apps


def get_injector() -> Injector:
    """
    Returns the default injector that all Injector Modules are managed by it.
    """

    django_injector = apps.get_app_config("django_injector")
    return getattr(django_injector, "injector")
