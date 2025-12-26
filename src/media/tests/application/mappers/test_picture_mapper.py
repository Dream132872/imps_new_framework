"""Test picture mapper"""

import uuid
from datetime import datetime
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType

from media.application.dtos import PictureDTO
from media.application.mappers import PictureDTOMapper
from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.entities.picture_entities import PictureType
from media.domain.exceptions import PictureValidationError
from shared.domain.entities import FileField, FileFieldType


@pytest.mark.application
@pytest.mark.unit
class TestPictureDTOMapper:
    """Test PictureDTOMapper"""

    def test_to_dto_with_valid_picture_entity(
        self,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test converting picture entity to DTO"""

        # Act
        result = PictureDTOMapper.to_dto(sample_picture_entity)

        # Assert
        assert isinstance(result, PictureDTO)
        assert str(result.id) == sample_picture_entity.id
        assert result.picture_type == sample_picture_entity.picture_type
        assert result.title == sample_picture_entity.title
        assert result.alternative == sample_picture_entity.alternative
        assert result.content_type_id == sample_picture_entity.content_type_id
        assert result.object_id == sample_picture_entity.object_id
        assert result.created_at == sample_picture_entity.created_at
        assert result.updated_at == sample_picture_entity.updated_at

        # Verify image field mapping
        assert result.image is not None
        assert result.image.name == sample_picture_entity.image.name
        assert result.image.url == sample_picture_entity.image.url
        assert result.image.size == sample_picture_entity.image.size
        assert result.image.width == sample_picture_entity.image.width
        assert result.image.height == sample_picture_entity.image.height
        assert result.image.content_type == sample_picture_entity.image.content_type
        assert result.image.file_type == FileFieldType.IMAGE.value

    def test_to_dto_with_different_picture_types(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test converting picture entity with different picture types"""

        # Test MAIN type
        main_picture = picture_entity_factory(picture_type=PictureType.MAIN.value)
        result = PictureDTOMapper.to_dto(main_picture)
        assert result.picture_type == PictureType.MAIN.value

        # Test GALLERY type
        gallery_picture = picture_entity_factory(picture_type=PictureType.GALLERY.value)
        result = PictureDTOMapper.to_dto(gallery_picture)
        assert result.picture_type == PictureType.GALLERY.value

        # Test AVATAR type
        avatar_picture = picture_entity_factory(picture_type=PictureType.AVATAR.value)
        result = PictureDTOMapper.to_dto(avatar_picture)
        assert result.picture_type == PictureType.AVATAR.value

        # Test BANNER type
        banner_picture = picture_entity_factory(picture_type=PictureType.BANNER.value)
        result = PictureDTOMapper.to_dto(banner_picture)
        assert result.picture_type == PictureType.BANNER.value

    def test_to_dto_with_empty_title_and_alternative(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test converting picture entity with empty title and alternative"""

        # Arrange
        picture = picture_entity_factory(picture_title="", picture_alternative="")

        # Act
        result = PictureDTOMapper.to_dto(picture)

        # Assert
        assert result.title == ""
        assert result.alternative == ""

    def test_to_dto_with_none_image_properties(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
        image_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test converting picture entity with None image properties"""

        # Arrange
        image_field = image_file_field_factory(
            image_width=0,
            image_height=0,
            image_size=0,
            image_content_type=None,
        )

        # Assert
        with pytest.raises(PictureValidationError) as e:
            picture = picture_entity_factory(image=image_field)

    def test_to_dto_preserves_timestamps(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
        sample_image_file_field: FileField,
        sample_content_type: ContentType,
    ) -> None:
        """Test that timestamps are preserved correctly"""

        # Arrange
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        picture_id = str(uuid.uuid4())

        picture = PictureEntity(
            id=picture_id,
            image=sample_image_file_field,
            picture_type="main",
            content_type_id=sample_content_type.id,
            object_id=str(uuid.uuid4()),
            title="Test",
            alternative="Test",
            created_at=created_at,
            updated_at=updated_at,
        )

        # Act
        result = PictureDTOMapper.to_dto(picture)

        # Assert
        assert result.created_at == created_at
        assert result.updated_at == updated_at

    def test_list_to_dto_with_empty_list(
        self,
    ) -> None:
        """Test converting empty list of picture entities"""

        # Act
        result = PictureDTOMapper.list_to_dto([])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_to_dto_with_single_picture(
        self,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test converting single picture entity in list"""

        # Act
        result = PictureDTOMapper.list_to_dto([sample_picture_entity])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PictureDTO)
        assert str(result[0].id) == sample_picture_entity.id

    def test_list_to_dto_with_multiple_pictures(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test converting multiple picture entities"""

        # Arrange
        picture1 = picture_entity_factory(picture_title="Picture 1")
        picture2 = picture_entity_factory(picture_title="Picture 2")
        picture3 = picture_entity_factory(picture_title="Picture 3")

        # Act
        result = PictureDTOMapper.list_to_dto([picture1, picture2, picture3])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0].title == "Picture 1"
        assert result[1].title == "Picture 2"
        assert result[2].title == "Picture 3"
        assert all(isinstance(dto, PictureDTO) for dto in result)

    def test_list_to_dto_preserves_order(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that list_to_dto preserves the order of entities"""

        # Arrange
        pictures = [
            picture_entity_factory(picture_title=f"Picture {i}") for i in range(5)
        ]

        # Act
        result = PictureDTOMapper.list_to_dto(pictures)

        # Assert
        assert len(result) == 5
        for i, dto in enumerate(result):
            assert dto.title == f"Picture {i}"

    def test_to_dto_with_different_object_id_types(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test converting picture entity with different object_id types"""

        # Test with string object_id
        picture_str = picture_entity_factory(picture_object_id="string-id")
        result_str = PictureDTOMapper.to_dto(picture_str)
        assert result_str.object_id == "string-id"

        # Test with integer object_id
        picture_int = picture_entity_factory(picture_object_id=12345)
        result_int = PictureDTOMapper.to_dto(picture_int)
        assert result_int.object_id == 12345

    def test_to_dto_with_large_image_dimensions(
        self,
        picture_entity_factory: Callable[..., PictureEntity],
        image_file_field_factory: Callable[..., FileField],
    ) -> None:
        """Test converting picture entity with large image dimensions"""

        # Arrange
        image_field = image_file_field_factory(
            image_width=5000,
            image_height=3000,
            image_size=5000000,  # 5MB
        )
        picture = picture_entity_factory(image=image_field)

        # Act
        result = PictureDTOMapper.to_dto(picture)

        # Assert
        assert result.image.width == 5000
        assert result.image.height == 3000
        assert result.image.size == 5000000
