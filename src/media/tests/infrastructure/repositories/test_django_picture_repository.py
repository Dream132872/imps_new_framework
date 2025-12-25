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

    def test_save_updates_existing_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that save() updates an existing entity when ID is provided."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        # Create and save initial entity
        entity = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
            picture_title="Original Title",
            picture_alternative="Original Alt",
        )

        repo = DjangoPictureRepository()
        saved_entity = repo.save(entity)

        # Act: Update the entity
        updated_entity = picture_entity_factory(
            picture_id=saved_entity.id,
            image=file_field,
            picture_object_id="obj-1",
            picture_type="gallery",  # Changed
            picture_title="Updated Title",  # Changed
            picture_alternative="Updated Alt",  # Changed
        )
        updated_saved = repo.save(updated_entity)

        # Assert
        assert updated_saved.id == saved_entity.id  # Same ID
        assert updated_saved.picture_type == "gallery"
        assert updated_saved.title == "Updated Title"
        assert updated_saved.alternative == "Updated Alt"

    def test_delete_removes_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that delete() removes an entity from the repository."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
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
        saved_entity = repo.save(entity)

        # Act
        repo.delete(saved_entity)

        # Assert: Entity should no longer exist
        assert not repo.exists_by_id(saved_entity.id)
        with pytest.raises(PictureNotFoundError):
            repo.get_by_id(saved_entity.id)

    def test_delete_raises_not_found(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that delete() raises error for non-existent entity."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity = picture_entity_factory(
            picture_id=str(uuid.uuid4()),  # Non-existent ID
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )

        repo = DjangoPictureRepository()

        # Act & Assert
        from shared.domain.exceptions import DomainEntityNotFoundError

        with pytest.raises(DomainEntityNotFoundError):
            repo.delete(entity)

    def test_get_all_returns_all_entities(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that get_all() returns all entities in the repository."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-2",
            picture_type="gallery",
        )
        entity3 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-3",
            picture_type="avatar",
        )

        repo = DjangoPictureRepository()
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)
        saved3 = repo.save(entity3)

        # Act
        all_entities = repo.get_all()

        # Assert
        assert len(all_entities) >= 3
        ids = [e.id for e in all_entities]
        assert saved1.id in ids
        assert saved2.id in ids
        assert saved3.id in ids

    def test_exists_by_id_returns_true_when_exists(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test that exists_by_id() returns True for existing entity."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
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
        saved_entity = repo.save(entity)

        # Act
        exists = repo.exists_by_id(saved_entity.id)

        # Assert
        assert exists is True

    def test_exists_by_id_returns_false_when_not_exists(self) -> None:
        """Test that exists_by_id() returns False for non-existent entity."""
        repo = DjangoPictureRepository()

        # Act
        exists = repo.exists_by_id(str(uuid.uuid4()))

        # Assert
        assert exists is False

    def test_search_pictures_with_empty_string_type(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_pictures with empty string picture_type returns all."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="gallery",
        )

        repo = DjangoPictureRepository()
        repo.save(entity1)
        repo.save(entity2)

        # Act
        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="",  # Empty string
        )

        # Assert: Should return all pictures for this object_id
        assert len(results) == 2

    def test_search_pictures_with_all_none_returns_all(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_pictures with all None parameters returns all entities."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-2",
            picture_type="gallery",
        )

        repo = DjangoPictureRepository()
        repo.save(entity1)
        repo.save(entity2)

        # Act
        results = repo.search_pictures(
            content_type=None,
            object_id=None,
            picture_type="",
        )

        # Assert: Should return all pictures
        assert len(results) >= 2

    def test_search_pictures_returns_empty_list_when_no_matches(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_pictures returns empty list when no matches found."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
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

        # Act: Search for non-existent object_id
        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="non-existent",
            picture_type="main",
        )

        # Assert
        assert len(results) == 0
        assert isinstance(results, list)

    def test_search_pictures_orders_by_created_at_when_display_order_same(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_pictures orders by created_at when display_order is same."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
            picture_type="main",
        )
        file_field = FileFieldFactory.from_image_field(temp_model.image)
        temp_model.delete()

        entity1 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )
        entity2 = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )

        repo = DjangoPictureRepository()
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)

        # Set same display_order
        PictureModel.objects.filter(id=saved1.id).update(display_order=1)
        PictureModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="main",
        )

        # Assert: Should be ordered by created_at (first saved comes first)
        assert len(results) == 2
        assert results[0].id == saved1.id  # First created comes first

    def test_search_first_picture_returns_none_when_no_matches(
        self,
        sample_content_type: ContentType,
    ) -> None:
        """Test search_first_picture returns None when no matches found."""
        repo = DjangoPictureRepository()

        # Act
        result = repo.search_first_picture(
            content_type=sample_content_type.id,
            object_id="non-existent",
            picture_type="main",
        )

        # Assert
        assert result is None

    def test_search_first_picture_with_empty_string_type(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test search_first_picture with empty string picture_type."""
        # Arrange: Create image file in storage
        temp_model = PictureModel.objects.create(
            image=_create_image_file(),
            content_type=sample_content_type,
            object_id="temp",
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
        saved = repo.save(entity)

        # Act
        result = repo.search_first_picture(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="",  # Empty string
        )

        # Assert
        assert result is not None
        assert result.id == saved.id