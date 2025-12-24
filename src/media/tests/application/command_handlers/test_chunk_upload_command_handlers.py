"""Test chunk upload command handlers"""

import uuid
from io import BytesIO
from typing import Callable
from unittest.mock import MagicMock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from media.application import commands as chunk_upload_commands
from media.application.command_handlers import (
    CompleteChunkUploadCommandHandler,
    CreateChunkUploadCommandHandler,
    UploadChunkCommandHandler,
)
from media.domain.entities.chunk_upload_entities import (
    ChunkUpload as ChunkUploadEntity,
    ChunkUploadStatus,
)
from media.domain.exceptions import (
    ChunkUploadNotFoundError,
    ChunkUploadValidationError,
)
from media.domain.repositories import ChunkUploadRepository
from media.domain.services import ChunkUploadService
from shared.application.exceptions import ApplicationError, ApplicationValidationError


@pytest.fixture
def mock_chunk_upload_service() -> MagicMock:
    """Creates a MagicMock object of chunk upload service"""

    return MagicMock(spec=ChunkUploadService)


@pytest.mark.application
@pytest.mark.unit
class TestCreateChunkUploadCommandHandler:
    """Test create chunk upload command handler"""

    def test_handle_create_chunk_upload_command_with_valid_data(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test creating chunk upload command"""

        # Arrange
        filename = "test_file.rar"
        total_size = 2048

        command = chunk_upload_commands.CreateChunkUploadCommand(
            filename=filename,
            total_size=total_size,
        )

        saved_chunk_upload = chunk_upload_entity_factory(
            filename=filename,
            total_size=total_size,
            status=ChunkUploadStatus.PENDING,
        )

        mock_unit_of_work[ChunkUploadRepository].save.return_value = saved_chunk_upload

        # Act
        handler = CreateChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        result = handler.handle(command)

        # Assert
        assert result is not None
        assert "upload_id" in result
        assert "offset" in result
        assert result["offset"] == 0
        assert result["upload_id"] == saved_chunk_upload.upload_id

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_handle_create_chunk_upload_raises_validation_error(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
    ) -> None:
        """Test creating chunk upload when validation fails"""

        # Arrange
        command = chunk_upload_commands.CreateChunkUploadCommand(
            filename="test_file.rar",
            total_size=-1,  # Invalid size
        )

        mock_unit_of_work[ChunkUploadRepository].save.side_effect = (
            ChunkUploadValidationError("Invalid total size")
        )

        handler = CreateChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationValidationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_create_chunk_upload_raises_generic_errors(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
    ) -> None:
        """Test creating chunk upload with generic errors"""

        # Arrange
        command = chunk_upload_commands.CreateChunkUploadCommand(
            filename="test_file.rar",
            total_size=2048,
        )

        mock_unit_of_work[ChunkUploadRepository].save.side_effect = Exception(
            "Database error"
        )

        handler = CreateChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_create_chunk_upload_when_service_not_available(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Test creating chunk upload when service is None"""

        # Arrange & Act & Assert - BaseChunkUploadCommandHandler should raise error during initialization
        with pytest.raises(ApplicationError):
            CreateChunkUploadCommandHandler(
                uow=mock_unit_of_work,
                file_storage_service=mock_file_storage_service,
                chunk_upload_service=None,  # type: ignore
            )


@pytest.mark.application
@pytest.mark.unit
class TestUploadChunkCommandHandler:
    """Test upload chunk command handler"""

    def test_handle_upload_chunk_command_with_valid_data(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test uploading chunk command"""

        # Arrange
        chunk_data = b"chunk data content"
        chunk = BytesIO(chunk_data)
        offset = 0
        chunk_size = len(chunk_data)
        uploaded_size = chunk_size

        command = chunk_upload_commands.UploadChunkCommand(
            upload_id=sample_chunk_upload_entity.upload_id,
            chunk=chunk,  # type: ignore
            offset=offset,
            chunk_size=chunk_size,
        )

        mock_chunk_upload_service.append_chunk.return_value = uploaded_size
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            sample_chunk_upload_entity
        )

        handler = UploadChunkCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        result = handler.handle(command)

        # Assert
        assert result is not None
        assert "upload_id" in result
        assert "offset" in result
        assert "progress" in result
        assert "completed" in result
        assert result["upload_id"] == command.upload_id
        assert result["offset"] == uploaded_size

        # Verify method calls
        mock_chunk_upload_service.append_chunk.assert_called_once_with(
            command.upload_id, chunk, offset, chunk_size
        )
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            command.upload_id
        )
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_handle_upload_chunk_when_chunk_upload_not_found(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test uploading chunk when chunk upload not found"""

        # Arrange
        chunk_data = b"chunk data content"
        chunk = BytesIO(chunk_data)

        command = chunk_upload_commands.UploadChunkCommand(
            upload_id=sample_chunk_upload_entity.upload_id,
            chunk=chunk,  # type: ignore
            offset=0,
            chunk_size=len(chunk_data),
        )

        mock_chunk_upload_service.append_chunk.return_value = len(chunk_data)
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.side_effect = (
            ChunkUploadNotFoundError()
        )

        handler = UploadChunkCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_chunk_upload_service.append_chunk.assert_called_once()
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            command.upload_id
        )
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_upload_chunk_when_append_chunk_raises_value_error(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test uploading chunk when append_chunk raises ValueError"""

        # Arrange
        chunk_data = b"chunk data content"
        chunk = BytesIO(chunk_data)

        command = chunk_upload_commands.UploadChunkCommand(
            upload_id=sample_chunk_upload_entity.upload_id,
            chunk=chunk,  # type: ignore
            offset=0,
            chunk_size=len(chunk_data),
        )

        mock_chunk_upload_service.append_chunk.side_effect = ValueError(
            "Invalid offset"
        )

        handler = UploadChunkCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError) as exc_info:
            handler.handle(command)

        assert "Invalid offset" in str(exc_info.value)

        # Assert
        mock_chunk_upload_service.append_chunk.assert_called_once()
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_upload_chunk_raises_generic_errors(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test uploading chunk with generic errors"""

        # Arrange
        chunk_data = b"chunk data content"
        chunk = BytesIO(chunk_data)

        command = chunk_upload_commands.UploadChunkCommand(
            upload_id=sample_chunk_upload_entity.upload_id,
            chunk=chunk,  # type: ignore
            offset=0,
            chunk_size=len(chunk_data),
        )

        mock_chunk_upload_service.append_chunk.side_effect = Exception(
            "Service error"
        )

        handler = UploadChunkCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_chunk_upload_service.append_chunk.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestCompleteChunkUploadCommandHandler:
    """Test complete chunk upload command handler"""

    def test_handle_complete_chunk_upload_command_with_valid_data(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test completing chunk upload command"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 2048  # Fully uploaded

        chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        completed_file = BytesIO(b"completed file content")

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            chunk_upload
        )
        mock_unit_of_work[ChunkUploadRepository].save.return_value = chunk_upload
        mock_chunk_upload_service.get_completed_file.return_value = completed_file

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        result = handler.handle(command)

        # Assert
        assert result is not None
        assert result == completed_file

        # Verify method calls
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_chunk_upload_service.get_completed_file.assert_called_once_with(upload_id)
        mock_chunk_upload_service.cleanup_upload.assert_called_once_with(upload_id)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_handle_complete_chunk_upload_when_not_fully_uploaded(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test completing chunk upload when not fully uploaded"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 1024  # Not fully uploaded

        chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            chunk_upload
        )

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_unit_of_work[ChunkUploadRepository].save.assert_not_called()
        mock_chunk_upload_service.get_completed_file.assert_not_called()
        mock_chunk_upload_service.cleanup_upload.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_complete_chunk_upload_when_chunk_upload_not_found(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
    ) -> None:
        """Test completing chunk upload when chunk upload not found"""

        # Arrange
        upload_id = str(uuid.uuid4())

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.side_effect = (
            ChunkUploadNotFoundError()
        )

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_chunk_upload_service.cleanup_upload.assert_called_once_with(upload_id)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_complete_chunk_upload_when_get_completed_file_fails(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test completing chunk upload when get_completed_file fails"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 2048

        chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            chunk_upload
        )
        mock_unit_of_work[ChunkUploadRepository].save.return_value = chunk_upload
        mock_chunk_upload_service.get_completed_file.side_effect = Exception(
            "File read error"
        )

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_chunk_upload_service.get_completed_file.assert_called_once_with(upload_id)
        # Cleanup should be called even on error
        mock_chunk_upload_service.cleanup_upload.assert_called_once_with(upload_id)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_complete_chunk_upload_when_save_fails(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test completing chunk upload when save fails"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 2048

        chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            chunk_upload
        )
        mock_unit_of_work[ChunkUploadRepository].save.side_effect = Exception(
            "Database error"
        )

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        mock_chunk_upload_service.get_completed_file.assert_not_called()
        # Cleanup should be called even on error
        mock_chunk_upload_service.cleanup_upload.assert_called_once_with(upload_id)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_handle_complete_chunk_upload_when_service_not_available(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Test completing chunk upload when service is None"""

        # Arrange & Act & Assert - BaseChunkUploadCommandHandler should raise error during initialization
        with pytest.raises(ApplicationError):
            CompleteChunkUploadCommandHandler(
                uow=mock_unit_of_work,
                file_storage_service=mock_file_storage_service,
                chunk_upload_service=None,  # type: ignore
            )

    def test_handle_complete_chunk_upload_when_cleanup_fails_during_error(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        mock_chunk_upload_service: MagicMock,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test completing chunk upload when cleanup fails during error handling"""

        # Arrange
        upload_id = str(uuid.uuid4())
        total_size = 2048
        uploaded_size = 2048

        chunk_upload = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=total_size,
            uploaded_size=uploaded_size,
            status=ChunkUploadStatus.UPLOADING,
        )

        command = chunk_upload_commands.CompleteChunkUploadCommand(upload_id=upload_id)

        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.return_value = (
            chunk_upload
        )
        mock_unit_of_work[ChunkUploadRepository].save.side_effect = Exception(
            "Database error"
        )
        # Cleanup also fails
        mock_chunk_upload_service.cleanup_upload.side_effect = Exception(
            "Cleanup error"
        )

        handler = CompleteChunkUploadCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
            chunk_upload_service=mock_chunk_upload_service,
        )

        # Act - Should still raise ApplicationError even if cleanup fails
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[ChunkUploadRepository].get_by_upload_id.assert_called_once_with(
            upload_id
        )
        mock_unit_of_work[ChunkUploadRepository].save.assert_called_once()
        # Cleanup should be attempted
        mock_chunk_upload_service.cleanup_upload.assert_called_once_with(upload_id)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

