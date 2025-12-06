"""
Django repository implementation for chunk upload.
"""

from uuid import UUID

from django.utils.translation import gettext_lazy as _

from media.domain.entities import ChunkUpload
from media.domain.exceptions import ChunkUploadNotFoundError
from media.domain.repositories import ChunkUploadRepository
from media.infrastructure.models import ChunkUpload as ChunkUploadModel
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoChunkUploadRepository",)


class DjangoChunkUploadRepository(DjangoRepository[ChunkUpload], ChunkUploadRepository):
    """Django implementation of chunk upload repository."""

    def __init__(self) -> None:
        super().__init__(ChunkUploadModel, ChunkUpload)

    def _model_to_entity(self, model: ChunkUploadModel) -> ChunkUpload:
        return ChunkUpload(
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

    def _entity_to_model(self, entity: ChunkUpload) -> ChunkUploadModel:
        model, created = ChunkUploadModel.objects.get_or_create(
            id=entity.id,
            defaults={
                "upload_id": entity.upload_id,
                "filename": entity.filename,
                "total_size": entity.total_size,
                "uploaded_size": entity.uploaded_size,
                "chunk_count": entity.chunk_count,
                "temp_file_path": entity.temp_file_path,
                "status": entity.status,
            },
        )

        if not created:
            model.upload_id = entity.upload_id
            model.filename = entity.filename
            model.total_size = entity.total_size
            model.uploaded_size = entity.uploaded_size
            model.chunk_count = entity.chunk_count
            model.temp_file_path = entity.temp_file_path
            model.status = entity.status

        return model

    def get_by_id(self, id: str) -> ChunkUpload:
        return super().get_by_id(id)

    def get_by_upload_id(self, upload_id: str | UUID) -> ChunkUpload:
        upload_id_str = str(upload_id) if isinstance(upload_id, UUID) else upload_id
        try:
            model_instance = self.model_class.objects.get(upload_id=upload_id_str)
            return self._model_to_entity(model_instance)
        except self.model_class.DoesNotExist:
            raise ChunkUploadNotFoundError(
                _("Chunk upload not found for upload id: {upload_id}").format(
                    upload_id=upload_id
                )
            )
