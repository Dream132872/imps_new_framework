from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "identity.infrastructure"
    label = "identity_infrastructure"
    verbose_name = _("Identity")
    verbose_name = _("Identities")
