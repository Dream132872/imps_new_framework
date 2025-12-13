"""Test picture command handlers"""

import uuid
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.application.command_handlers import (
    CreatePictureCommandHandler,
    DeletePictureCommandHandler,
    UpdatePictureCommandHandler,
)
from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.entities.picture_entities import PictureType
from media.domain.exceptions import PictureNotFoundError
from media.domain.repositories import PictureRepository
from media.tests.conftest import sample_picture_entity
from shared.application.exceptions import (
    ApplicationError,
    ApplicationNotFoundError,
    ApplicationValidationError,
)
from shared.domain.entities import FileField


@pytest.mark.application
@pytest.mark.unit
class TestCreatePictureCommandHandler:
    """Test create picture command handler"""

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_create_picture_command_with_valid_data(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_image_file: SimpleUploadedFile,
        sample_image_file_field: FileField,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test creating picture command"""

        image_path = "images/test_image.jpg"
        mock_file_storage_service.save_image.return_value = image_path
        mock_from_image_name.return_value = sample_image_file_field

        # Arrange
        object_id = uuid.uuid4()
        command = CreatePictureCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            image=sample_image_file,  # type: ignore
            picture_type=PictureType.MAIN.value,
            title="Title of the image",
            alternative="Alternative of the image",
        )

        saved_picture = picture_entity_factory(
            picture_title=command.title,
            picture_alternative=command.alternative,
            picture_type=command.picture_type,
            picture_object_id=command.object_id,
        )

        mock_unit_of_work[PictureRepository].save.return_value = saved_picture

        # Act
        handler = CreatePictureCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        result = handler.handle(command)

        # Assert
        assert result is not None
        assert result.id == saved_picture.id
        assert result.title == command.title
        assert result.alternative == command.alternative
        assert result.content_type_id == command.content_type_id
        assert result.object_id == command.object_id
        assert result.picture_type == command.picture_type
        assert result.image is not None
        assert result.image.name == sample_image_file_field.name

        # Verify service calls
        mock_file_storage_service.save_image.assert_called_with(sample_image_file)
        mock_from_image_name.assert_called_once_with("images/test_image.jpg")

        mock_unit_of_work[PictureRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_create_picture_command_with_invalid_image_size_raises_validation_error(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_content_type: ContentType,
        image_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test validation errors for create picture command"""

        # Arrange
        image_path = "images/test_image.jpg"
        sample_image_file_field = image_file_field_factory(
            image_name="test_image.jpg",
            image_path=image_path,
            image_url="",
            image_width=0,
            image_height=0,
            image_size=0,  # this would generate error
            image_content_type="images/jpeg",
        )
        mock_from_image_name.return_value = sample_image_file_field
        mock_file_storage_service.save_image.return_value = image_path

        command = CreatePictureCommand(
            content_type_id=sample_content_type.id,
            title="Create new image",
            alternative="Alternative new image",
            image=SimpleUploadedFile(
                name="test_image.jpg", content=b"content", content_type="images/jpeg"
            ),  # type: ignore
            object_id=uuid.uuid4(),
            picture_type=PictureType.AVATAR.value,
        )

        handler = CreatePictureCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act and Assert
        with pytest.raises(ApplicationValidationError) as e:
            handler.handle(command=command)

        # Verify
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()

        # Verify that cleanup method calls
        mock_file_storage_service.delete_image.assert_called_once_with(image_path)
        mock_from_image_name.assert_called_once_with(image_path)

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_raises_error_when_image_is_emtpy(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test raising error when image is empty"""
        # Arrange

        mock_file_storage_service.save_image.return_value = ""

        object_id = uuid.uuid4()
        command = CreatePictureCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            image=None,
            picture_type=PictureType.MAIN.value,
            title="",
            alternative="",
        )

        # Act
        handler = CreatePictureCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Assert
        with pytest.raises(ApplicationValidationError):
            handler.handle(command=command)

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_create_picture_raises_generic_errors(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_image_file: SimpleUploadedFile,
        sample_image_file_field: FileField,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test creating picture command"""

        image_path = "images/test_image.jpg"

        # Arrange
        object_id = uuid.uuid4()
        command = CreatePictureCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            image=sample_image_file,  # type: ignore
            picture_type=PictureType.MAIN.value,
            title="Title of the image",
            alternative="Alternative of the image",
        )

        mock_file_storage_service.save_image.return_value = image_path
        mock_from_image_name.return_value = sample_image_file_field
        mock_unit_of_work[PictureRepository].save.side_effect = Exception(
            "Database error"
        )

        handler = CreatePictureCommandHandler(
            uow=mock_unit_of_work,
            file_storage_service=mock_file_storage_service,
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command)

        # Assert and verify services calls
        mock_file_storage_service.save_image.assert_called_with(sample_image_file)
        mock_from_image_name.assert_called_once_with("images/test_image.jpg")

        mock_unit_of_work[PictureRepository].save.assert_called_once()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestUpdatePictureCommandHandler:
    """Test updating picture command"""

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_update_picture_command_including_image(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        image_file_factory: Callable[..., SimpleUploadedFile],
        sample_picture_entity: PictureEntity,
        image_file_field_factory: Callable[..., FileField],
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test updating picture with valid data"""

        # Arrange
        new_image = image_file_factory(name="new_image.jpg", content=b"new fake image")
        new_image_name = "new_image.jpg"
        new_title = "New title for picture"
        new_alternative = "New alternative for picture"
        new_image_file_field = image_file_field_factory(
            image_name=new_image_name,
            image_path="images/" + new_image_name,
            image_url="images/" + new_image_name,
        )
        original_image_path = sample_picture_entity.image.path

        updated_picture = picture_entity_factory(
            id=sample_picture_entity.id,
            image=new_image_file_field,
            picture_type=sample_picture_entity.picture_type,
            picture_object_id=sample_picture_entity.object_id,
            picture_title=new_title,
            picture_alternative=new_alternative,
        )

        command = UpdatePictureCommand(
            picture_id=uuid.UUID(sample_picture_entity.id),
            content_type_id=sample_picture_entity.content_type_id,
            title=new_title,
            alternative=new_alternative,
            object_id=sample_picture_entity.object_id,
            picture_type=PictureType.MAIN.value,
            image=new_image,
        )

        handler = UpdatePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_file_storage_service.save_image.return_value = new_image_name
        mock_from_image_name.return_value = new_image_file_field
        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )
        mock_unit_of_work[PictureRepository].save.return_value = updated_picture

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == updated_picture.id
        assert result.image is not None
        assert result.image.name == updated_picture.image.name
        assert result.image.url == updated_picture.image.url
        assert result.image.size == updated_picture.image.size
        assert result.image.content_type == updated_picture.image.content_type
        assert result.image.file_type == updated_picture.image.file_type.value
        assert result.content_type_id == updated_picture.content_type_id
        assert result.object_id == updated_picture.object_id
        assert result.title == updated_picture.title
        assert result.alternative == updated_picture.alternative

        # Verify method calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            sample_picture_entity.id
        )
        mock_file_storage_service.save_image.assert_called_once_with(new_image)
        mock_from_image_name.assert_called_once_with(new_image_name)
        mock_unit_of_work[PictureRepository].save.assert_called_once()
        mock_file_storage_service.delete_image.assert_called_once_with(
            original_image_path
        )
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_update_picture_command_without_image(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_picture_entity: PictureEntity,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test updating picture with valid data"""

        # Arrange
        new_title = "New title for picture"
        new_alternative = "New alternative for picture"

        updated_picture = picture_entity_factory(
            id=sample_picture_entity.id,
            picture_type=sample_picture_entity.picture_type,
            picture_object_id=sample_picture_entity.object_id,
            picture_title=new_title,
            picture_alternative=new_alternative,
        )

        command = UpdatePictureCommand(
            picture_id=uuid.UUID(sample_picture_entity.id),
            content_type_id=sample_picture_entity.content_type_id,
            title=new_title,
            alternative=new_alternative,
            object_id=sample_picture_entity.object_id,
            picture_type=PictureType.MAIN.value,
            image=None,
        )

        handler = UpdatePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )
        mock_unit_of_work[PictureRepository].save.return_value = updated_picture

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == updated_picture.id
        assert result.image is not None
        assert result.image.name == updated_picture.image.name
        assert result.image.url == updated_picture.image.url
        assert result.image.size == updated_picture.image.size
        assert result.image.content_type == updated_picture.image.content_type
        assert result.image.file_type == updated_picture.image.file_type.value
        assert result.content_type_id == updated_picture.content_type_id
        assert result.object_id == updated_picture.object_id
        assert result.title == updated_picture.title
        assert result.alternative == updated_picture.alternative

        # Verify method calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            sample_picture_entity.id
        )
        mock_file_storage_service.save_image.assert_not_called()
        mock_from_image_name.assert_not_called()
        mock_unit_of_work[PictureRepository].save.assert_called_once()
        mock_file_storage_service.delete_image.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_handle_update_picture_not_found_exception(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_picture_entity: PictureEntity,
        sample_image_file: SimpleUploadedFile,
    ) -> None:
        """Test updating picture when picture not found in db"""

        # Arrange
        mock_unit_of_work[PictureRepository].get_by_id.side_effect = (
            PictureNotFoundError()
        )

        command = UpdatePictureCommand(
            picture_id=uuid.UUID(sample_picture_entity.id),
            title="New title",
            alternative="New alternative",
            content_type_id=sample_picture_entity.content_type_id,
            object_id=sample_picture_entity.object_id,
            image=sample_image_file,
            picture_type=PictureType.MAIN.value,
        )

        handler = UpdatePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        # Act
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(command)

    @patch(
        "media.application.command_handlers.picture_command_handlers.FileFieldFactory.from_image_name"
    )
    def test_handle_update_picture_raises_generic_errors(
        self,
        mock_from_image_name: MagicMock,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        image_file_factory: Callable[..., SimpleUploadedFile],
        sample_picture_entity: PictureEntity,
        image_file_field_factory: Callable[..., FileField],
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test updating picture with valid data"""

        # Arrange
        new_image = image_file_factory(name="new_image.jpg", content=b"new fake image")
        new_image_name = "new_image.jpg"
        new_title = "New title for picture"
        new_alternative = "New alternative for picture"
        new_image_file_field = image_file_field_factory(
            image_name=new_image_name,
            image_path="images/" + new_image_name,
            image_url="images/" + new_image_name,
        )

        command = UpdatePictureCommand(
            picture_id=uuid.UUID(sample_picture_entity.id),
            content_type_id=sample_picture_entity.content_type_id,
            title=new_title,
            alternative=new_alternative,
            object_id=sample_picture_entity.object_id,
            picture_type=PictureType.MAIN.value,
            image=new_image,
        )

        handler = UpdatePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_file_storage_service.save_image.return_value = new_image_name
        mock_from_image_name.return_value = new_image_file_field
        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )
        mock_unit_of_work[PictureRepository].save.side_effect = Exception(
            "Database error"
        )

        # Act
        with pytest.raises(ApplicationError):
            handler.handle(command=command)

        # Asserts and verify services calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            sample_picture_entity.id
        )
        mock_file_storage_service.save_image.assert_called_once_with(new_image)
        mock_from_image_name.assert_called_once_with(new_image_name)
        mock_unit_of_work[PictureRepository].save.assert_called_once()
        mock_file_storage_service.delete_image.assert_not_called()
        mock_unit_of_work.__enter__.assert_called_once()
        mock_unit_of_work.__exit__.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestDeletePictureCommandHandler:
    """Test deletion of the picture with its command"""

    def test_delete_picture_command(
        self,
        sample_picture_entity: PictureEntity,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Tests the complete deletion scenario"""

        # Arrange
        command = DeletePictureCommand(pk=uuid.UUID(sample_picture_entity.id))

        handler = DeletePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == sample_picture_entity.id
        assert result.image.name == sample_picture_entity.image.name

        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            sample_picture_entity.id
        )
        mock_unit_of_work[PictureRepository].delete.assert_called_once_with(
            sample_picture_entity
        )
        mock_file_storage_service.delete_image.assert_called_once_with(
            sample_picture_entity.image.path
        )

    def test_delete_picture_while_picture_does_not_exist(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test deleting picture that does not exists"""

        # Arrange
        mock_unit_of_work[PictureRepository].get_by_id.side_effect = (
            PictureNotFoundError()
        )
        command = DeletePictureCommand(pk=uuid.UUID(sample_picture_entity.id))
        handler = DeletePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        # Act
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(command)

        # Assert
        mock_unit_of_work[PictureRepository].delete.assert_not_called()
        mock_file_storage_service.delete_image.assert_not_called()

    def test_delete_picture_raises_generic_errors(
        self,
        sample_picture_entity: PictureEntity,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
    ) -> None:
        """Tests the complete deletion scenario"""

        # Arrange
        command = DeletePictureCommand(pk=uuid.UUID(sample_picture_entity.id))

        handler = DeletePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )

        # Act
        result = handler.handle(command=command)

        # Assert
        assert result is not None
        assert result.id == sample_picture_entity.id
        assert result.image.name == sample_picture_entity.image.name

        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            sample_picture_entity.id
        )
        mock_unit_of_work[PictureRepository].delete.assert_called_once_with(
            sample_picture_entity
        )
        mock_file_storage_service.delete_image.assert_called_once_with(
            sample_picture_entity.image.path
        )
