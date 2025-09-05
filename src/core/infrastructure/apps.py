from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.infrastructure"
    label = "core_infrastructure"
    verbose_name = _("Core")
