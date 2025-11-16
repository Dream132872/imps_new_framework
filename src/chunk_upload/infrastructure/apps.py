from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chunk_upload.infrastructure"
    label = "chunk_upload_infrastructure"
    verbose_name = _("Chunk upload")
