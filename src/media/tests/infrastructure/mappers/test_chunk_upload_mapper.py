"""Test chunk upload mapper"""

import uuid
from datetime import datetime
from typing import Callable

import pytest

from media.domain.entities.chunk_upload_entities import (
    ChunkUpload as ChunkUploadEntity,
)
from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.infrastructure.mappers import ChunkUploadMapper
from media.infrastructure.models import ChunkUpload as ChunkUploadModel


@pytest.mark.infrastructure
@pytest.mark.unit
class TestChunkUploadMapper:
    """Test ChunkUploadMapper"""

    def test_entity_to_model_with_valid_chunk_upload_entity(
        self,
        sample_chunk_upload_entity: ChunkUploadEntity,
    ) -> None:
        """Test converting chunk upload entity to model"""

        # Act
        result = ChunkUploadMapper.entity_to_model(sample_chunk_upload_entity)

        # Assert
        assert isinstance(result, ChunkUploadModel)
        assert result.id == sample_chunk_upload_entity.id
        assert result.created_at == sample_chunk_upload_entity.created_at
        assert result.updated_at == sample_chunk_upload_entity.updated_at
        assert result.upload_id == sample_chunk_upload_entity.upload_id
        assert result.filename == sample_chunk_upload_entity.filename
        assert result.total_size == sample_chunk_upload_entity.total_size
        assert result.uploaded_size == sample_chunk_upload_entity.uploaded_size
        assert result.chunk_count == sample_chunk_upload_entity.chunk_count
        assert result.temp_file_path == sample_chunk_upload_entity.temp_file_path
        assert result.status == sample_chunk_upload_entity.status

    def test_entity_to_model_with_different_statuses(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test converting entity to model with different statuses"""

        # Arrange
        pending_entity = chunk_upload_entity_factory(status=ChunkUploadStatus.PENDING)
        uploading_entity = chunk_upload_entity_factory(
            status=ChunkUploadStatus.UPLOADING
        )
        completed_entity = chunk_upload_entity_factory(
            status=ChunkUploadStatus.COMPLETED
        )
        failed_entity = chunk_upload_entity_factory(status=ChunkUploadStatus.FAILED)
        cancelled_entity = chunk_upload_entity_factory(
            status=ChunkUploadStatus.CANCELLED
        )

        # Act
        pending_model = ChunkUploadMapper.entity_to_model(pending_entity)
        uploading_model = ChunkUploadMapper.entity_to_model(uploading_entity)
        completed_model = ChunkUploadMapper.entity_to_model(completed_entity)
        failed_model = ChunkUploadMapper.entity_to_model(failed_entity)
        cancelled_model = ChunkUploadMapper.entity_to_model(cancelled_entity)

        # Assert
        assert pending_model.status == "pending"
        assert uploading_model.status == "uploading"
        assert completed_model.status == "completed"
        assert failed_model.status == "failed"
        assert cancelled_model.status == "cancelled"

    def test_entity_to_model_preserves_all_fields(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test that entity_to_model preserves all entity fields"""

        # Arrange
        chunk_id = str(uuid.uuid4())
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        upload_id = str(uuid.uuid4())
        filename = "test_file.rar"
        total_size = 10240
        uploaded_size = 5120
        chunk_count = 5
        temp_file_path = "/tmp/chunks/test_file.rar"
        status = ChunkUploadStatus.UPLOADING

        entity = chunk_upload_entity_factory(
            id=chunk_id,
            upload_id=upload_id,
            filename=filename,
            total_size=total_size,
            uploaded_size=uploaded_size,
            chunk_count=chunk_count,
            temp_file_path=temp_file_path,
            status=status,
        )
        entity._created_at = created_at
        entity._updated_at = updated_at

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert model.id == chunk_id
        assert model.created_at == created_at
        assert model.updated_at == updated_at
        assert str(model.upload_id) == upload_id
        assert model.filename == filename
        assert model.total_size == total_size
        assert model.uploaded_size == uploaded_size
        assert model.chunk_count == chunk_count
        assert model.temp_file_path == temp_file_path
        assert model.status == status.value

    def test_model_to_entity_with_valid_chunk_upload_model(
        self,
        db: None,
    ) -> None:
        """Test converting chunk upload model to entity"""

        # Arrange
        model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="test_file.rar",
            total_size=2048,
            uploaded_size=1024,
            chunk_count=2,
            temp_file_path="/tmp/chunks/test_file.rar",
            status="uploading",
        )
        model.save()

        # Act
        result = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert isinstance(result, ChunkUploadEntity)
        assert result.id == str(model.id)
        assert result.created_at == model.created_at
        assert result.updated_at == model.updated_at
        assert result.upload_id == str(model.upload_id)
        assert result.filename == model.filename
        assert result.total_size == model.total_size
        assert result.uploaded_size == model.uploaded_size
        assert result.chunk_count == model.chunk_count
        assert result.temp_file_path == model.temp_file_path
        assert result.status == model.status

    def test_model_to_entity_with_different_statuses(
        self,
        db: None,
    ) -> None:
        """Test converting model to entity with different statuses"""

        # Arrange
        pending_model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="pending.rar",
            total_size=1024,
            status="pending",
        )
        pending_model.save()

        completed_model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="completed.rar",
            total_size=1024,
            status="completed",
        )
        completed_model.save()

        # Act
        pending_entity = ChunkUploadMapper.model_to_entity(pending_model)
        completed_entity = ChunkUploadMapper.model_to_entity(completed_model)

        # Assert
        assert pending_entity.status == "pending"
        assert completed_entity.status == "completed"

    def test_model_to_entity_preserves_all_fields(
        self,
        db: None,
    ) -> None:
        """Test that model_to_entity preserves all model fields"""

        # Arrange
        upload_id = uuid.uuid4()
        filename = "custom_file.zip"
        total_size = 5120
        uploaded_size = 2560
        chunk_count = 3
        temp_file_path = "/tmp/chunks/custom_file.zip"
        status = "completed"

        model = ChunkUploadModel(
            upload_id=upload_id,
            filename=filename,
            total_size=total_size,
            uploaded_size=uploaded_size,
            chunk_count=chunk_count,
            temp_file_path=temp_file_path,
            status=status,
        )
        model.save()

        # Act
        entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert entity.id == str(model.id)
        assert entity.created_at == model.created_at
        assert entity.updated_at == model.updated_at
        assert entity.upload_id == str(upload_id)
        assert entity.filename == filename
        assert entity.total_size == total_size
        assert entity.uploaded_size == uploaded_size
        assert entity.chunk_count == chunk_count
        assert entity.temp_file_path == temp_file_path
        assert entity.status == status

    def test_round_trip_conversion(
        self,
        sample_chunk_upload_entity: ChunkUploadEntity,
        db: None,
    ) -> None:
        """Test round-trip conversion: entity -> model -> entity"""

        # Arrange
        original_entity = sample_chunk_upload_entity

        # Act
        model = ChunkUploadMapper.entity_to_model(original_entity)
        model.save()
        converted_entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert converted_entity.id == original_entity.id
        assert converted_entity.upload_id == original_entity.upload_id
        assert converted_entity.filename == original_entity.filename
        assert converted_entity.total_size == original_entity.total_size
        assert converted_entity.uploaded_size == original_entity.uploaded_size
        assert converted_entity.chunk_count == original_entity.chunk_count
        assert converted_entity.temp_file_path == original_entity.temp_file_path
        assert converted_entity.status == original_entity.status
        # Note: created_at and updated_at might differ slightly due to save operation

    def test_entity_to_model_with_none_values(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test entity_to_model handles None values correctly"""

        # Arrange
        entity = chunk_upload_entity_factory(
            temp_file_path=None,
        )

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert model.temp_file_path is None

    def test_model_to_entity_with_none_values(
        self,
        db: None,
    ) -> None:
        """Test model_to_entity handles None values correctly"""

        # Arrange
        model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="test.rar",
            total_size=1024,
            temp_file_path=None,
        )
        model.save()

        # Act
        entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert entity.temp_file_path is None

    def test_entity_to_model_with_zero_values(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test entity_to_model handles zero values correctly"""

        # Arrange
        entity = chunk_upload_entity_factory(
            uploaded_size=0,
            chunk_count=0,
        )

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert model.uploaded_size == 0
        assert model.chunk_count == 0

    def test_model_to_entity_with_zero_values(
        self,
        db: None,
    ) -> None:
        """Test model_to_entity handles zero values correctly"""

        # Arrange
        model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="test.rar",
            total_size=1024,
            uploaded_size=0,
            chunk_count=0,
        )
        model.save()

        # Act
        entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert entity.uploaded_size == 0
        assert entity.chunk_count == 0

    def test_entity_to_model_with_large_values(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test entity_to_model handles large values correctly"""

        # Arrange
        large_total_size = 10**15  # 1 petabyte
        large_uploaded_size = 5 * 10**14  # 500 terabytes
        large_chunk_count = 1000000

        entity = chunk_upload_entity_factory(
            total_size=large_total_size,
            uploaded_size=large_uploaded_size,
            chunk_count=large_chunk_count,
        )

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert model.total_size == large_total_size
        assert model.uploaded_size == large_uploaded_size
        assert model.chunk_count == large_chunk_count

    def test_model_to_entity_with_large_values(
        self,
        db: None,
    ) -> None:
        """Test model_to_entity handles large values correctly"""

        # Arrange
        large_total_size = 10**15  # 1 petabyte
        large_uploaded_size = 5 * 10**14  # 500 terabytes
        large_chunk_count = 1000000

        model = ChunkUploadModel(
            upload_id=uuid.uuid4(),
            filename="large_file.rar",
            total_size=large_total_size,
            uploaded_size=large_uploaded_size,
            chunk_count=large_chunk_count,
        )
        model.save()

        # Act
        entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert entity.total_size == large_total_size
        assert entity.uploaded_size == large_uploaded_size
        assert entity.chunk_count == large_chunk_count

    def test_entity_to_model_upload_id_conversion(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test that entity_to_model correctly handles upload_id as UUID string"""

        # Arrange
        upload_id_str = str(uuid.uuid4())
        entity = chunk_upload_entity_factory(upload_id=upload_id_str)

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert str(model.upload_id) == upload_id_str

    def test_model_to_entity_upload_id_conversion(
        self,
        db: None,
    ) -> None:
        """Test that model_to_entity correctly converts UUID to string"""

        # Arrange
        upload_id_uuid = uuid.uuid4()
        model = ChunkUploadModel(
            upload_id=upload_id_uuid,
            filename="test.rar",
            total_size=1024,
        )
        model.save()

        # Act
        entity = ChunkUploadMapper.model_to_entity(model)

        # Assert
        assert entity.upload_id == str(upload_id_uuid)

    def test_entity_to_model_with_string_status(
        self,
        chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
    ) -> None:
        """Test entity_to_model handles string status values"""

        # Arrange
        entity = chunk_upload_entity_factory(status="pending")

        # Act
        model = ChunkUploadMapper.entity_to_model(entity)

        # Assert
        assert model.status == "pending"

