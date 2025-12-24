"""Test chunk upload query handlers"""

import uuid
from typing import Callable
from unittest.mock import MagicMock

import pytest

from media.application import queries as chunk_upload_queries
from media.application.query_handlers.chunk_upload_query_handlers import (
    GetChunkUploadStatusQueryHandler,
)
from media.domain.entities.chunk_upload_entities import (
    ChunkUpload as ChunkUploadEntity,
    ChunkUploadStatus,
)
from media.domain.repositories import ChunkUploadRepository
from shared.application.exceptions import ApplicationError


@pytest.mark.application
@pytest.mark.unit
class TestGetChunkUploadStatusQueryHandler:
    """Test getting chunk upload status"""

    def test_get_chunk_upload_status_success(
        self,
        mock_unit_of_work: MagicMock,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test successfully getting chunk upload status"""

        # Arrange
        upload_id = sample_chunk_upload_entity.upload_id
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            sample_chunk_upload_entity
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "upload_id" in result
        assert "filename" in result
        assert "total_size" in result
        assert "uploaded_size" in result
        assert "chunk_count" in result
        assert "status" in result
        assert "progress" in result
        assert "completed" in result

        assert result["upload_id"] == sample_chunk_upload_entity.upload_id
        assert result["filename"] == sample_chunk_upload_entity.filename
        assert result["total_size"] == sample_chunk_upload_entity.total_size
        assert result["uploaded_size"] == sample_chunk_upload_entity.uploaded_size
        assert result["chunk_count"] == sample_chunk_upload_entity.chunk_count
        assert result["status"] == sample_chunk_upload_entity.status

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_with_completed_upload(
        self,
        mock_unit_of_work: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test getting status for completed chunk upload"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 2048

        completed_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.COMPLETED,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            completed_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert result["status"] == ChunkUploadStatus.COMPLETED.value
        assert result["completed"] is True
        assert result["progress"] == 100.0

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_with_partial_upload(
        self,
        mock_unit_of_work: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test getting status for partially uploaded chunk upload"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 1024  # 50% uploaded

        partial_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            partial_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert result["status"] == ChunkUploadStatus.UPLOADING.value
        assert result["completed"] is False
        assert result["progress"] == 50.0
        assert result["uploaded_size"] == uploaded_size
        assert result["total_size"] == total_size

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_when_not_found(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting chunk upload status when chunk upload not found"""

        # Arrange
        upload_id = str(uuid.uuid4())
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = None

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationError) as exc_info:
            handler.handle(query)

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_when_repository_raises_error(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting chunk upload status when repository raises error"""

        # Arrange
        upload_id = str(uuid.uuid4())
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.side_effect = Exception(
            "Database connection error"
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationError) as exc_info:
            handler.handle(query)

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_with_zero_total_size(
        self,
        mock_unit_of_work: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test getting status when total_size is zero"""

        # Arrange
        upload_id = str(uuid.uuid4())

        zero_size_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=0,
            uploaded_size=0,
            status=ChunkUploadStatus.PENDING,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            zero_size_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert result["progress"] == 0.0
        assert result["total_size"] == 0
        assert result["uploaded_size"] == 0

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )

    def test_get_chunk_upload_status_with_different_statuses(
        self,
        mock_unit_of_work: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test getting status with different chunk upload statuses"""

        # Test PENDING status
        upload_id = str(uuid.uuid4())
        pending_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            status=ChunkUploadStatus.PENDING,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            pending_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        handler = GetChunkUploadStatusQueryHandler(uow=mock_unit_of_work)

        result = handler.handle(query)

        assert result["status"] == ChunkUploadStatus.PENDING.value

        # Test FAILED status
        upload_id = str(uuid.uuid4())
        failed_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            status=ChunkUploadStatus.FAILED,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            failed_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        result = handler.handle(query)

        assert result["status"] == ChunkUploadStatus.FAILED.value

        # Test CANCELLED status
        upload_id = str(uuid.uuid4())
        cancelled_chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            status=ChunkUploadStatus.CANCELLED,
        )

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            cancelled_chunk_upload
        )

        query = chunk_upload_queries.GetChunkUploadStatusQuery(upload_id=upload_id)
        result = handler.handle(query)

        assert result["status"] == ChunkUploadStatus.CANCELLED.value

