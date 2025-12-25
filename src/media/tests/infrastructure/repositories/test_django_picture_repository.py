import uuid
from io import BytesIO
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.exceptions import PictureNotFoundError
from media.infrastructure.models import Picture as PictureModel
from media.infrastructure.repositories import DjangoPictureRepository
from shared.domain.entities import FileFieldType
from shared.domain.factories import FileFieldFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


def _create_image_file(name: str = "test.png") -> SimpleUploadedFile:
    """Helper to create a valid image file for testing."""
    buffer = BytesIO()
    Image.new("RGB", (100, 100), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(
        name=name, content=buffer.read(), content_type="image/png"
    )


class TestDjangoPictureRepository:
    """Test suite for DjangoPictureRepository using DDD approach."""

    def test_get_by_id_returns_domain_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test retrieving picture entity by ID after saving through repository."""
        # Arrange: Create image file in storage and get FileField
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp-obj",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()  # Clean up temp model

        # Create entity using factory
        entity = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
            picture_title="Cover",
            picture_alternative="Alt",
        )

        repo = DjangoPictureRepository()

        # Act: Save entity through repository
        saved_entity = repo.save(entity)

        # Retrieve entity
        retrieved_entity = repo.get_by_id(saved_entity.id)

        # Assert
        assert retrieved_entity.id == saved_entity.id
        assert retrieved_entity.content_type_id == sample_content_type.id
        assert retrieved_entity.object_id == "obj-1"
        assert retrieved_entity.picture_type == "main"
        assert retrieved_entity.title == "Cover"
        assert retrieved_entity.alternative == "Alt"
        assert retrieved_entity.image.file_type == FileFieldType.IMAGE
        assert retrieved_entity.image.name.startswith("images/")

    def test_get_by_id_raises_not_found(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that get_by_id raises PictureNotFoundError for non-existent ID."""
        # Arrange: Save one entity
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="obj-1",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )

        repo = DjangoPictureRepository()
        repo.save(entity)

        # Act & Assert
        with pytest.raises(PictureNotFoundError):
            repo.get_by_id(str(uuid.uuid4()))

    def test_search_pictures_filters_and_orders(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_pictures with filtering and ordering."""
        # Arrange: Create image files in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        # Create and save entities with different display orders
        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="MAIN",  # Case-insensitive match
        )
        entity3 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-2",  # Different object_id
            picture_type="main",
        )

        repo = DjangoPictureRepository()

        # Save entities
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)
        repo.save(entity3)

        # Update display_order directly on models for ordering test
        PictureModel.objects.filter(id=saved1.id).update(display_order=2)
        PictureModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="main",
        )

        # Assert: Should return entities ordered by display_order, then created_at
        assert len(results) == 2
        assert results[0].id == saved2.id  # display_order=1 comes first
        assert results[1].id == saved1.id  # display_order=2 comes second

    def test_search_first_picture_returns_first_match(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_first_picture returns the first matching entity."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        # Create entities
        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="gallery",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="gallery",
        )

        repo = DjangoPictureRepository()

        # Save entities
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)

        # Set display_order: first entity should have lower order
        PictureModel.objects.filter(id=saved1.id).update(display_order=0)
        PictureModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        first = repo.search_first_picture(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="gallery",
        )

        # Assert
        assert first is not None
        assert first.id == saved1.id  # Should return the one with display_order=0
