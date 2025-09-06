import inspect
import os
from importlib import import_module

import injector as django_injector_module
from django.apps import AppConfig, apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.utils.module_manager import *


class SharedInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.infrastructure"
    label = "shared_infrastructure"
    verbose_name = _("Shared infrastrucutre")
    shared_modules_to_load = ()

    def ready(self) -> None:
        # for managing injection, we should get injector instance of django_injector app.
        # this instance is in django_injector app instance
        django_injector = apps.get_app_config("django_injector")
        injector = getattr(django_injector, "injector")

        # modules that should be load for all installed_apps.
        # you can define a class attribute named shared_modules_to_load to load them in all installed apps.
        shared_modules_to_load = getattr(
            SharedInfrastructureConfig, "shared_modules_to_load", ()
        )

        # create base migration history folder in the project root directory
        ModuleNode(
            name=settings.MIGRATIONS_HISTORY_PATH,
        ).render()

        for _, config in apps.app_configs.items():
            if not any(filter(lambda a: a == config.name, settings.LOCAL_APPS)):
                continue

            django_app_dot_location = ".".join(config.__module__.split(".")[:-1])

            # manage initial load python modules
            # each django app has a config file and each config file can have
            # a variable named initial_loading_modules that contains a string/list/tuple of all
            # python modules that should be loaded after ready() method
            if hasattr(config, "initial_loading_modules"):
                initial_loading_modules = getattr(config, "initial_loading_modules")

                if isinstance(initial_loading_modules, str):
                    load_module(f"{django_app_dot_location}.{initial_loading_modules}")
                elif isinstance(initial_loading_modules, (list, tuple)):
                    for py_module in initial_loading_modules:
                        load_module(f"{django_app_dot_location}.{py_module}")

            # load all initial load python modules that are shared between all installed apps.
            for module in shared_modules_to_load:
                load_module(f"{django_app_dot_location}.{module}")

            # manage all Injector Module classes to handle dependency injection.
            # each django app can have a python module named ioc.py that contains all Injector Modules.
            # this section installs all Modules in global django_injector injector instance.
            try:
                module = import_module(f"{django_app_dot_location}.ioc")

                for _, klass in inspect.getmembers(
                    module,
                    lambda a: inspect.isclass(a)
                    and issubclass(a, django_injector_module.Module),
                ):
                    # install found class to injector
                    injector.binder.install(klass)
            except ImportError as e:
                pass

            # handle locale folder for each django app.
            # a folder with name 'locale' should be created in each django app directory.
            # after creating locale folder, we should config that path in LOCALE_PATHS.
            ModuleNode(
                name="locale",
                parent_dir=django_app_dot_location.split(".")[0],
            ).render()

            settings.LOCALE_PATHS.append(
                os.path.join(
                    settings.BASE_DIR, *django_app_dot_location.split(".")[0], "locale"
                )
            )

            # to manage migration histories, we should create a direcotry for app in migration history folder.
            # then we can configure it with settings.MIGRATION_HISTORY_PATH settings.
            ModuleNode(
                name=config.label,
                parent_dir=settings.MIGRATIONS_HISTORY_PATH,
                children=[ModuleNode("__init__.py", content="")],
            ).render()

            settings.MIGRATION_MODULES[config.label] = (
                f"{settings.MIGRATIONS_HISTORY_PATH}.{config.label}"
            )
