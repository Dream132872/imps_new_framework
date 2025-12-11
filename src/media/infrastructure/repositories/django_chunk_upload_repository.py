"""
Django repository implementation for chunk upload.
"""

from uuid import UUID

from django.utils.translation import gettext_lazy as _

from media.domain.entities import ChunkUpload
from media.domain.exceptions import ChunkUploadNotFoundError
from media.domain.repositories import ChunkUploadRepository
from media.infrastructure.mappers import ChunkUploadMapper
from media.infrastructure.models import ChunkUpload as ChunkUploadModel
from shared.infrastructure.repositories import DjangoRepository

__all__ = ("DjangoChunkUploadRepository",)


class DjangoChunkUploadRepository(DjangoRepository[ChunkUpload], ChunkUploadRepository):
    """Django implementation of chunk upload repository."""

    def __init__(self) -> None:
        super().__init__(ChunkUploadModel, ChunkUpload)

    def _model_to_entity(self, model: ChunkUploadModel) -> ChunkUpload:
        return ChunkUploadMapper.model_to_entity(model)

    def _entity_to_model(self, entity: ChunkUpload) -> ChunkUploadModel:
        return ChunkUploadMapper.entity_to_model(entity)

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
