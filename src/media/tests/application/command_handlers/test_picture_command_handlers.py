"""Test picture command handlers"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.application.command_handlers import CreatePictureCommandHandler
from media.application.commands import CreatePictureCommand
from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.entities.picture_entities import PictureType
from media.domain.repositories import PictureRepository
from shared.domain.factories import FileFieldFactory


@pytest.mark.application
@pytest.mark.unit
class TestCreatePictureCommandHandler:
    """Test create picture command handler"""

    def test_handle_create_picture_command(
        self,
        mock_unit_of_work: MagicMock,
        mock_file_storage_service: MagicMock,
        sample_image_file: SimpleUploadedFile,
        sample_content_type: ContentType,
    ) -> None:
        """Test creating picture command"""

        mock_file_storage_service.save_image.return_value = "images/test_image.jpg"

        # Arrange
        object_id = uuid.uuid4()
        command = CreatePictureCommand(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            image=sample_image_file,
            picture_type=PictureType.MAIN.value,
            title="Title of the image",
            alternative="Alternative of the image",
        )

        picture_entity_image = FileFieldFactory.from_image_name("images/test_image.jpg")

        saved_picture = PictureEntity(
            image=picture_entity_image,
            content_type_id=sample_content_type.id,
            object_id=str(object_id),
            picture_type=PictureType.MAIN.value,
            title="Title of the image",
            alternative="Alternative of the image",
        )

        mock_unit_of_work[PictureRepository].save.return_value = saved_picture

        # Act
        handler = CreatePictureCommandHandler(
            uow=mock_unit_of_work, file_storage_service=mock_file_storage_service
        )

        result = handler.handle(command)

        # Assert
        assert result is not None
        assert result.id == saved_picture.id
        assert result.title == "Title of the image"
        mock_file_storage_service.save_image.assert_called_with(sample_image_file)
        mock_unit_of_work[PictureRepository].save.assert_called_once()
