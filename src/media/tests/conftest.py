"""
Media related fixtures.
"""

import uuid

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.picture_entities import Picture as PictureEntity
from media.infrastructure.models import Picture as PictureModel
from shared.domain.entities import FileField, FileType


@pytest.fixture
def sample_image_file() -> SimpleUploadedFile:
    """Creating a sample image file for testing."""

    image_file = b"fake image content"
    return SimpleUploadedFile(
        name="test_image.jpg", content=image_file, content_type="image/jpeg"
    )


@pytest.fixture
def sample_image_field_fied() -> FileField:
    return FileField(
        file_type=FileType.IMAGE,
        name="test_image.jpg",
        path="/media/test_image.jpg",
        url="/media/test_image.jpg",
        width=1000,
        height=700,
        size=1024,
        content_type="images/jpeg",
    )


@pytest.fixture
def sample_picture_entity(
    db: None, sample_image_field_fied: FileField, sample_content_type: ContentType
) -> PictureEntity:
    """
    Create a sample picture domain entity.

    Returns a sample Picutre (Entity) instance with:
    - image:
    """
    return PictureEntity(
        image=sample_image_field_fied,
        picture_type="main",
        content_type_id=sample_content_type.id,
        object_id=str(uuid.uuid4()),
        title="Image title",
        alternative="Image alternative",
    )


@pytest.fixture
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
