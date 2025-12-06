"""Test attachment entity"""

import uuid

import pytest
from django.contrib.contenttypes.models import ContentType

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from shared.domain.entities import FileField


@pytest.mark.unit
@pytest.mark.domain
class TestAttachmentEntity:
    """Test suite for attachment entity."""

    def test_attachment_creation_with_required_fields(
        self, sample_attachment_file_field: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating attachment entity with required fields"""
        # Arrange
        object_id = str(uuid.uuid4())

        # Act
        attachment = AttachmentEntity(
            file=sample_attachment_file_field,
            content_type_id=sample_content_type.id,
            object_id=object_id,
        )

        # Assert
        assert attachment.id is not None, "Id should be created automatically"
        assert (
            attachment.object_id == object_id
        ), "attachment.object_id should be equal to object_id"
        assert attachment.created_at is not None, "created_at should not be None"
        assert attachment.updated_at is not None, "updated_at should not be None"
        assert (
            attachment.file == sample_attachment_file_field
        ), "file of the attachment should be equal to sample_attachment_file_field"
        assert (
            attachment.content_type_id == sample_content_type.id
        ), "content_type_id of attachment should be equal to sample_content_type.id"
        assert attachment.title == "", "title of the attachment should be ''"
