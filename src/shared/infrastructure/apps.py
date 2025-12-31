import inspect
import logging
import os
from importlib import import_module

import injector as injector_module
from django.apps import AppConfig, apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.utils.module_manager import *

logger = logging.getLogger(__name__)


class SharedInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.infrastructure"
    label = "shared_infrastructure"
    verbose_name = _("Shared infrastrucutre")
    shared_modules_to_load = (
        "infrastructure.api",
        "application.cqrs_services",
        "application.event_services",
    )
    modules_to_load = ()

    def ready(self) -> None:
        # this is for shared injector instance
        self.injector = injector_module.Injector()

        # modules that should be load for all installed_apps.
        # you can define a class attribute named shared_modules_to_load to load them in all installed apps.
        shared_modules_to_load = getattr(
            SharedInfrastructureConfig, "shared_modules_to_load", ()
        )

        # create base migration history folder in the project root directory
        ModuleNode(
            name=settings.MIGRATIONS_HISTORY_PATH,
        ).render()

        # create locale folder for config folder
        os.makedirs(os.path.join(settings.BASE_DIR, "config", "locale"), exist_ok=True)

        for _, config in apps.app_configs.items():
            if not any(filter(lambda a: a == config.name, settings.LOCAL_APPS)):
                continue

            # dotted path to the installed app.
            django_app_dot_location = ".".join(config.__module__.split(".")[:-1])
            bounded_context_name = django_app_dot_location.split(".")[0]

            # manage initial load python modules.
            # each django app has a config file and each config file can have
            # a variable named initial_loading_modules that contains a string/list/tuple of all
            # python modules that should be loaded after ready() method.
            initial_loading_modules = getattr(config, "initial_loading_modules", [])
            if not isinstance(initial_loading_modules, (list, tuple)):
                raise TypeError(
                    "initial_loading_modules should be of type list or tuple"
                )

            # load all initial load python modules that are shared between all installed apps.
            initial_loading_modules.extend(shared_modules_to_load)

            for py_module in initial_loading_modules:
                print(f"{bounded_context_name}.{py_module}")
                load_module(f"{bounded_context_name}.{py_module}")

            # manage all Injector Module classes to handle dependency injection.
            # each django app can have a python module named ioc.py that contains all Injector Modules.
            # this section installs all Modules in global injector instance.
            try:
                module_dotted_path = import_module(f"{django_app_dot_location}.ioc")

                for _, klass in inspect.getmembers(
                    module_dotted_path,
                    lambda a: inspect.isclass(a)
                    and issubclass(a, injector_module.Module),
                ):
                    # install found class to the injector
                    self.injector.binder.install(klass)
            except Exception as e:
                logger.error(
                    f"Failed to load ioc module for app {django_app_dot_location}: {e}"
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

        # add api router to the urls after loading all api modules
        add_api_urls()


def add_api_urls() -> None:
    """Add api urls to the main urls."""

    from django.conf.urls.i18n import i18n_patterns
    from django.urls import path

    from config.urls import urlpatterns
    from shared.infrastructure.api import api_v1

    urlpatterns += i18n_patterns(
        path("api/v1/", api_v1.urls),
        prefix_default_language=False,
    )
