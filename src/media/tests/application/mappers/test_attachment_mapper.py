"""Test attachment mapper"""

import uuid
from datetime import datetime
from typing import Callable

from django.contrib.contenttypes.models import ContentType
import pytest

from media.application.dtos import AttachmentDTO
from media.application.mappers import AttachmentDTOMapper
from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentValidationError
from shared.domain.entities import FileField, FileFieldType


@pytest.mark.application
@pytest.mark.unit
class TestAttachmentDTOMapper:
    """Test AttachmentDTOMapper"""

    def test_to_dto_with_valid_attachment_entity(
        self,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test converting attachment entity to DTO"""

        # Act
        result = AttachmentDTOMapper.to_dto(sample_attachment_entity)

        # Assert
        assert isinstance(result, AttachmentDTO)
        assert str(result.id) == sample_attachment_entity.id
        assert result.attachment_type == sample_attachment_entity.attachment_type
        assert result.title == sample_attachment_entity.title
        assert result.content_type_id == sample_attachment_entity.content_type_id
        assert result.object_id == sample_attachment_entity.object_id
        assert result.created_at == sample_attachment_entity.created_at
        assert result.updated_at == sample_attachment_entity.updated_at

        # Verify file field mapping
        assert result.file is not None
        assert result.file.name == sample_attachment_entity.file.name
        assert result.file.url == sample_attachment_entity.file.url
        assert result.file.size == sample_attachment_entity.file.size
        assert result.file.content_type == sample_attachment_entity.file.content_type
        assert result.file.file_type == FileFieldType.FILE.value
        # File fields don't have width/height
        assert result.file.width is None
        assert result.file.height is None

    def test_to_dto_with_different_attachment_types(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test converting attachment entity with different attachment types"""

        # Test document type
        document_attachment = attachment_entity_factory(attachment_type="document")
        result = AttachmentDTOMapper.to_dto(document_attachment)
        assert result.attachment_type == "document"

        # Test image type
        image_attachment = attachment_entity_factory(attachment_type="image")
        result = AttachmentDTOMapper.to_dto(image_attachment)
        assert result.attachment_type == "image"

        # Test video type
        video_attachment = attachment_entity_factory(attachment_type="video")
        result = AttachmentDTOMapper.to_dto(video_attachment)
        assert result.attachment_type == "video"

        # Test other type
        other_attachment = attachment_entity_factory(attachment_type="other")
        result = AttachmentDTOMapper.to_dto(other_attachment)
        assert result.attachment_type == "other"

    def test_to_dto_with_empty_title(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test converting attachment entity with empty title"""

        # Arrange
        attachment = attachment_entity_factory(title="")

        # Act
        result = AttachmentDTOMapper.to_dto(attachment)

        # Assert
        assert result.title == ""

    def test_to_dto_with_none_file_properties(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test converting attachment entity with None file properties"""

        # Arrange
        file_field = attachment_file_field_factory(
            file_size=0,
            file_content_type=None,
        )
        with pytest.raises(AttachmentValidationError) as e:
            attachment = attachment_entity_factory(file=file_field)

        # # Act
        # result = AttachmentDTOMapper.to_dto(attachment)

        # # Assert
        # assert result.file is not None
        # assert result.file.size is None
        # assert result.file.content_type is None
        # assert result.file.width is None
        # assert result.file.height is None

    def test_to_dto_preserves_timestamps(
        self,
        sample_attachment_file_field: FileField,
        sample_content_type: ContentType,
    ) -> None:
        """Test that timestamps are preserved correctly"""

        # Arrange
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)

        attachment = AttachmentEntity(
            id=str(uuid.uuid4()),
            file=sample_attachment_file_field,
            attachment_type="document",
            content_type_id=sample_content_type.id,
            object_id=str(uuid.uuid4()),
            title="Test",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        result = AttachmentDTOMapper.to_dto(attachment)

        # Assert
        assert result.created_at == created_at
        assert result.updated_at == updated_at

    def test_list_to_dto_with_empty_list(
        self,
    ) -> None:
        """Test converting empty list of attachment entities"""

        # Act
        result = AttachmentDTOMapper.list_to_dto([])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_to_dto_with_single_attachment(
        self,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test converting single attachment entity in list"""

        # Act
        result = AttachmentDTOMapper.list_to_dto([sample_attachment_entity])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], AttachmentDTO)
        assert str(result[0].id) == sample_attachment_entity.id

    def test_list_to_dto_with_multiple_attachments(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test converting multiple attachment entities"""

        # Arrange
        attachment1 = attachment_entity_factory(title="Attachment 1")
        attachment2 = attachment_entity_factory(title="Attachment 2")
        attachment3 = attachment_entity_factory(title="Attachment 3")

        # Act
        result = AttachmentDTOMapper.list_to_dto(
            [attachment1, attachment2, attachment3]
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0].title == "Attachment 1"
        assert result[1].title == "Attachment 2"
        assert result[2].title == "Attachment 3"
        assert all(isinstance(dto, AttachmentDTO) for dto in result)

    def test_list_to_dto_preserves_order(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that list_to_dto preserves the order of entities"""

        # Arrange
        attachments = [
            attachment_entity_factory(title=f"Attachment {i}") for i in range(5)
        ]

        # Act
        result = AttachmentDTOMapper.list_to_dto(attachments)

        # Assert
        assert len(result) == 5
        for i, dto in enumerate(result):
            assert dto.title == f"Attachment {i}"

    def test_to_dto_with_different_object_id_types(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test converting attachment entity with different object_id types"""

        # Test with string object_id
        attachment_str = attachment_entity_factory(object_id="string-id")
        result_str = AttachmentDTOMapper.to_dto(attachment_str)
        assert result_str.object_id == "string-id"

        # Test with integer object_id
        attachment_int = attachment_entity_factory(object_id=12345)
        result_int = AttachmentDTOMapper.to_dto(attachment_int)
        assert result_int.object_id == 12345

    def test_to_dto_with_large_file_size(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test converting attachment entity with large file size"""

        # Arrange
        file_field = attachment_file_field_factory(
            file_size=100000000,  # 100MB
        )
        attachment = attachment_entity_factory(file=file_field)

        # Act
        result = AttachmentDTOMapper.to_dto(attachment)

        # Assert
        assert result.file.size == 100000000

    def test_to_dto_with_different_content_types(
        self,
        attachment_entity_factory: Callable[..., AttachmentEntity],
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test converting attachment entity with different file content types"""

        # Test PDF
        pdf_file = attachment_file_field_factory(
            file_content_type="application/pdf",
            file_name="document.pdf",
        )
        pdf_attachment = attachment_entity_factory(file=pdf_file)
        result = AttachmentDTOMapper.to_dto(pdf_attachment)
        assert result.file.content_type == "application/pdf"
        assert result.file.name == "document.pdf"

        # Test ZIP
        zip_file = attachment_file_field_factory(
            file_content_type="application/zip",
            file_name="archive.zip",
        )
        zip_attachment = attachment_entity_factory(file=zip_file)
        result = AttachmentDTOMapper.to_dto(zip_attachment)
        assert result.file.content_type == "application/zip"
        assert result.file.name == "archive.zip"

        # Test RAR
        rar_file = attachment_file_field_factory(
            file_content_type="application/x-rar-compressed",
            file_name="archive.rar",
        )
        rar_attachment = attachment_entity_factory(file=rar_file)
        result = AttachmentDTOMapper.to_dto(rar_attachment)
        assert result.file.content_type == "application/x-rar-compressed"
        assert result.file.name == "archive.rar"

    def test_to_dto_file_field_has_correct_file_type(
        self,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test that file field in DTO has correct file_type"""

        # Act
        result = AttachmentDTOMapper.to_dto(sample_attachment_entity)

        # Assert
        assert result.file.file_type == FileFieldType.FILE.value
        assert result.file.file_type != FileFieldType.IMAGE.value
