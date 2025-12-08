"""Test chunk upload entity."""

import uuid
from typing import Callable

import pytest

from media.domain.entities.chunk_upload_entities import ChunkUpload as ChunkUploadEntity
from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.domain.exceptions import (
    ChunkUploadInvalidEntityError,
    ChunkUploadValidationError,
)


@pytest.mark.unit
@pytest.mark.domain
class TestChunkUploadEntity:
    """Test chunk upload domain"""

    def test_create_chunk_upload_with_required_fields(self) -> None:
        """Test creating new chunk upload with required fields"""

        # Arrange
        upload_id = str(uuid.uuid4())
        filename = str(uuid.uuid4())

        # Act
        chunk_upload = ChunkUploadEntity(
            upload_id=upload_id,
            filename=filename,
            total_size=2000,
        )

        # Assert
        assert chunk_upload.id is not None, "id should be generated"
        assert chunk_upload.created_at is not None, "created_at should be set"
        assert chunk_upload.updated_at is not None, "updated_at should be set"
        assert (
            chunk_upload.status == ChunkUploadStatus.PENDING.value
        ), "default state of the chunk upload should be 'pending'"

    def test_create_chunk_upload_with_state(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test creating chunk upload with optional values"""

        # Arrange
        upload_id = str(uuid.uuid4())
        filename = str(uuid.uuid4())

        # Act
        chunk_upload = ChunkUploadEntity(
            upload_id=upload_id,
            filename=filename,
            total_size=2000,
            status=ChunkUploadStatus.UPLOADING,
            chunk_count=10,
            temp_file_path="chunks/temporary.rar",
            uploaded_size=1000,
        )

        # Assert
        assert (
            chunk_upload.status == ChunkUploadStatus.UPLOADING.value
        ), "status should be 'uploading'"
        assert chunk_upload.uploaded_size == 1000, "uploaded_size should be 1000"
        assert chunk_upload.chunk_count == 10, "chunk_count should be 10"
        assert (
            chunk_upload.temp_file_path == "chunks/temporary.rar"
        ), "temp_file_path should be 'chunks/temporary.rar'"

    def test_creating_with_invalid_state_value(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test raise error with invalid status value"""

        # Arrange
        invalid_state = "invalid_value"

        # Assert
        with pytest.raises(ChunkUploadValidationError) as e:
            chunk_upload = chunk_upload_entity_factory(status=invalid_state)

    def test_complete_incompleted_chunk(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test mark complete incompleted upload session"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(uploaded_size=1000)

        # Assert
        with pytest.raises(ChunkUploadInvalidEntityError) as e:
            chunk_upload.complete()

    def test_complete_chunk_upload(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test complete upload session"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(uploaded_size=2048)
        original_updated_at = chunk_upload.updated_at

        # Act
        chunk_upload.complete()

        # Assert
        assert (
            chunk_upload.status == ChunkUploadStatus.COMPLETED.value
        ), "status should be 'completed'"

        assert (
            chunk_upload.updated_at > original_updated_at
        ), "updated_at should be greater than original_updated_at"

    def test_chunk_upload_is_complete(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test is complete chunk upload session"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory()
        completed_chunk_upload = chunk_upload_entity_factory(
            total_size=1000,
            uploaded_size=1000,
            status=ChunkUploadStatus.COMPLETED,
        )

        # Assert
        assert not chunk_upload.is_complete(), "should not be completed"
        assert completed_chunk_upload.is_complete(), "should be completed"

    def test_chunk_upload_process_percentage(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test upload percentage processing"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(
            total_size=1000, uploaded_size=500, status=ChunkUploadStatus.UPLOADING
        )

        # Assert
        assert chunk_upload.get_progress_percent() == 50

    def test_update_uploaded_size(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test updating uploaded size of the chunk"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(
            total_size=2000,
            uploaded_size=1000,
            status=ChunkUploadStatus.UPLOADING,
        )
        original_updated_at = chunk_upload.updated_at

        # Act
        chunk_upload.update_uploaded_size(1400)

        # Assert
        assert (
            chunk_upload.updated_at > original_updated_at
        ), "updated_at should be greater than original_updated_at"
        assert chunk_upload.uploaded_size == 1400

    def test_increment_chunk_count(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test incrementing chunk count"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(
            total_size=2000,
            uploaded_size=1000,
            status=ChunkUploadStatus.UPLOADING,
            chunk_count=2,
        )
        original_updated_at = chunk_upload.updated_at
        original_chunk_count = chunk_upload.chunk_count

        # Act
        chunk_upload.increment_chunk_count()

        # Assert
        assert (
            chunk_upload.updated_at > original_updated_at
        ), "updated_at should be greater than original_updated_at"
        assert (
            chunk_upload.chunk_count == original_chunk_count + 1
        ), "new chunk_count should be original_chunk_count + 1"

    def test_change_chunk_upload_status(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test changing chunk upload status"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(
            total_size=2000,
            uploaded_size=1000,
            status=ChunkUploadStatus.UPLOADING,
        )
        original_updated_at = chunk_upload.updated_at

        # Act
        chunk_upload.set_status(ChunkUploadStatus.COMPLETED)

        # Assert
        assert (
            chunk_upload.updated_at > original_updated_at
        ), "new updated_at should be greater than original_updated_at"
        assert chunk_upload.status == "completed", "new status should be 'completed'"

    def test_set_temp_file_path(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test setting the temporary file path of the chunk file"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory()
        original_updated_at = chunk_upload.updated_at
        temp_path = "chunks/temp_1.tmp"

        # Act
        chunk_upload.set_temp_file_path(temp_path)

        # Assert
        assert (
            chunk_upload.updated_at > original_updated_at
        ), "updated_at should be greater than original_updated_at"
        assert (
            chunk_upload.temp_file_path == temp_path
        ), f"temp_file_path should be equal to '{temp_path}'"

    def test_string_representation_of_chunk(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test string representation of the chunk upload"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory()
        str_chunk = str(chunk_upload)

        # Assert
        assert (
            str_chunk
            == f"ChunkUpload {chunk_upload.upload_id} - {chunk_upload.filename}"
        ), "generated string representation should be like this"

    def test_repr_representation_of_chunk(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test repr representation of the chunk upload"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory()
        repr_of_chunk = repr(chunk_upload)

        # Assert
        assert "<ChunkUpload" in repr_of_chunk, "repr should begin with '<ChunkUpload'"
        assert (
            f"id={chunk_upload.id}" in repr_of_chunk
        ), "id should be in the repr value"
        assert (
            f"upload_id={chunk_upload.upload_id}" in repr_of_chunk
        ), "upload_id should be in the repr value"
        assert (
            f"filename={chunk_upload.filename}" in repr_of_chunk
        ), "filename should be in the repr value"

    def test_converting_to_dict(
        self, chunk_upload_entity_factory: Callable[..., ChunkUploadEntity]
    ) -> None:
        """Test converting to dictionary"""

        # Arrange
        chunk_upload = chunk_upload_entity_factory(
            total_size=2000,
            uploaded_size=1000,
            status=ChunkUploadStatus.UPLOADING,
            filename="file_name.rar",
            temp_file_path="chunks/temp_uploading/file_name.rar",
            chunk_count=4,
        )

        # Act
        dict_value = chunk_upload.to_dict()

        # Assert
        assert "upload_id" in dict_value, "upload_id should be in dict_value"
        assert "filename" in dict_value, "filename should be in dict_value"
        assert "total_size" in dict_value, "total_size should be in dict_value"
        assert "uploaded_size" in dict_value, "uploaded_size should be in dict_value"
        assert "chunk_count" in dict_value, "chunk_count should be in dict_value"
        assert "temp_file_path" in dict_value, "temp_file_path should be in dict_value"
        assert "status" in dict_value, "status should be in dict_value"
        assert "progress" in dict_value, "progress should be in dict_value"
        assert "completed" in dict_value, "completed should be in dict_value"
