"""Test attachment entity"""

import uuid
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentValidationError
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
            attachment_type="document",
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

    def test_attachment_creation_with_optional_fields(
        self, sample_attachment_file_field: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating attachment entity with optional fields"""

        # Arrange
        object_id = str(uuid.uuid4())
        attachment_title = "Title of the attachment"

        # Act
        attachment = AttachmentEntity(
            file=sample_attachment_file_field,
            content_type_id=sample_content_type.id,
            object_id=object_id,
            attachment_type="document",
            title=attachment_title,
        )

        # Assert
        assert (
            attachment.title == attachment_title
        ), f"Title of the generated attachment should be '{attachment_title}'"

    def test_custom_id_for_attachment(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test creating attachment with custom id"""

        # Arrange
        attachment_id = str(uuid.uuid4())

        # Act
        attachment = attachment_entity_factory(attachment_id=attachment_id)

        # Assert
        assert (
            attachment.id == attachment_id
        ), f"attachment.id should be equal to {attachment_id}"

    def test_create_attachment_with_invalid_file(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test raise error for creating attachment with invalid file."""

        # Arrange
        invalid_file = "invalid file"

        # Assert
        with pytest.raises(AttachmentValidationError) as e:
            attachment_entity_factory(file=invalid_file)

    def test_create_attachment_with_invalid_type(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test raise error for creating attachment with invalid type"""

        # Arrange
        invalid_attachment_type = ""

        # Assert
        with pytest.raises(AttachmentValidationError) as e:
            attachment_entity_factory(attachment_type=invalid_attachment_type)

    def test_update_attachment_file(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        attachment_file_field_factory: Callable[..., FileField],
    ):
        """Test updating attachment file with new one"""

        # Arrange
        attachment = attachment_entity_factory()
        original_updated_at = attachment.updated_at
        new_file = attachment_file_field_factory(file_name="new_file.rar", size=5540)

        # Act
        attachment.update_file(new_file)

        # Assert
        assert (
            attachment.file == new_file
        ), "attachment.file should be equal to new_file value"
        assert (
            attachment.updated_at > original_updated_at
        ), "attachment.updated_at should be greater than original_updated_at"

    def test_update_attachment_file_with_invalid_data(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test updating attachment file with invalid data"""

        # Arrange
        attachment = attachment_entity_factory()
        new_file = {"data": "this is data"}

        # Assert
        with pytest.raises(AttachmentValidationError) as e:
            attachment.update_file(new_file)  # type: ignore

    def test_update_attachment_information_with_title(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test updating attachment information with title"""

        # Arrange
        attachment = attachment_entity_factory()
        new_title = "New title"
        original_updated_at = attachment.updated_at

        # Act
        attachment.update_information(title=new_title)

        # Assert
        assert (
            attachment.title == new_title
        ), f"attachment.title should be equalt to '{new_title}'"
        assert (
            attachment.updated_at > original_updated_at
        ), "attachment.updated_at should be greater than original_updated_at value"

    def test_string_representation_of_attachment(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test string representation of attachment."""

        # Arrange
        attachment = attachment_entity_factory()

        # Assert
        assert (
            str(attachment) == attachment.file.name
        ), "str(attachment) should be equal to attachment.file.name"

    def test_repr_representation_of_attachment(
        self, sample_attachment_entity: AttachmentEntity
    ):
        """Test repr representation of the attachment"""
        # Arrange
        representation = repr(sample_attachment_entity)

        # Assert
        assert (
            "<AttachmentEntity" in representation
        ), "repr should have '<AttachmentEntity' start tag"

        assert (
            sample_attachment_entity.id in representation
        ), "representation should have id of attachment"

    def test_attachment_to_dict(
        self, sample_attachment_entity: AttachmentEntity
    ) -> None:
        """Test converting attachment to dictionary"""

        # Arrange
        dict_value = sample_attachment_entity.to_dict()

        # Assert
        assert "file" in dict_value, "file should be in dict_value"
        assert "title" in dict_value, "title should be in dict_value"
        assert (
            "attachment_type" in dict_value
        ), "attachment_type should be in dict_value"
        assert isinstance(dict_value["file"], dict), "file should be a dictionary"

    def test_attachment_equality(
        self, attachment_entity_factory: Callable[..., AttachmentEntity]
    ) -> None:
        """Test equality of two attachments."""

        # Arrange
        attachment_id = str(uuid.uuid4())
        attachment_1 = attachment_entity_factory(attachment_id=attachment_id)
        attachment_2 = attachment_entity_factory(attachment_id=attachment_id)
        attachment_3 = attachment_entity_factory()

        # Assert
        assert (
            attachment_1 == attachment_2
        ), "attachment_1 should be equal to attachment_2 because same ID"
        assert (
            attachment_1 != attachment_3
        ), "attachment_1 should not be equal to attachment_3"
