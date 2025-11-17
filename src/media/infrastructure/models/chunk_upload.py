"""
Chunk upload model for handling chunked file uploads.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from media.infrastructure.models.managers import ChunkUploadManager
from shared.infrastructure.models import BaseModel

__all__ = ("ChunkUpload",)


class ChunkUpload(BaseModel):
    """Model for tracking chunked file uploads."""

    # unique upload id
    upload_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Upload ID"),
        help_text=_("Unique identifier for this upload session"),
    )

    # the original file name of the chunk upload file
    filename = models.CharField(
        max_length=255,
        verbose_name=_("Filename"),
        help_text=_("Original filename"),
    )

    # total size of the uploaded file
    total_size = models.BigIntegerField(
        verbose_name=_("Total Size"),
        help_text=_("Total file size in bytes"),
    )

    # single chunk upload size
    uploaded_size = models.BigIntegerField(
        default=0,
        verbose_name=_("Uploaded Size"),
        help_text=_("Total bytes uploaded so far"),
    )

    # total number of chunks for uploaded file
    chunk_count = models.IntegerField(
        default=0,
        verbose_name=_("Chunk Count"),
        help_text=_("Number of chunks uploaded"),
    )

    # temporary file path of the file
    temp_file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Temporary File Path"),
        help_text=_("Path to the temporary file being assembled"),
    )

    # state of the uploaded file
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

    # default manager of the model
    objects = ChunkUploadManager()

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
        """Unicode representation of the chunk upload."""
        return f"ChunkUpload {self.upload_id} - {self.filename}"

    def __repr__(self) -> str:
        """Debug representation of the chunk upload."""
        return f"<ChunkUpload pk={self.id} file_name={self.filename} total_size={self.total_size} uploaded_size={self.uploaded_size} chunk_count={self.chunk_count} />"
