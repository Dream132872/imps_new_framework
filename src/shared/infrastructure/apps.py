from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharedInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.infrastructure"
    label = "shared_infrastructure"
    verbose_name = _("Shared infrastrucutre")
