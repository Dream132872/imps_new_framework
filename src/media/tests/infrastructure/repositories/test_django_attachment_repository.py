import uuid
from typing import Callable

import pytest

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentNotFoundError
from media.infrastructure.models import Attachment as AttachmentModel
from media.infrastructure.repositories import DjangoAttachmentRepository
from shared.domain.entities import FileField, FileFieldType
from shared.domain.factories import FileFieldFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


class TestDjangoAttachmentRepository:
    """Test suite for DjangoAttachmentRepository using DDD approach."""

    def test_get_by_id_returns_domain_entity(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test retrieving attachment entity by ID after saving through repository."""
        # Arrange: Create file in storage and get FileField
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp-obj",
            attachment_type="temp",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()  # Clean up temp model

        # Create entity using factory
        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            title="Doc",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()

        # Act: Save entity through repository
        saved_entity = repo.save(entity)

        # Retrieve entity
        retrieved_entity = repo.get_by_id(saved_entity.id)

        # Assert
        assert retrieved_entity.id == saved_entity.id
        assert retrieved_entity.content_type_id == sample_content_type.id
        assert retrieved_entity.object_id == "obj-1"
        assert retrieved_entity.attachment_type == "document"
        assert retrieved_entity.title == "Doc"
        assert retrieved_entity.file.file_type == FileFieldType.FILE
        assert retrieved_entity.file.name.startswith("attachments/")

    def test_get_by_id_raises_not_found(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that get_by_id raises AttachmentNotFoundError for non-existent ID."""
        # Arrange: Save one entity
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="obj-1",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        repo.save(entity)

        # Act & Assert
        with pytest.raises(AttachmentNotFoundError):
            repo.get_by_id(str(uuid.uuid4()))

    def test_search_attachments_filters_and_orders(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_attachments with filtering and ordering."""
        # Arrange: Create files in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="temp",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        # Create and save entities with different display orders
        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="DOCUMENT",  # Case-insensitive match
            content_type_id=sample_content_type.id,
        )
        entity3 = attachment_entity_factory(
            file=file_field,
            object_id="obj-2",  # Different object_id
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()

        # Save entities and update display_order through models
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)
        repo.save(entity3)

        # Update display_order directly on models for ordering test
        AttachmentModel.objects.filter(id=saved1.id).update(display_order=2)
        AttachmentModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="document",
        )

        # Assert: Should return entities ordered by display_order, then created_at
        assert len(results) == 2
        assert results[0].id == saved2.id  # display_order=1 comes first
        assert results[1].id == saved1.id  # display_order=2 comes second

    def test_search_first_attachment_returns_first_match(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_first_attachment returns the first matching entity."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="temp",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        # Create entities
        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()

        # Save entities
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)

        # Set display_order: first entity should have lower order
        AttachmentModel.objects.filter(id=saved1.id).update(display_order=0)
        AttachmentModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        first = repo.search_first_attachment(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="document",
        )

        # Assert
        assert first is not None
        assert first.id == saved1.id  # Should return the one with display_order=0

    def test_save_updates_existing_entity(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that save() updates an existing entity when ID is provided."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        # Create and save initial entity
        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            title="Original Title",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        saved_entity = repo.save(entity)

        # Act: Update the entity
        updated_entity = attachment_entity_factory(
            attachment_id=saved_entity.id,
            file=file_field,
            object_id="obj-1",
            attachment_type="image",  # Changed
            title="Updated Title",  # Changed
            content_type_id=sample_content_type.id,
        )
        updated_saved = repo.save(updated_entity)

        # Assert
        assert updated_saved.id == saved_entity.id  # Same ID
        assert updated_saved.attachment_type == "image"
        assert updated_saved.title == "Updated Title"

    def test_delete_removes_entity(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that delete() removes an entity from the repository."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        saved_entity = repo.save(entity)

        # Act
        repo.delete(saved_entity)

        # Assert: Entity should no longer exist
        assert not repo.exists_by_id(saved_entity.id)
        with pytest.raises(AttachmentNotFoundError):
            repo.get_by_id(saved_entity.id)

    def test_delete_raises_not_found(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that delete() raises error for non-existent entity."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            attachment_id=str(uuid.uuid4()),  # Non-existent ID
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()

        # Act & Assert
        from shared.domain.exceptions import DomainEntityNotFoundError

        with pytest.raises(DomainEntityNotFoundError):
            repo.delete(entity)

    def test_get_all_returns_all_entities(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that get_all() returns all entities in the repository."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-2",
            attachment_type="image",
            content_type_id=sample_content_type.id,
        )
        entity3 = attachment_entity_factory(
            file=file_field,
            object_id="obj-3",
            attachment_type="video",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
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
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test that exists_by_id() returns True for existing entity."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        saved_entity = repo.save(entity)

        # Act
        exists = repo.exists_by_id(saved_entity.id)

        # Assert
        assert exists is True

    def test_exists_by_id_returns_false_when_not_exists(self) -> None:
        """Test that exists_by_id() returns False for non-existent entity."""
        repo = DjangoAttachmentRepository()

        # Act
        exists = repo.exists_by_id(str(uuid.uuid4()))

        # Assert
        assert exists is False

    def test_search_attachments_with_empty_string_type(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_attachments with empty string attachment_type returns all."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="image",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        repo.save(entity1)
        repo.save(entity2)

        # Act
        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="",  # Empty string
        )

        # Assert: Should return all attachments for this object_id
        assert len(results) == 2

    def test_search_attachments_with_all_none_returns_all(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_attachments with all None parameters returns all entities."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-2",
            attachment_type="image",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        repo.save(entity1)
        repo.save(entity2)

        # Act
        results = repo.search_attachments(
            content_type=None,
            object_id=None,
            attachment_type="",
        )

        # Assert: Should return all attachments
        assert len(results) >= 2

    def test_search_attachments_returns_empty_list_when_no_matches(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_attachments returns empty list when no matches found."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        repo.save(entity)

        # Act: Search for non-existent object_id
        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="non-existent",
            attachment_type="document",
        )

        # Assert
        assert len(results) == 0
        assert isinstance(results, list)

    def test_search_attachments_orders_by_created_at_when_display_order_same(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_attachments orders by created_at when display_order is same."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity1 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )
        entity2 = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        saved1 = repo.save(entity1)
        saved2 = repo.save(entity2)

        # Set same display_order
        AttachmentModel.objects.filter(id=saved1.id).update(display_order=1)
        AttachmentModel.objects.filter(id=saved2.id).update(display_order=1)

        # Act
        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="document",
        )

        # Assert: Should be ordered by created_at (first saved comes first)
        assert len(results) == 2
        assert results[0].id == saved1.id  # First created comes first

    def test_search_first_attachment_returns_none_when_no_matches(
        self,
        sample_content_type,
    ) -> None:
        """Test search_first_attachment returns None when no matches found."""
        repo = DjangoAttachmentRepository()

        # Act
        result = repo.search_first_attachment(
            content_type=sample_content_type.id,
            object_id="non-existent",
            attachment_type="document",
        )

        # Assert
        assert result is None

    def test_search_first_attachment_with_empty_string_type(
        self,
        sample_attachment_file,
        sample_content_type,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        """Test search_first_attachment with empty string attachment_type."""
        # Arrange: Create file in storage
        temp_model = AttachmentModel.objects.create(
            file=sample_attachment_file,
            content_type=sample_content_type,
            object_id="temp",
            attachment_type="document",
        )
        file_field = FileFieldFactory.from_file_field(temp_model.file)
        temp_model.delete()

        entity = attachment_entity_factory(
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        repo = DjangoAttachmentRepository()
        saved = repo.save(entity)

        # Act
        result = repo.search_first_attachment(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="",  # Empty string
        )

        # Assert
        assert result is not None
        assert result.id == saved.id

