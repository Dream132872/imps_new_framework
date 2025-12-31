from typing import Callable
import uuid

import pytest

from media.domain.entities.chunk_upload_entities import ChunkUploadStatus, ChunkUpload
from media.domain.exceptions import ChunkUploadNotFoundError
from media.infrastructure.repositories import DjangoChunkUploadRepository
from shared.domain.exceptions import DomainEntityNotFoundError

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


class TestDjangoChunkUploadRepository:
    def test_get_by_upload_id_supports_uuid_and_string(
        self, chunk_upload_entity_factory: Callable[..., ChunkUpload]
    ) -> None:
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()
        entity = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )

        saved = repo.save(entity)

        fetched_by_uuid = repo.get_by_upload_id(upload_id)
        fetched_by_string = repo.get_by_upload_id(str(upload_id))

        assert fetched_by_uuid.id == saved.id
        assert fetched_by_uuid.upload_id == str(upload_id)
        assert fetched_by_uuid.status == ChunkUploadStatus.UPLOADING.value

        assert fetched_by_string.id == saved.id
        assert fetched_by_string.upload_id == str(upload_id)

    def test_get_by_upload_id_raises_not_found(self) -> None:
        repo = DjangoChunkUploadRepository()

        with pytest.raises(ChunkUploadNotFoundError):
            repo.get_by_upload_id(uuid.uuid4())

    def test_get_by_id_returns_domain_entity(
        self, chunk_upload_entity_factory: Callable[..., ChunkUpload]
    ) -> None:
        """Test retrieving chunk upload entity by ID after saving through repository."""
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()
        entity = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )

        # Act: Save entity through repository
        saved_entity = repo.save(entity)

        # Retrieve entity
        retrieved_entity = repo.get_by_id(saved_entity.id)

        # Assert
        assert retrieved_entity.id == saved_entity.id
        assert retrieved_entity.upload_id == str(upload_id)
        assert retrieved_entity.total_size == 5000
        assert retrieved_entity.uploaded_size == 2500
        assert retrieved_entity.chunk_count == 3
        assert retrieved_entity.status == ChunkUploadStatus.UPLOADING.value

    def test_get_by_id_raises_not_found(self) -> None:
        """Test that get_by_id raises DomainEntityNotFoundError for non-existent ID."""
        repo = DjangoChunkUploadRepository()

        # Act & Assert
        with pytest.raises(DomainEntityNotFoundError):
            repo.get_by_id(str(uuid.uuid4()))

    def test_save_updates_existing_entity(
        self, chunk_upload_entity_factory: Callable[..., ChunkUpload]
    ) -> None:
        """Test that save() updates an existing entity when ID is provided."""
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()

        # Create and save initial entity
        entity = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )
        saved_entity = repo.save(entity)

        # Act: Update the entity
        updated_entity = chunk_upload_entity_factory(
            id=saved_entity.id,
            upload_id=upload_id,
            total_size=10000,  # Changed
            uploaded_size=7500,  # Changed
            chunk_count=5,  # Changed
            status=ChunkUploadStatus.COMPLETED,  # Changed
        )
        updated_saved = repo.save(updated_entity)

        # Assert
        assert updated_saved.id == saved_entity.id  # Same ID
        assert updated_saved.total_size == 10000
        assert updated_saved.uploaded_size == 7500
        assert updated_saved.chunk_count == 5
        assert updated_saved.status == ChunkUploadStatus.COMPLETED.value

    def test_delete_removes_entity(
        self, chunk_upload_entity_factory: Callable[..., ChunkUpload]
    ) -> None:
        """Test that delete() removes an entity from the repository."""
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()
        entity = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )

        saved_entity = repo.save(entity)

        # Act
        repo.delete(saved_entity)

        # Assert: Entity should no longer exist
        assert not repo.exists_by_id(saved_entity.id)
        with pytest.raises(DomainEntityNotFoundError):
            repo.get_by_id(saved_entity.id)

    def test_delete_raises_not_found(
        self, chunk_upload_entity_factory: Callable[..., ChunkUpload]
    ) -> None:
        """Test that delete() raises error for non-existent entity."""
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()
        entity = chunk_upload_entity_factory(
            id=str(uuid.uuid4()),  # Non-existent ID
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )

        # Act & Assert
        with pytest.raises(DomainEntityNotFoundError):
            repo.delete(entity)
