"""Test attachment command handlers"""

import uuid
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.application.command_handlers import (
    CreateAttachmentCommandHandler,
    DeleteAttachmentCommandHandler,
    UpdateAttachmentCommandHandler,
)
from media.application.commands import (
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentNotFoundError, AttachmentValidationError
from media.domain.repositories import AttachmentRepository
from media.tests.conftest import sample_attachment_entity
from shared.application.exceptions import (
    ApplicationError,
    ApplicationNotFoundError,
    ApplicationValidationError,
)
from shared.domain.entities import FileField


@pytest.mark.application
@pytest.mark.unit
class TestCreateAttachmentCommandHandler:
    """Test create attachment command handler"""

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_command_with_valid_data(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_file_field: FileField,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test creating attachment command"""

        file_path = "attachments/test_file.rar"
        mock_file_storage_service.save_file.return_value = file_path
        mock_from_file_name.return_value = sample_attachment_file_field

        # Arrange
        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=sample_attachment_file,  # type: ignore
            attachment_type="document",
            title="Title of the attachment",
        )

        saved_attachment = attachment_entity_factory(
            attachment_type=command.attachment_type,
            title=command.title,
            object_id=str(command.object_id),
        )

        mock_unit_of_work[AttachmentRepository].save.return_value = saved_attachment

        # Act
        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        result = handler.handle(command)

        # Assert
        assert result is not None
        assert result.id == saved_attachment.id
        assert result.title == command.title
        assert result.content_type_id == command.content_type_id
        assert result.object_id == str(command.object_id)
        assert result.attachment_type == command.attachment_type
        assert result.file is not None
        assert result.file.name == sample_attachment_file_field.name

        # Verify service calls
        mock_file_storage_service.save_file.assert_called_with(sample_attachment_file)
        mock_from_file_name.assert_called_once_with(file_path)

        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_command_with_invalid_file_size_raises_validation_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_content_type: ContentType,
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test validation errors for create attachment command"""

        # Arrange
        file_path = "attachments/test_file.rar"
        sample_file_field = attachment_file_field_factory(
            file_name="test_file.rar",
            file_path=file_path,
            file_url="",
            file_size=0,  # this would generate error
            file_content_type="application/x-rar-compressed",
        )
        mock_from_file_name.return_value = sample_file_field
        mock_file_storage_service.save_file.return_value = file_path

        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            title="Create new attachment",
            file=SimpleUploadedFile(
                name="test_file.rar", content=b"content", content_type="application/x-rar-compressed"
            ),  # type: ignore
            object_id=uuid.uuid4(),
            attachment_type="document",
        )

        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act and Assert
        with pytest.raises(ApplicationValidationError):
            handler.handle(command=command)

        # Verify
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

        # Verify that cleanup method calls
        mock_file_storage_service.delete_file.assert_called_once_with(file_path)
        mock_from_file_name.assert_called_once_with(file_path)

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_raises_error_when_file_is_empty(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test raising error when file is empty"""
        # Arrange

        mock_file_storage_service.save_file.return_value = ""

        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=None,
            attachment_type="document",
            title="",
        )

        # Act
        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Assert
        with pytest.raises(ApplicationValidationError):
            handler.handle(command=command)

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_raises_generic_errors(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_file_field: FileField,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test creating attachment command with generic errors"""

        file_path = "attachments/test_file.rar"

        # Arrange
        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=sample_attachment_file,  # type: ignore
            attachment_type="document",
            title="Title of the attachment",
        )

        mock_file_storage_service.save_file.return_value = file_path
        mock_from_file_name.return_value = sample_attachment_file_field
        mock_unit_of_work[AttachmentRepository].save.side_effect = Exception(
            "Database error"
        )

        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert and verify services calls
        mock_file_storage_service.save_file.assert_called_with(sample_attachment_file)
        mock_from_file_name.assert_called_once_with(file_path)

        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_when_file_field_factory_raises_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
    ) -> None:
        """Test creating attachment when FileFieldFactory raises error"""

        file_path = "attachments/test_file.rar"
        mock_file_storage_service.save_file.return_value = file_path
        mock_from_file_name.side_effect = Exception("FileFieldFactory error")

        # Arrange
        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=sample_attachment_file,  # type: ignore
            attachment_type="document",
            title="Title of the attachment",
        )

        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert
        mock_file_storage_service.save_file.assert_called_with(sample_attachment_file)
        mock_from_file_name.assert_called_once_with(file_path)
        mock_file_storage_service.delete_file.assert_called_once_with("")
        mock_unit_of_work[AttachmentRepository].save.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_when_repository_save_raises_validation_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_file_field: FileField,
        sample_content_type: ContentType,
    ) -> None:
        """Test creating attachment when repository save raises AttachmentValidationError"""

        file_path = "attachments/test_file.rar"
        mock_file_storage_service.save_file.return_value = file_path
        mock_from_file_name.return_value = sample_attachment_file_field
        mock_unit_of_work[AttachmentRepository].save.side_effect = AttachmentValidationError(
            "Invalid attachment data"
        )

        # Arrange
        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=sample_attachment_file,  # type: ignore
            attachment_type="document",
            title="Title of the attachment",
        )

        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act
        with pytest.raises(ApplicationValidationError):
            handler.handle(command)

        # Assert
        mock_file_storage_service.save_file.assert_called_with(sample_attachment_file)
        mock_from_file_name.assert_called_once_with(file_path)
        mock_file_storage_service.delete_file.assert_called_once_with(
            sample_attachment_file_field.path
        )
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_create_attachment_when_save_file_returns_empty_string(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
    ) -> None:
        """Test creating attachment when save_file returns empty string"""

        mock_file_storage_service.save_file.return_value = ""

        # Arrange
        object_id = uuid.uuid4()
        command = CreateAttachmentCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            file=sample_attachment_file,  # type: ignore
            attachment_type="document",
            title="Title of the attachment",
        )

        handler = CreateAttachmentCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act
        with pytest.raises(ApplicationValidationError):
            handler.handle(command)

        # Assert
        mock_file_storage_service.save_file.assert_called_with(sample_attachment_file)
        mock_from_file_name.assert_not_called()
        mock_file_storage_service.delete_file.assert_called_once_with("")
        mock_unit_of_work[AttachmentRepository].save.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestUpdateAttachmentCommandHandler:
    """Test updating attachment command"""

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_command_including_file(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
        attachment_file_field_factory: Callable[..., FileField],
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test updating attachment with valid data"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"
        new_title = "New title for attachment"
        new_attachment_type = "image"
        new_file_field = attachment_file_field_factory(
            file_name=new_file_name,
            file_path="attachments/" + new_file_name,
            file_url="attachments/" + new_file_name,
        )
        original_file_path = sample_attachment_entity.file.path

        updated_attachment = attachment_entity_factory(
            id=sample_attachment_entity.id,
            file=new_file_field,
            attachment_type=new_attachment_type,
            object_id=sample_attachment_entity.object_id,
            title=new_title,
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title=new_title,
            object_id=sample_attachment_entity.object_id,
            attachment_type=new_attachment_type,
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.return_value = new_file_field
        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_unit_of_work[AttachmentRepository].save.return_value = updated_attachment

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == updated_attachment.id
        assert result.file is not None
        assert result.file.name == updated_attachment.file.name
        assert result.file.url == updated_attachment.file.url
        assert result.file.size == updated_attachment.file.size
        assert result.content_type_id == updated_attachment.content_type_id
        assert result.object_id == updated_attachment.object_id
        assert result.title == updated_attachment.title
        assert result.attachment_type == updated_attachment.attachment_type

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_file_storage_service.delete_file.assert_called_once_with(original_file_path)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_command_without_file(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test updating attachment without file"""

        # Arrange
        new_title = "New title for attachment"
        new_attachment_type = "image"

        updated_attachment = attachment_entity_factory(
            id=sample_attachment_entity.id,
            attachment_type=new_attachment_type,
            object_id=sample_attachment_entity.object_id,
            title=new_title,
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title=new_title,
            object_id=sample_attachment_entity.object_id,
            attachment_type=new_attachment_type,
            file=None,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_unit_of_work[AttachmentRepository].save.return_value = updated_attachment

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == updated_attachment.id
        assert result.file is not None
        assert result.file.name == updated_attachment.file.name
        assert result.file.url == updated_attachment.file.url
        assert result.file.size == updated_attachment.file.size
        assert result.content_type_id == updated_attachment.content_type_id
        assert result.object_id == updated_attachment.object_id
        assert result.title == updated_attachment.title
        assert result.attachment_type == updated_attachment.attachment_type

        # Verify method calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_not_called()
        mock_from_file_name.assert_not_called()
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_handle_update_attachment_not_found_exception(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_entity: AttachmentEntity,
        sample_attachment_file: SimpleUploadedFile,
    ) -> None:
        """Test updating attachment when attachment not found in db"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].get_by_id.side_effect = (
            AttachmentNotFoundError()
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            title="New title",
            content_type_id=sample_attachment_entity.content_type_id,
            object_id=sample_attachment_entity.object_id,
            file=sample_attachment_file,
            attachment_type="document",
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        # Act
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(command)

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_raises_generic_errors(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test updating attachment with generic errors"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"
        new_file_field = attachment_file_field_factory(
            file_name=new_file_name,
            file_path="attachments/" + new_file_name,
            file_url="attachments/" + new_file_name,
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title="New title",
            object_id=sample_attachment_entity.object_id,
            attachment_type="document",
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.return_value = new_file_field
        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_unit_of_work[AttachmentRepository].save.side_effect = Exception(
            "Database error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Asserts and verify services calls
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_when_save_file_fails(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test updating attachment when save_file fails"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title="New title",
            object_id=sample_attachment_entity.object_id,
            attachment_type="document",
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_file_storage_service.save_file.side_effect = Exception(
            "Storage service error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_not_called()
        mock_unit_of_work[AttachmentRepository].save.assert_not_called()
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_when_file_field_factory_raises_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test updating attachment when FileFieldFactory raises error"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title="New title",
            object_id=sample_attachment_entity.object_id,
            attachment_type="document",
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.side_effect = Exception("FileFieldFactory error")

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_not_called()
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_when_update_file_raises_validation_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test updating attachment when update_file raises AttachmentValidationError"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"
        # Create invalid file field (size=0)
        invalid_file_field = attachment_file_field_factory(
            file_name=new_file_name,
            file_path="attachments/" + new_file_name,
            file_url="attachments/" + new_file_name,
            file_size=0,  # Invalid size
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title="New title",
            object_id=sample_attachment_entity.object_id,
            attachment_type="document",
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.return_value = invalid_file_field

        # Act
        with pytest.raises(ApplicationValidationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_not_called()
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_when_repository_save_raises_validation_error(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
        attachment_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test updating attachment when repository save raises AttachmentValidationError"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"
        new_file_field = attachment_file_field_factory(
            file_name=new_file_name,
            file_path="attachments/" + new_file_name,
            file_url="attachments/" + new_file_name,
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title="New title",
            object_id=sample_attachment_entity.object_id,
            attachment_type="document",
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.return_value = new_file_field
        mock_unit_of_work[AttachmentRepository].save.side_effect = AttachmentValidationError(
            "Invalid attachment data"
        )

        # Act
        with pytest.raises(ApplicationValidationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        # Old file should not be deleted if save fails
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    @patch(
        "media.application.command_handlers.attachment_command_handlers.FileFieldFactory.from_file_name"
    )
    def test_handle_update_attachment_when_delete_file_fails_but_update_succeeds(
        self,
        mock_from_file_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_entity: AttachmentEntity,
        attachment_file_field_factory: Callable[..., FileField],
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test updating attachment when delete_file fails but update succeeds"""

        # Arrange
        new_file = SimpleUploadedFile(
            name="new_file.rar", content=b"new fake file", content_type="application/x-rar-compressed"
        )
        new_file_name = "new_file.rar"
        new_title = "New title for attachment"
        new_attachment_type = "image"
        new_file_field = attachment_file_field_factory(
            file_name=new_file_name,
            file_path="attachments/" + new_file_name,
            file_url="attachments/" + new_file_name,
        )
        original_file_path = sample_attachment_entity.file.path

        updated_attachment = attachment_entity_factory(
            id=sample_attachment_entity.id,
            file=new_file_field,
            attachment_type=new_attachment_type,
            object_id=sample_attachment_entity.object_id,
            title=new_title,
        )

        command = UpdateAttachmentCommand(
            attachment_id=uuid.UUID(sample_attachment_entity.id),
            content_type_id=sample_attachment_entity.content_type_id,
            title=new_title,
            object_id=sample_attachment_entity.object_id,
            attachment_type=new_attachment_type,
            file=new_file,
        )

        handler = UpdateAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_file_storage_service.save_file.return_value = new_file_name
        mock_from_file_name.return_value = new_file_field
        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_unit_of_work[AttachmentRepository].save.return_value = updated_attachment
        mock_file_storage_service.delete_file.side_effect = Exception(
            "File deletion error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_file_storage_service.save_file.assert_called_once_with(new_file)
        mock_from_file_name.assert_called_once_with(new_file_name)
        mock_unit_of_work[AttachmentRepository].save.assert_called_once()
        mock_file_storage_service.delete_file.assert_called_once_with(original_file_path)
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestDeleteAttachmentCommandHandler:
    """Test deletion of the attachment with its command"""

    def test_delete_attachment_command(
        self,
        sample_attachment_entity: AttachmentEntity,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Tests the complete deletion scenario"""

        # Arrange
        command = DeleteAttachmentCommand(pk=uuid.UUID(sample_attachment_entity.id))

        handler = DeleteAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == sample_attachment_entity.id
        assert result.file.name == sample_attachment_entity.file.name

        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_unit_of_work[AttachmentRepository].delete.assert_called_once_with(
            sample_attachment_entity
        )
        mock_file_storage_service.delete_file.assert_called_once_with(
            sample_attachment_entity.file.path
        )
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_delete_attachment_while_attachment_does_not_exist(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_attachment_entity: AttachmentEntity,
    ) -> None:
        """Test deleting attachment that does not exists"""

        # Arrange
        mock_unit_of_work[AttachmentRepository].get_by_id.side_effect = (
            AttachmentNotFoundError()
        )
        command = DeleteAttachmentCommand(pk=uuid.UUID(sample_attachment_entity.id))
        handler = DeleteAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        # Act
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[AttachmentRepository].delete.assert_not_called()
        mock_file_storage_service.delete_file.assert_not_called()

    def test_delete_attachment_raises_generic_errors(
        self,
        sample_attachment_entity: AttachmentEntity,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Tests deletion when repository raises generic error"""

        # Arrange
        command = DeleteAttachmentCommand(pk=uuid.UUID(sample_attachment_entity.id))

        handler = DeleteAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_unit_of_work[AttachmentRepository].delete.side_effect = Exception(
            "Database error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_unit_of_work[AttachmentRepository].delete.assert_called_once_with(
            sample_attachment_entity
        )
        mock_file_storage_service.delete_file.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

    def test_delete_attachment_when_file_deletion_fails(
        self,
        sample_attachment_entity: AttachmentEntity,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Tests deletion when file deletion fails but attachment is deleted from DB"""

        # Arrange
        command = DeleteAttachmentCommand(pk=uuid.UUID(sample_attachment_entity.id))

        handler = DeleteAttachmentCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[AttachmentRepository].get_by_id.return_value = (
            sample_attachment_entity
        )
        mock_file_storage_service.delete_file.side_effect = Exception(
            "File deletion error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Assert
        mock_unit_of_work[AttachmentRepository].get_by_id.assert_called_once_with(
            sample_attachment_entity.id
        )
        mock_unit_of_work[AttachmentRepository].delete.assert_called_once_with(
            sample_attachment_entity
        )
        mock_file_storage_service.delete_file.assert_called_once_with(
            sample_attachment_entity.file.path
        )
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()
