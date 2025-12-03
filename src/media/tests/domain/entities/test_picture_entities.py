"""Test picture entity."""

import uuid

import pytest
from django.contrib.contenttypes.models import ContentType

from media.domain.entities.picture_entities import Picture as PictureEntity
from shared.domain.entities import FileField


@pytest.mark.unit
@pytest.mark.domain
class TestPictureEntity:
    """Test suite for picture domain entity."""

    def test_picture_creation_with_required_fields(
        self, sample_image_field_fied: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating picture entity with required fields."""

        # Arrange
        object_id = str(uuid.uuid4())

        # Act
        picture = PictureEntity(
            image=sample_image_field_fied,
            picture_type="main",
            content_type_id=sample_content_type.id,
            object_id=object_id,
            title="Image title",
            alternative="Image alternative",
        )

        # Assert
        assert picture.id is not None
        assert picture.image == sample_image_field_fied
        assert picture.picture_type == "main"
        assert picture.created_at is not None
        assert picture.updated_at is not None
        assert picture.title == "Image title"
        assert picture.alternative == "Image alternative"
        assert picture.content_type_id == sample_content_type.id
