from socket import inet_pton
from django.apps import AppConfig, apps
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from injector import Module

from core.infrastructure.ioc import UserModule
from shared.utils.apps_manager import *
from importlib import import_module
import inspect


class SharedInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.infrastructure"
    label = "shared_infrastructure"
    verbose_name = _("Shared infrastrucutre")

    def ready(self) -> None:
        django_injector = apps.get_app_config("django_injector")
        injector = getattr(django_injector, "injector")

        # iterate over all installed apps
        for label, config in apps.app_configs.items():
            django_app_dot_location = ".".join(config.__module__.split(".")[:-1])

            # manage initial load python modules
            if any(filter(lambda a: a == config.name, settings.LOCAL_APPS)):
                if hasattr(config, "initial_loading_modules"):
                    initial_loading_modules = getattr(config, "initial_loading_modules")

                    if isinstance(initial_loading_modules, str):
                        load_module(
                            f"{django_app_dot_location}.{initial_loading_modules}"
                        )
                    elif isinstance(initial_loading_modules, (list, tuple)):
                        for mod in initial_loading_modules:
                            load_module(f"{django_app_dot_location}.{mod}")

            # manage all Injector Module classes to handle dependency injection
            try:
                module = import_module(f"{django_app_dot_location}.ioc")

                for name, klass in inspect.getmembers(
                    module, lambda a: inspect.isclass(a) and issubclass(a, Module)
                ):
                    injector.binder.install(klass)

            except ImportError as e:
                pass
