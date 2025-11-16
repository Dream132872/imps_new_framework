"""
Chunk upload model for handling chunked file uploads.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.models import BaseModel

__all__ = ("ChunkUpload",)


class ChunkUpload(BaseModel):
    """Model for tracking chunked file uploads."""

    upload_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Upload ID"),
        help_text=_("Unique identifier for this upload session"),
    )
    filename = models.CharField(
        max_length=255,
        verbose_name=_("Filename"),
        help_text=_("Original filename"),
    )
    total_size = models.BigIntegerField(
        verbose_name=_("Total Size"),
        help_text=_("Total file size in bytes"),
    )
    uploaded_size = models.BigIntegerField(
        default=0,
        verbose_name=_("Uploaded Size"),
        help_text=_("Total bytes uploaded so far"),
    )
    chunk_count = models.IntegerField(
        default=0,
        verbose_name=_("Chunk Count"),
        help_text=_("Number of chunks uploaded"),
    )
    temp_file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Temporary File Path"),
        help_text=_("Path to the temporary file being assembled"),
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", _("Pending")),
            ("uploading", _("Uploading")),
            ("completed", _("Completed")),
            ("failed", _("Failed")),
        ],
        default="pending",
        verbose_name=_("Status"),
    )

    class Meta:
        db_table = "chunk_uploads"
        verbose_name = _("Chunk Upload")
        verbose_name_plural = _("Chunk Uploads")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["upload_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"ChunkUpload {self.upload_id} - {self.filename}"
