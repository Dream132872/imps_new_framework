import inspect
from importlib import import_module

import injector as django_injector_module
from django.apps import AppConfig, apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shared.utils.apps_manager import *


class SharedInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.infrastructure"
    label = "shared_infrastructure"
    verbose_name = _("Shared infrastrucutre")

    def ready(self) -> None:
        django_injector = apps.get_app_config("django_injector")
        injector = getattr(django_injector, "injector")

        for label, config in apps.app_configs.items():
            django_app_dot_location = ".".join(config.__module__.split(".")[:-1])

            # manage initial load python modules
            # each django app has a config file and each config file can have
            # a variable named initial_loading_modules that contains a string/list/tuple of all
            # python modules that should be loaded after ready() method
            if any(filter(lambda a: a == config.name, settings.LOCAL_APPS)):
                if hasattr(config, "initial_loading_modules"):
                    initial_loading_modules = getattr(config, "initial_loading_modules")

                    if isinstance(initial_loading_modules, str):
                        load_module(
                            f"{django_app_dot_location}.{initial_loading_modules}"
                        )
                    elif isinstance(initial_loading_modules, (list, tuple)):
                        for py_module in initial_loading_modules:
                            load_module(f"{django_app_dot_location}.{py_module}")

            # manage all Injector Module classes to handle dependency injection.
            # each django app can have a python module named ioc.py that contains all Injector Modules.
            # this section installs all Modules in global django_injector injector instance.
            try:
                module = import_module(f"{django_app_dot_location}.ioc")

                for name, klass in inspect.getmembers(
                    module,
                    lambda a: inspect.isclass(a)
                    and issubclass(a, django_injector_module.Module),
                ):
                    # install found class to injector
                    injector.binder.install(klass)

            except ImportError as e:
                pass
