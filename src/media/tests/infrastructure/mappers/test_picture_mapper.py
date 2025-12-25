"""Test picture mapper"""

import uuid
from datetime import datetime
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.entities.picture_entities import PictureType
from media.infrastructure.mappers import PictureMapper
from media.infrastructure.models import Picture as PictureModel
from shared.domain.entities import FileField, FileFieldType


@pytest.mark.infrastructure
@pytest.mark.unit
class TestPictureMapper:
    """Test PictureMapper"""

    def test_entity_to_model_with_valid_picture_entity(
        self,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test converting picture entity to model"""

        # Act
        result = PictureMapper.entity_to_model(sample_picture_entity)

        # Assert
        assert isinstance(result, PictureModel)
        assert result.id == sample_picture_entity.id
        assert result.created_at == sample_picture_entity.created_at
        assert result.updated_at == sample_picture_entity.updated_at
        assert result.image == sample_picture_entity.image.name
        assert result.alternative == sample_picture_entity.alternative
        assert result.title == sample_picture_entity.title
        assert result.picture_type == sample_picture_entity.picture_type
        assert result.content_type_id == sample_picture_entity.content_type_id
        assert result.object_id == sample_picture_entity.object_id

    def test_entity_to_model_with_different_picture_types(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test converting entity to model with different picture types"""

        # Arrange
        main_picture = picture_entity_factory(picture_type="main")
        gallery_picture = picture_entity_factory(picture_type="gallery")
        avatar_picture = picture_entity_factory(picture_type="avatar")
        banner_picture = picture_entity_factory(picture_type="banner")

        # Act
        main_model = PictureMapper.entity_to_model(main_picture)
        gallery_model = PictureMapper.entity_to_model(gallery_picture)
        avatar_model = PictureMapper.entity_to_model(avatar_picture)
        banner_model = PictureMapper.entity_to_model(banner_picture)

        # Assert
        assert main_model.picture_type == "main"
        assert gallery_model.picture_type == "gallery"
        assert avatar_model.picture_type == "avatar"
        assert banner_model.picture_type == "banner"

    def test_entity_to_model_preserves_all_fields(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
        sample_content_type: ContentType,
    ) -> None:
        """Test that entity_to_model preserves all entity fields"""

        # Arrange
        picture_id = str(uuid.uuid4())
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        image_name = "custom_image.png"
        title = "Custom Title"
        alternative = "Custom Alternative"
        picture_type = "gallery"
        content_type_id = sample_content_type.id
        object_id = str(uuid.uuid4())

        image_field = FileField(
            file_type=FileFieldType.IMAGE,
            name=image_name,
            path=f"/media/{image_name}",
            url=f"/media/{image_name}",
            width=800,
            height=600,
            size=2048,
            content_type="image/png",
        )

        entity = picture_entity_factory(
            picture_id=picture_id,
            image=image_field,
            picture_title=title,
            picture_alternative=alternative,
            picture_type=picture_type,
            picture_object_id=object_id,
        )
        entity._created_at = created_at
        entity._updated_at = updated_at

        # Act
        model = PictureMapper.entity_to_model(entity)

        # Assert
        assert model.id == picture_id
        assert model.created_at == created_at
        assert model.updated_at == updated_at
        assert model.image == image_name
        assert model.title == title
        assert model.alternative == alternative
        assert model.picture_type == picture_type
        assert model.content_type_id == content_type_id
        assert model.object_id == object_id

    def test_model_to_entity_with_valid_picture_model(
        self,
        sample_picture_model: PictureModel,
        db: None,
    ) -> None:
        """Test converting picture model to entity"""

        # Save model to database to get proper file field
        sample_picture_model.save()

        # Act
        result = PictureMapper.model_to_entity(sample_picture_model)

        # Assert
        assert isinstance(result, PictureEntity)
        assert result.id == str(sample_picture_model.id)
        assert result.created_at == sample_picture_model.created_at
        assert result.updated_at == sample_picture_model.updated_at
        assert isinstance(result.image, FileField)
        assert result.image.name == sample_picture_model.image.name
        assert result.title == sample_picture_model.title
        assert result.alternative == sample_picture_model.alternative
        assert result.picture_type == sample_picture_model.picture_type
        assert result.content_type_id == sample_picture_model.content_type_id
        assert result.object_id == sample_picture_model.object_id

    def test_model_to_entity_with_different_picture_types(
        self,
        sample_image_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test converting model to entity with different picture types"""

        # Arrange
        main_model = PictureModel(
            image=sample_image_file,
            picture_type="main",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        main_model.save()

        gallery_model = PictureModel(
            image=sample_image_file,
            picture_type="gallery",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        gallery_model.save()

        # Act
        main_entity = PictureMapper.model_to_entity(main_model)
        gallery_entity = PictureMapper.model_to_entity(gallery_model)

        # Assert
        assert main_entity.picture_type == "main"
        assert gallery_entity.picture_type == "gallery"

    def test_model_to_entity_preserves_all_fields(
        self,
        sample_image_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test that model_to_entity preserves all model fields"""

        # Arrange
        title = "Model Title"
        alternative = "Model Alternative"
        picture_type = "banner"
        object_id = str(uuid.uuid4())

        model = PictureModel(
            image=sample_image_file,
            title=title,
            alternative=alternative,
            picture_type=picture_type,
            content_type=sample_content_type,
            object_id=object_id,
        )
        model.save()

        # Act
        entity = PictureMapper.model_to_entity(model)

        # Assert
        assert entity.id == str(model.id)
        assert entity.created_at == model.created_at
        assert entity.updated_at == model.updated_at
        assert entity.title == title
        assert entity.alternative == alternative
        assert entity.picture_type == picture_type
        assert entity.content_type_id == sample_content_type.id
        assert entity.object_id == object_id
        assert isinstance(entity.image, FileField)
        assert entity.image.file_type == FileFieldType.IMAGE

    def test_round_trip_conversion(
        self,
        sample_picture_entity: PictureEntity,
        db: None,
    ) -> None:
        """Test round-trip conversion: entity -> model -> entity"""

        # Arrange
        original_entity = sample_picture_entity

        # Act
        model = PictureMapper.entity_to_model(original_entity)
        # Save model to get proper file field
        model.save()
        converted_entity = PictureMapper.model_to_entity(model)

        # Assert
        assert converted_entity.id == original_entity.id
        assert converted_entity.title == original_entity.title
        assert converted_entity.alternative == original_entity.alternative
        assert converted_entity.picture_type == original_entity.picture_type
        assert converted_entity.content_type_id == original_entity.content_type_id
        assert converted_entity.object_id == original_entity.object_id
        # Note: created_at and updated_at might differ slightly due to save operation

    def test_entity_to_model_with_none_values(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test entity_to_model handles None values correctly"""

        # Arrange
        entity = picture_entity_factory(
            picture_title="",
            picture_alternative="",
        )

        # Act
        model = PictureMapper.entity_to_model(entity)

        # Assert
        assert model.title == ""
        assert model.alternative == ""

    def test_model_to_entity_with_none_values(
        self,
        sample_image_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test model_to_entity handles None/empty values correctly"""

        # Arrange
        model = PictureModel(
            image=sample_image_file,
            title="",
            alternative="",
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
        )
        model.save()

        # Act
        entity = PictureMapper.model_to_entity(model)

        # Assert
        assert entity.title == ""
        assert entity.alternative == ""

    def test_entity_to_model_with_different_object_id_types(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test entity_to_model handles different object_id types"""

        # Arrange
        string_object_id = str(uuid.uuid4())
        int_object_id = 12345

        entity_string = picture_entity_factory(picture_object_id=string_object_id)
        entity_int = picture_entity_factory(picture_object_id=int_object_id)

        # Act
        model_string = PictureMapper.entity_to_model(entity_string)
        model_int = PictureMapper.entity_to_model(entity_int)

        # Assert
        assert model_string.object_id == string_object_id
        assert model_int.object_id == int_object_id

    def test_model_to_entity_with_different_object_id_types(
        self,
        sample_image_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        db: None,
    ) -> None:
        """Test model_to_entity handles different object_id types"""

        # Arrange
        string_object_id = str(uuid.uuid4())
        int_object_id = "12345"

        model_string = PictureModel(
            image=sample_image_file,
            content_type=sample_content_type,
            object_id=string_object_id,
        )
        model_string.save()

        model_int = PictureModel(
            image=sample_image_file,
            content_type=sample_content_type,
            object_id=int_object_id,
        )
        model_int.save()

        # Act
        entity_string = PictureMapper.model_to_entity(model_string)
        entity_int = PictureMapper.model_to_entity(model_int)

        # Assert
        assert entity_string.object_id == string_object_id
        assert entity_int.object_id == int_object_id
