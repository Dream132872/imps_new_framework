"""Test attachment mapper"""

import uuid
from datetime import datetime
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.infrastructure.mappers import AttachmentMapper
from media.infrastructure.models import Attachment as AttachmentModel
from shared.domain.entities import FileField, FileFieldType


@pytest.mark.infrastructure
@pytest.mark.unit
class TestAttachmentMapper:
    """Test AttachmentMapper"""

    def test_entity_to_model_with_valid_attachment_entity(
        self,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test converting attachment entity to model"""

        # Act
        result = AttachmentMapper.entity_to_model(sample_attachment_entity)

        # Assert
        assert isinstance(result, AttachmentModel)
        assert result.id == sample_attachment_entity.id
        assert result.created_at == sample_attachment_entity.created_at
        assert result.updated_at == sample_attachment_entity.updated_at
        assert result.file == sample_attachment_entity.file.name
        assert result.title == sample_attachment_entity.title
        assert result.attachment_type == sample_attachment_entity.attachment_type
        assert result.content_type_id == sample_attachment_entity.content_type_id
        assert result.object_id == sample_attachment_entity.object_id

    def test_entity_to_model_with_different_attachment_types(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test converting entity to model with different attachment types"""

        # Arrange
        document_attachment = attachment_entity_factory(attachment_type="document")
        contract_attachment = attachment_entity_factory(attachment_type="contract")
        invoice_attachment = attachment_entity_factory(attachment_type="invoice")

        # Act
        document_model = AttachmentMapper.entity_to_model(document_attachment)
        contract_model = AttachmentMapper.entity_to_model(contract_attachment)
        invoice_model = AttachmentMapper.entity_to_model(invoice_attachment)

        # Assert
        assert document_model.attachment_type == "document"
        assert contract_model.attachment_type == "contract"
        assert invoice_model.attachment_type == "invoice"

    def test_entity_to_model_preserves_all_fields(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        sample_content_type: ContentType
    ) -> None:
        """Test that entity_to_model preserves all entity fields"""

        # Arrange
        attachment_id = str(uuid.uuid4())
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        file_name = "custom_file.pdf"
        title = "Custom Title"
        attachment_type = "document"
        content_type_id = sample_content_type.id
        object_id = str(uuid.uuid4())

        file_field = FileField(
            file_type=FileFieldType.FILE,
            name=file_name,
            path=f"/media/{file_name}",
            url=f"/media/{file_name}",
            size=4096,
            content_type="application/pdf",
        )

        entity = attachment_entity_factory(
            attachment_id=attachment_id,
            file=file_field,
            title=title,
            attachment_type=attachment_type,
            object_id=object_id,
        )
        entity._created_at = created_at
        entity._updated_at = updated_at

        # Act
        model = AttachmentMapper.entity_to_model(entity)

        # Assert
        assert model.id == attachment_id
        assert model.created_at == created_at
        assert model.updated_at == updated_at
        assert model.file == file_name
        assert model.title == title
        assert model.attachment_type == attachment_type
        assert model.content_type_id == content_type_id
        assert model.object_id == object_id

    def test_model_to_entity_with_valid_attachment_model(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test converting attachment model to entity"""

        # Arrange
        model = AttachmentModel(
            file=sample_attachment_file,
            title="Test Attachment",
            attachment_type="document",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        model.save()

        # Act
        result = AttachmentMapper.model_to_entity(model)

        # Assert
        assert isinstance(result, AttachmentEntity)
        assert result.id == str(model.id)
        assert result.created_at == model.created_at
        assert result.updated_at == model.updated_at
        assert isinstance(result.file, FileField)
        assert result.file.name == model.file.name
        assert result.title == model.title
        assert result.attachment_type == model.attachment_type
        assert result.content_type_id == model.content_type_id
        assert result.object_id == model.object_id

    def test_model_to_entity_with_different_attachment_types(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test converting model to entity with different attachment types"""

        # Arrange
        document_model = AttachmentModel(
            file=sample_attachment_file,
            attachment_type="document",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        document_model.save()

        contract_model = AttachmentModel(
            file=sample_attachment_file,
            attachment_type="contract",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        contract_model.save()

        # Act
        document_entity = AttachmentMapper.model_to_entity(document_model)
        contract_entity = AttachmentMapper.model_to_entity(contract_model)

        # Assert
        assert document_entity.attachment_type == "document"
        assert contract_entity.attachment_type == "contract"

    def test_model_to_entity_preserves_all_fields(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test that model_to_entity preserves all model fields"""

        # Arrange
        title = "Model Title"
        attachment_type = "invoice"
        object_id = str(uuid.uuid4())

        model = AttachmentModel(
            file=sample_attachment_file,
            title=title,
            attachment_type=attachment_type,
            content_type=sample_content_type,
            object_id=object_id,
        )
        model.save()

        # Act
        entity = AttachmentMapper.model_to_entity(model)

        # Assert
        assert entity.id == str(model.id)
        assert entity.created_at == model.created_at
        assert entity.updated_at == model.updated_at
        assert entity.title == title
        assert entity.attachment_type == attachment_type
        assert entity.content_type_id == sample_content_type.id
        assert entity.object_id == object_id
        assert isinstance(entity.file, FileField)
        assert entity.file.file_type == FileFieldType.FILE

    def test_round_trip_conversion(
        self,
        sample_attachment_entity: AttachmentEntity,
        db: None,
    ) -> None:
        """Test round-trip conversion: entity -> model -> entity"""

        # Arrange
        original_entity = sample_attachment_entity

        # Act
        model = AttachmentMapper.entity_to_model(original_entity)
        # Save model to get proper file field
        model.save()
        converted_entity = AttachmentMapper.model_to_entity(model)

        # Assert
        assert converted_entity.id == original_entity.id
        assert converted_entity.title == original_entity.title
        assert converted_entity.attachment_type == original_entity.attachment_type
        assert converted_entity.content_type_id == original_entity.content_type_id
        assert converted_entity.object_id == original_entity.object_id
        # Note: created_at and updated_at might differ slightly due to save operation

    def test_entity_to_model_with_none_values(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test entity_to_model handles None/empty values correctly"""

        # Arrange
        entity = attachment_entity_factory(
            title="",
        )

        # Act
        model = AttachmentMapper.entity_to_model(entity)

        # Assert
        assert model.title == ""

    def test_model_to_entity_with_none_values(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test model_to_entity handles None/empty values correctly"""

        # Arrange
        model = AttachmentModel(
            file=sample_attachment_file,
            title="",
            attachment_type="document",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        model.save()

        # Act
        entity = AttachmentMapper.model_to_entity(model)

        # Assert
        assert entity.title == ""

    def test_entity_to_model_with_different_object_id_types(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test entity_to_model handles different object_id types"""

        # Arrange
        string_object_id = str(uuid.uuid4())
        int_object_id = 12345

        entity_string = attachment_entity_factory(object_id=string_object_id)
        entity_int = attachment_entity_factory(object_id=int_object_id)

        # Act
        model_string = AttachmentMapper.entity_to_model(entity_string)
        model_int = AttachmentMapper.entity_to_model(entity_int)

        # Assert
        assert model_string.object_id == string_object_id
        assert model_int.object_id == int_object_id

    def test_model_to_entity_with_different_object_id_types(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test model_to_entity handles different object_id types"""

        # Arrange
        string_object_id = str(uuid.uuid4())
        int_object_id = "12345"

        model_string = AttachmentModel(
            file=sample_attachment_file,
            attachment_type="document",
            content_type=sample_content_type,
            object_id=string_object_id,
        )
        model_string.save()

        model_int = AttachmentModel(
            file=sample_attachment_file,
            attachment_type="document",
            content_type=sample_content_type,
            object_id=int_object_id,
        )
        model_int.save()

        # Act
        entity_string = AttachmentMapper.model_to_entity(model_string)
        entity_int = AttachmentMapper.model_to_entity(model_int)

        # Assert
        assert entity_string.object_id == string_object_id
        assert entity_int.object_id == int_object_id

    def test_entity_to_model_file_name_extraction(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that entity_to_model correctly extracts file name from FileField"""

        # Arrange
        file_name = "test_document.pdf"
        file_field = FileField(
            file_type=FileFieldType.FILE,
            name=file_name,
            path=f"/media/{file_name}",
            url=f"/media/{file_name}",
            size=1024,
            content_type="application/pdf",
        )

        entity = attachment_entity_factory(file=file_field)

        # Act
        model = AttachmentMapper.entity_to_model(entity)

        # Assert
        assert model.file == file_name

    def test_model_to_entity_file_field_creation(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test that model_to_entity correctly creates FileField from model file"""

        # Arrange
        model = AttachmentModel(
            file=sample_attachment_file,
            attachment_type="document",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        model.save()

        # Act
        entity = AttachmentMapper.model_to_entity(model)

        # Assert
        assert isinstance(entity.file, FileField)
        assert entity.file.file_type == FileFieldType.FILE
        assert entity.file.name == model.file.name
