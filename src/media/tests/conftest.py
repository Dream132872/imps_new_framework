"""
Media related fixtures.
"""

import uuid
from unittest.mock import MagicMock

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.repositories import PictureRepository
from media.domain.services import FileStorageService
from media.infrastructure.models import Picture as PictureModel


@pytest.fixture
def sample_image_file() -> SimpleUploadedFile:
    """Creating a sample image file for testing."""

    image_file = b"fake image content"
    return SimpleUploadedFile(
        name="test_image.jpg", content=image_file, content_type="image/jpeg"
    )


@pytest.fixture()
def sample_picture_model(
    sample_image_file: SimpleUploadedFile, sample_content_type: ContentType, db: None
) -> PictureModel:
    """
    Create a sample picture model.

    Returns a Picture instance with:
    - image: sample file field.
    - picture_type: main value ('main').
    - title: static title ('title').
    - alternative: static alternative ('alternative').
    """

    return PictureModel(
        image=sample_image_file,
        alternative="alternative",
        title="title",
        content_type=sample_content_type,
        object_id=str(uuid.uuid4()),
        picture_type="main",
        display_order=1,
    )


@pytest.fixture
def mock_picture_repository() -> MagicMock:
    """Mock object of PictureRepository."""

    mock_repository = MagicMock(spec=PictureRepository)
    return mock_repository


@pytest.fixture
def mock_file_storage_service() -> MagicMock:
    """Mock object of FileStorageService"""

    mock_service = MagicMock(spec=FileStorageService)

    mock_service.save_image.return_value = "images/test_image.jpg"
    mock_service.delete_image.return_value = None

    mock_service.save_file.return_value = "attachments/test_file.rar"
    mock_service.delete_file.return_value = None

    return mock_service
