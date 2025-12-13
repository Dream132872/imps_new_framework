"""Chunk upload mapper"""

from media.domain.entities import ChunkUpload as ChunkUploadEntity
from media.infrastructure.models import ChunkUpload as ChunkUploadModel


class ChunkUploadMapper:
    """Chunk upload mapper"""

    @staticmethod
    def entity_to_model(entity: ChunkUploadEntity) -> ChunkUploadModel:
        """Converts chunk upload entity to model instance"""

        return ChunkUploadModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            upload_id=entity.upload_id,
            filename=entity.filename,
            total_size=entity.total_size,
            uploaded_size=entity.uploaded_size,
            chunk_count=entity.chunk_count,
            temp_file_path=entity.temp_file_path,
            status=entity.status,
        )

    @staticmethod
    def model_to_entity(model: ChunkUploadModel) -> ChunkUploadEntity:
        """Converts chunk upload model to entity instance"""

        return ChunkUploadEntity(
            id=str(model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            upload_id=model.upload_id,
            filename=model.filename,
            total_size=model.total_size,
            uploaded_size=model.uploaded_size,
            chunk_count=model.chunk_count,
            temp_file_path=model.temp_file_path,
            status=model.status,
        )
