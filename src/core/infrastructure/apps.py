from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.utils.menu_utils import MenuItem


class InfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.infrastructure"
    label = "core_infrastructure"
    verbose_name = _("Core")
    menu_items = [
        MenuItem(
            name="core:base:home",
            title=_("Dashboard"),
            url=reverse_lazy("core:base:home"),
            icon="bi bi-house",
            display_order=-999999999,
        ),
    ]
