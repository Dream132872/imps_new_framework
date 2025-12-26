"""Test picture entity."""

import uuid
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType

from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.exceptions import PictureValidationError
from shared.domain.entities import FileField, FileFieldType


@pytest.mark.unit
@pytest.mark.domain
class TestPictureEntity:
    """Test suite for picture domain entity."""

    def test_picture_creation_with_required_fields(
        self, sample_image_file_field: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating picture entity with required fields."""

        # Arrange
        object_id = str(uuid.uuid4())

        # Act
        picture = PictureEntity(
            image=sample_image_file_field,
            picture_type="main",
            content_type_id=sample_content_type.id,
            object_id=object_id,
        )

        # Assert
        assert picture.id is not None, "picture id should not be None"
        assert (
            picture.image == sample_image_file_field
        ), "Picture image should be equal to sample_image_field"
        assert picture.picture_type == "main", "picture type should be eqaul to 'main'"
        assert (
            picture.created_at is not None
        ), "created_at value should be set automatically"
        assert (
            picture.updated_at is not None
        ), "updated_at value should be set automatically"
        assert picture.title == "", "title of the picture should be empty string"
        assert (
            picture.alternative == ""
        ), "alternative text of the picture should be empty string"
        assert (
            picture.content_type_id == sample_content_type.id
        ), "content_type_id foreign key should be equalt to sample_content_type.id"

    def test_create_picture_entity_with_optional_fields(
        self, sample_image_file_field: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating picture entity with optional fields."""

        # Arrange
        object_id = str(uuid.uuid4())
        title = "Image title"
        alternative = "Image alternative"

        # Act
        picture = PictureEntity(
            image=sample_image_file_field,
            picture_type="main",
            content_type_id=sample_content_type.id,
            object_id=object_id,
            title=title,
            alternative=alternative,
        )

        # Assert
        assert (
            picture.id is not None
        ), "picture id should not be None and would have created automatically"
        assert (
            picture.title == "Image title"
        ), "picture title should be changed to 'Image title'"
        assert (
            picture.alternative == "Image alternative"
        ), "picture alternative should be changed to 'Image alternative'"

    def test_create_picture_entity_with_custom_id(
        self, sample_image_file_field: FileField, sample_content_type: ContentType
    ) -> None:
        """Test creating picture entity with custom id."""
        # Arrange
        custom_id = str(uuid.uuid4())
        object_id = str(uuid.uuid4())

        # Act
        picture = PictureEntity(
            id=custom_id,
            image=sample_image_file_field,
            picture_type="main",
            content_type_id=sample_content_type.id,
            object_id=object_id,
        )

        # Assert
        assert (
            picture.id == custom_id
        ), "id of the picture should be set to custom value"

    def test_create_picture_with_invalid_type(
        self, picture_entity_factory: Callable[..., PictureEntity]
    ) -> None:
        """Test creating picture with invalid type"""

        # Arrange
        invalid_type = "inalid_type"

        # Assert
        with pytest.raises(PictureValidationError) as e:
            picture_entity_factory(picture_type=invalid_type)

    def test_picture_update_image(
        self, sample_picture_entity: PictureEntity, sample_content_type: ContentType
    ) -> None:
        """Test updating picture image."""
        # Arragne
        original_updated_at = sample_picture_entity.updated_at
        new_file_field = FileField(
            file_type=FileFieldType.IMAGE,
            content_type="images/jpeg",
            name="images/new_image.jpg",
            url="/media/images/new_image.jpg",
            size=2000,
            width=2000,
            height=1000,
            path="/media/images/new_image.jpg",
        )

        # Act
        sample_picture_entity.update_image(new_file_field)

        # Assert
        assert (
            sample_picture_entity.image == new_file_field
        ), "New image file should be equal"
        assert (
            sample_picture_entity.updated_at > original_updated_at
        ), "Updated datetime should be greater than base value"

    def test_picture_update_information_with_title(
        self, sample_picture_entity: PictureEntity
    ) -> None:
        """Test updating picture information with title text."""
        # Arrange
        new_title = "New title"
        original_updated_at = sample_picture_entity.updated_at

        # Act
        sample_picture_entity.update_information(title=new_title)

        # Assert
        assert (
            sample_picture_entity.title == new_title
        ), "title of the picture should be set to 'New title'"
        assert (
            sample_picture_entity.updated_at > original_updated_at
        ), "the value of the updated_at of the picture should be greater than the original value"

    def test_picture_update_information_with_alternative(
        self, sample_picture_entity: PictureEntity
    ) -> None:
        """Testing picture information with alternative text."""
        # Arrange
        original_updated_at = sample_picture_entity.updated_at
        new_alternative = "New alternative"

        # Act
        sample_picture_entity.update_information(alternative=new_alternative)

        # Assert
        assert (
            sample_picture_entity.alternative == new_alternative
        ), "alternative text of the picture should be changed to 'New alternative'"
        assert (
            sample_picture_entity.updated_at > original_updated_at
        ), "the value of the updated_at of the picture should be greater than the original value"

    def test_update_picture_information_with_title_and_alternative_both(
        self, sample_picture_entity: PictureEntity
    ) -> None:
        """Testing picture update information with both title and alternative."""

        # Arrange
        new_title = "New title"
        new_alternative = "New alternative"
        original_updated_at = sample_picture_entity.updated_at

        # Act
        sample_picture_entity.update_information(
            title=new_title, alternative=new_alternative
        )

        # Assert
        assert (
            sample_picture_entity.title == new_title
        ), "title of the picture should be changed to 'New title'"
        assert (
            sample_picture_entity.alternative == "New alternative"
        ), "alternative of the picture should be changed to 'New alternative'"

        assert (
            sample_picture_entity.updated_at > original_updated_at
        ), "updated_at value should be changed to greater value of the original"

    def test_update_picture_information_with_empty_title_and_empty_alternative(
        self, sample_picture_entity: PictureEntity
    ):
        """Testing update picture information with empty title and empty alternative."""

        # Arrange
        original_title = sample_picture_entity.title
        origianl_alternative = sample_picture_entity.alternative

        # Act
        sample_picture_entity.update_information(title="", alternative="")

        # Assert
        assert sample_picture_entity.title == "", "title value should be changed"
        assert (
            sample_picture_entity.alternative == ""
        ), "alternative value should be changed"

    def test_picture_to_dict(self, sample_picture_entity: PictureEntity) -> None:
        """Test converting Picture entity to dictionary."""
        # Act
        result = sample_picture_entity.to_dict()

        # Assert
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "image" in result
        assert "title" in result
        assert "alternative" in result
        assert result["title"] == sample_picture_entity.title
        assert result["alternative"] == sample_picture_entity.alternative
        assert type(result["image"]) == dict

    def test_picture_equality(
        self, sample_content_type: ContentType, sample_image_file_field: FileField
    ):
        """Test picture equality using ID."""

        # Arrange
        picture_id = str(uuid.uuid4())
        object_id = str(uuid.uuid4())

        picture_1 = PictureEntity(
            id=picture_id,
            image=sample_image_file_field,
            content_type_id=sample_content_type.id,
            object_id=object_id,
            picture_type="main",
        )

        picture_2 = PictureEntity(
            id=picture_id,
            image=sample_image_file_field,
            content_type_id=sample_content_type.id,
            object_id=object_id,
            picture_type="main",
        )

        picture_3 = PictureEntity(
            id=str(uuid.uuid4()),
            image=sample_image_file_field,
            content_type_id=sample_content_type.id,
            object_id=object_id,
            picture_type="main",
        )

        # Assert
        assert picture_1 == picture_2
        assert picture_1 != picture_3
        assert picture_2 != picture_3

    def test_picture_repr_representation(
        self, sample_picture_entity: PictureEntity
    ) -> None:
        """Test picture representation."""
        # Arrange
        picture_repr = repr(sample_picture_entity)

        # Assert
        assert "PictureEntity" in picture_repr
        assert sample_picture_entity.id in picture_repr
        assert sample_picture_entity.image.name in picture_repr
