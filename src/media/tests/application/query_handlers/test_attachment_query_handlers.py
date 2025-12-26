"""Test attachment query handlers"""

import uuid
from typing import Callable
from unittest.mock import MagicMock

import pytest
from django.contrib.contenttypes.models import ContentType

from media.application.dtos import AttachmentDTO
from media.application.queries.attachment_queries import (
    GetAttachmentByIdQuery,
    SearchAttachmentsQuery,
    SearchFirstAttachmentQuery,
)
from media.application.query_handlers.attachment_query_handlers import (
    GetAttachmentByIdQueryHandler,
    SearchAttachmentsQueryHandler,
    SearchFirstAttachmentQueryHandler,
)
from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentNotFoundError
from media.domain.repositories import AttachmentRepository
from shared.application.exceptions import ApplicationError, ApplicationNotFoundError


@pytest.mark.application
@pytest.mark.unit
class TestSearchAttachmentsQueryHandler:
    """Test searching attachments"""

    def test_search_attachments_with_content_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching attachments"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_attachments.return_value = [
            sample_attachment_entity
        ]

        query = SearchAttachmentsQuery(content_type_id=sample_content_type.id)
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert str(result[0].id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            attachment_type="",
        )

    def test_search_attachments_with_all_parameters(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test searching attachments with all query parameters"""

        # Arrange
        object_id = str(uuid.uuid4())
        attachment_type = "image"
        attachment1 = sample_attachment_entity
        attachment2 = attachment_entity_factory(
            object_id=object_id,
            attachment_type=attachment_type,
        )

        mock_unit_of_work[AttachmentRepository].search_attachments.return_value = [
            attachment1,
            attachment2,
        ]

        query = SearchAttachmentsQuery(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            attachment_type=attachment_type,
        )
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 2
        assert str(result[0].id) == attachment1.id
        assert str(result[1].id) == attachment2.id

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=object_id,
            attachment_type=attachment_type,
        )

    def test_search_attachments_returns_empty_list(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching attachments when no results found"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_attachments.return_value = []

        query = SearchAttachmentsQuery(content_type_id=sample_content_type.id)
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 0
        assert isinstance(result, list)

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            attachment_type="",
        )

    def test_search_attachments_with_only_object_id(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test searching attachments with only object_id parameter"""

        # Arrange
        object_id = str(uuid.uuid4())
        mock_unit_of_work[AttachmentRepository].search_attachments.return_value = [
            sample_attachment_entity
        ]

        query = SearchAttachmentsQuery(object_id=object_id)
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert str(result[0].id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once_with(
            content_type=None,
            object_id=object_id,
            attachment_type="",
        )

    def test_search_attachments_with_only_attachment_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test searching attachments with only attachment_type parameter"""

        # Arrange
        attachment_type = "document"
        mock_unit_of_work[AttachmentRepository].search_attachments.return_value = [
            sample_attachment_entity
        ]

        query = SearchAttachmentsQuery(attachment_type=attachment_type)
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert str(result[0].id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once_with(
            content_type=None,
            object_id=None,
            attachment_type=attachment_type,
        )

    def test_search_attachments_when_repository_raises_error(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching attachments when repository raises error"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_attachments.side_effect = Exception(
            "Database error"
        )

        query = SearchAttachmentsQuery(content_type_id=sample_content_type.id)
        handler = SearchAttachmentsQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            handler.handle(query)

        assert "Database error" in str(exc_info.value)

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].search_attachments.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestSearchFirstAttachmentQueryHandler:
    """Test searching first occurrence of attachment"""

    def test_search_first_attachment_with_content_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first attachment with special information"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_first_attachment.return_value = (
            sample_attachment_entity
        )

        query = SearchFirstAttachmentQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            attachment_type="",
        )

    def test_search_first_attachment_with_all_parameters(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first attachment with all query parameters"""

        # Arrange
        object_id = str(uuid.uuid4())
        attachment_type = "document"

        mock_unit_of_work[AttachmentRepository].search_first_attachment.return_value = (
            sample_attachment_entity
        )

        query = SearchFirstAttachmentQuery(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            attachment_type=attachment_type,
        )
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=object_id,
            attachment_type=attachment_type,
        )

    def test_search_first_attachment_returns_none_when_not_found(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first attachment when no attachment found"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_first_attachment.return_value = None

        query = SearchFirstAttachmentQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is None

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            attachment_type="",
        )

    def test_search_first_attachment_with_only_object_id(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test finding first attachment with only object_id parameter"""

        # Arrange
        object_id = str(uuid.uuid4())
        mock_unit_of_work[AttachmentRepository].search_first_attachment.return_value = (
            sample_attachment_entity
        )

        query = SearchFirstAttachmentQuery(object_id=object_id)
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once_with(
            content_type=None,
            object_id=object_id,
            attachment_type="",
        )

    def test_search_first_attachment_with_only_attachment_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test finding first attachment with only attachment_type parameter"""

        # Arrange
        attachment_type = "image"
        mock_unit_of_work[AttachmentRepository].search_first_attachment.return_value = (
            sample_attachment_entity
        )

        query = SearchFirstAttachmentQuery(attachment_type=attachment_type)
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once_with(
            content_type=None,
            object_id=None,
            attachment_type=attachment_type,
        )

    def test_search_first_attachment_when_repository_raises_error(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first attachment when repository raises error"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].search_first_attachment.side_effect = (
            Exception("Database error")
        )

        query = SearchFirstAttachmentQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstAttachmentQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            handler.handle(query)

        assert "Database error" in str(exc_info.value)

        # Verify method calls
        mock_unit_of_work[
            AttachmentRepository
        ].search_first_attachment.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestGetAttachmentByIdQueryHandler:
    """Test getting attachment by ID"""

    def test_get_attachment_by_id_success(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test successfully getting attachment by ID"""

        # Arrange
        attachment_id = sample_attachment_entity.id
        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )

        query = GetAttachmentByIdQuery(attachment_id=attachment_id)
        handler = GetAttachmentByIdQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id
        assert result.title == sample_attachment_entity.title
        assert result.content_type_id == sample_attachment_entity.content_type_id
        assert result.object_id == sample_attachment_entity.object_id
        assert result.attachment_type == sample_attachment_entity.attachment_type

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            attachment_id
        )

    def test_get_attachment_by_id_when_not_found(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting attachment by ID when attachment not found"""

        # Arrange
        attachment_id = str(uuid.uuid4())
        mock_unit_of_work[AttachmentRepository].get_by_id.side_effect = (
            AttachmentNotFoundError()
        )

        query = GetAttachmentByIdQuery(attachment_id=attachment_id)
        handler = GetAttachmentByIdQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(query)

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            attachment_id
        )

    def test_get_attachment_by_id_when_repository_raises_generic_error(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting attachment by ID when repository raises generic error"""

        # Arrange
        attachment_id = str(uuid.uuid4())
        mock_unit_of_work[AttachmentRepository].get_by_id.side_effect = Exception(
            "Database connection error"
        )

        query = GetAttachmentByIdQuery(attachment_id=attachment_id)
        handler = GetAttachmentByIdQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationError) as exc_info:
            handler.handle(query)

        assert attachment_id in str(exc_info.value)

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            attachment_id
        )

    def test_get_attachment_by_id_with_different_id_formats(
        self,
        mock_unit_of_work: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test getting attachment by ID with different ID formats"""

        # Arrange - Test with UUID string
        attachment_id = str(uuid.uuid4())
        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )

        query = GetAttachmentByIdQuery(attachment_id=attachment_id)
        handler = GetAttachmentByIdQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_attachment_entity.id

        # Verify method calls - handler converts attachment_id to string
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            attachment_id
        )

