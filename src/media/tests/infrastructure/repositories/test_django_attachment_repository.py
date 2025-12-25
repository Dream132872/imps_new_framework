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

